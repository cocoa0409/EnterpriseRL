# worklog — bed_hold_and_leave_reservations
## Step 0 (difficulty pre-check)
- draw: task0 prereq=2 factors[6,4,5]; task1 prereq=1 factors[5,6]
- XF_recipe.md read in full (32 points); applied per policy below.
## Step 0 decisions (difficulty level)
- Blueprint defect routed around: every user-owned bedhold write (hold/decline/extension/release election) carries no
  numeric field, yet every problem needs a numeric 4-6 factor computation. Payment amounts reduce to an open balance
  (no honest factors). Route: the customer's own numeric write is the representative's written approval of the
  bed-hold charge for one booked entry of privately held days (a confirmation; the approved charge is what posts).
  Charges split by billing subtype (skill: "split into different tools by billing subtype"):
  skilled-stay / private holds (all held days private) vs Medicaid reserved-bed extensions (days after MA days).
- Bed-hold daily rate source: private pay schedule (2026-07-01 schedule) restated as the charge policies' params;
  isolation-placement rule read from the private agreement (cross private).
- Task 0 (Medicare skilled-stay hospital hold, frozen 2026-10-21): R1 pre-notice reduction of the September charge
  (agent), R2 October held-day booking (agent), R3 October charge approval (user, root).
- Task 1 (Medicaid hospital leave with private extension): S1 October extension-day booking (agent), S2 extension
  charge approval (user, root).
- REVISED (supersedes the task split above): factor richness check showed payer-day counts and pre-notice credits
  carry <=2 honest variations; private-day bookings (company hold terms: election window, private hold maximum,
  renewal, return/release) and charges (company bed-hold charge schedule) carry 5-6. Final trees:
  Task 0 (Medicaid resident, hospital leave Sept->Oct, late private extension, return in Oct):
    T0a reverse the October payer-reserved entry's days booked past the reserved-bed allowance (agent, 4)
    T0b book the October privately held extension days (agent, 5)    [waits on T0a, value_input]
    T0c representative approves the October extension charge (user, 6, root) [waits on T0b, value_input]
  Task 1 (Medicare skilled-stay resident, private hospital hold): T1a book held days (agent,5) -> T1b approve the
    hold charge (user,6, root). Charge tools split by billing subtype (MA reserved-bed extension vs skilled hold).
## RESUME (successor agent, round 1) — breakpoint: extended_policies [], no tools, no tasks
- Re-read plan/worklog, XF_recipe (32 points), base bedhold charter, schema, share tools, references.
- Realism re-check of the customer's own numeric write (coordinator ask): bedhold user acts in the blueprint are
  elections (hold/decline/private_extension/release: enum+date only) and payments (amount = open balance, no honest
  factors). The one family act carrying a computed figure is the representative's signature on the private bed-hold
  charge agreement for the privately held days of one booked entry (real SNF practice: the responsible party signs
  the private-pay bed-hold agreement stating the days and the charge it accepts). Kept, framed as "signs the private
  bed-hold charge agreement", not "approves a posted charge". Design re-check of factor honesty continues below.
## Step 0 re-check (successor) — the REVISED split is replaced (reason below)
- Finding: a payer-reserved day count (the T0a reversal of the REVISED split) is fully fixed by the real MA reserve
  rule; in an extension world only two levers move it (the reserve limit and the reserve already used), so a
  4-factor payer-day computation would need invented ladders on a Pennsylvania MA rule (forbidden by the realism line).
- What the real rules DO support (checked with bite arithmetic): a later-month private-day booking in a long hold
  carries four honest, independently biting factors — the MA reserve that dates the first private day (cross medicaid),
  the private hold maximum per written election/renewal (base private_hold_max_days, renewals add a period), the
  late-renewal gap (base: a later written election holds only from its day), and the hold end (midnight census
  return / release). Charges carry: accommodation priced (isolation billing tier = private charter; secure memory),
  the 60-day rate-notice rule (private charter / 42 CFR 483.10(g)(18)), days before the transfer notice (base/federal),
  plus operator charge-schedule items (company-set, allowed by the realism line for private bed-hold charges).
- New split (Plan Z):
  T0 (MA hospital leave, long private hold with a late renewal, return in Oct): A Oct extension-day booking (agent, 4)
     -> C Oct extension charge agreement (user, 6, root) [value_input: entry days]; B opening-month (Sept) extension
     charge agreement (user, 5) -> C [state_gate: a hold's months are charged oldest month first].
  T1 (Medicare skilled-stay hospital hold, long hold, released): D Oct held-day booking (agent, 5) -> E Oct hold charge
     agreement (user, 6, root) [value_input].
## RESUME (successor 3, round 1) — Plan Z kept; factor sets fixed (no re-litigation of the tree)
- One-line change (feasibility, not shape): the factor-count multiset [6,4,5] is assigned A=4, B=6, C=5 (Plan Z had
  B=5, C=6): the October world carries no pre-transfer-notice day, so the closing-month charge has five load-bearing
  rules and the opening-month charge six. Tree, owners, edges and kinds unchanged.
- DSL routes: opening-month entry = the resident-private entry whose service month equals the service month of the
  last payer-reserved entry (LATEST by to_date); closing-month entry = the latest resident-private entry by to_date.
  Both selections are order-independent of the sibling write (A writes a booked row, B a charge row).
- Scopes (sibling overwrites of bedhold_evt_charges exclude each other by name): B = opening-month extension entry of
  a Medical Assistance hospital leave; C = closing-month extension entry of a Medical Assistance hospital leave (not
  also the opening entry); E (task 1) = closing-month entry of a skilled-stay hospital hold. A = closing-month
  privately held days of a Medical Assistance or private-pay hospital-leave hold; D (task 1) = skilled-stay hold.
### Task 0 factor sets (world: dep 2026-08-25, MA reserve 15 -> private from 09-09, extension period to 10-08,
###   late renewal eff 10-12, return 10-20; isolation room Private LTC -> Semi-Private LTC rate; rate notice 08-14 -> eff 10-13;
###   transfer notice delivered late 09-10)
- A (agent, 4) closing-month private days = MN(last_held - reserve + 1 - gap, cover_cap) - private booked net:
  A1 reserve [param, cross medicaid, multi-source: MA status x eligibility lag] 15 | 15-lag | 0(base)
  A2 last held day [method] return-1 | release | end_date | posting date(base)
  A3 renewal gap [param] late renewal: days strictly between | no renewal & still held past period: days after period | 0(base)
  A4 cover cap [param] >=2 written private elections: count x max | none: 0 | one: max(base)
  gold 16; each factor alone at baseline: 31 / 18 / 19 / 8; all baseline 8.
- B (user, 6) opening-month charge: pre-notice days [param], isolation rate [param, cross private, multi-source],
  schedule/notice rate [method, cross private], extended-hold percent [param, operator], meal credit [param, operator],
  routine-supply credit [param, operator].
- C (user, 5) closing-month charge: schedule/notice split [method, cross private], isolation rate [param, cross
  private], extended-hold percent, meal credit, supply credit [params, operator]; pre-notice is a non-factor guard.
- Edges: A->C value_input (state form, affirmative "only after"); B->C state_gate (state form, negated "not ... until").
- task0 policies A,B,C written; check_extended structure OK (only tools/tasks pending); task_tools.py 3 tools TASK TOOL CONTRACT OK. Next: seed task 0 via /tmp/bedhold_0074/build0.py
- Task 0 seed built (/tmp/bedhold_0074/build0_seed.py, ids frozen in t0_ids.json); tasks/0.json skeleton by build0_task.py
  (texts from t0_text.json). Handling-time recompute (sens.py, real tool replay): A=16 | B=7793.10 | C=5367.65.
  Factor sensitivity: A ma_reserve 31, last_held 18, late_renewal 19, cover_cap 8, all-baseline 8.
  B unnoticed 8164.20, isolation 8531.25, notice_schedule 8092.35, extended_hold 8225.70, meal 8089.20, program 7923.30, all 10230.00.
  C isolation 5876.80, notice_schedule 5482.40, extended_hold 6372.20, meal 5593.25, program 5466.85, all 7440.00.
  Edge sensitivity: skip A -> C reads the September entry: 7793.10 (value_input bears); skip B -> C unchanged 5367.65, the
  September booked entry stays uncharged (state_gate: terminal ledger lacks the opening-month charge row).
### Task 0 revisions (symptom -> cause -> change -> rerun)
- replay MISMATCH (22 unread rows) -> MA patient-pay ledger and April reservation rows outside the read closure -> ledger read by
  customer_id (covers both reservations); MA patient-pay ledger dropped (case balance 0.00 = empty ledger) -> REPLAY OK 14/14.
- solvability: charge_once gate field bedhold_ledger.days_entry_id had no carrier row -> seeded the real-world 2026-09-09
  payer-day booking error (September payer entry 9 days, 1 reversed billing_error); A nets reversals (near-miss) -> OK.
- C trigger state_due -> on_request: October bed-hold charges bill on the November statement (base: billed the statement day
  of the following month), so at 2026-10-21 the October charge is the representative's own request; September's is owed.
- decoy probes failed (first-match private agreement; LATEST transfer notice) -> agreement read = current one (active, else
  notice_period, else payer_converted) via EXISTS-selected status filter; notice = earliest of the latest delivery to the
  resident and to the representative. Rule sentence added to B and C.
### Decoy / absent-record probe table (scratch copies, sens.py)            result A | B | C
| probe                                              | outcome                          |
| none                                               | 16 | 7793.10 | 5367.65 (gold)   |
| closed MA case listed first (status filter)        | unchanged                        |
| closed private agreement listed first              | unchanged (after fix; was 8661.45/5880.80) |
| second transfer notice to resident 09-12           | unchanged (after fix; was 7050.90) |
| other reservation's private entry 2026-10          | unchanged (HID scoping)          |
| absent transfer notice                             | B 0.00, C 0.00 (no day charged: rule tier) |
| absent MA case                                     | A 31 (reserve 0 tier)            |
| absent renewal election                            | A 8 (one-period cap)             |
### Pairwise method-tier table (shape test, XF#7)
- last_held_day_rule: returned (return_date input, -1) | released (release_date input) | expired (end_date input) |
  in force (posting date) — each pair differs by its anchor input.
- notice_schedule_opening: split (adds notice date + notice-days inputs, MX/MN window) | all prior (no date input) |
  all current (none) — prior vs current differ by the rate input selected; split adds an operation.
- notice_schedule_closing: same three shapes, the split counted back from the entry's last day (adds to_date input).
### Manual gates (task 0)
- Factor independence (XF#1): no factor binding reads another factor's binding (checked by listing names per binding);
  result/assembly bindings read factor outputs only. Assembly sentence generic, order fixed (count -> lost -> ceiling;
  percent -> credits -> days).
- T2 per factor: every factor moves the result alone on this world (sensitivity list above).
- Realism: MA 15-day reserve, midnight census, 60-day rate notice, no charge before the transfer notice are real; meal
  credit, specialty-program credit and extended-hold percent are the operator's published private bed-hold schedule.
- Persona: names only the October signing; no prerequisite hint; last reaction = the October signature confirmation.
- TASK 0 per-task gates all green (extended, task_tools, replay, solvability, compute, grounding, cross_fire). Next: task 1 (D->E).
## Task 1 design (Plan Z: D Oct held-day booking agent 5 -> E Oct hold charge user 6 root, value_input). Draw [5,6]: D=5, E=6.
- Structural finding (recorded, tree unchanged): independent additive day factors exist for start / middle gap / end / cap only;
  a skilled hold has no payer reserve, so D's fifth is the operator's interrupted-stay courtesy offset (cross medicare), and
  the start factor is the late written hold election read on calendar days (declared overwrite of the 24-hour window clause,
  because the DSL cannot add hours). Start-segment factors mask each other across D/E, so E carries no pre-notice factor;
  E's sixth is the operator's housekeeping credit by beds per room (cross private).
- World: Harold Quintero (rep Marisol Quintero, spouse), long-stay private resident since 2025-11-03, room 452 Private Bariatric
  Care Room (isolation placement), Part A skilled stay from 2026-08-29 after the 08-26..08-29 qualifying stay (prior private-pay
  hold 08-26..08-28, 3 days charged 1398.00 and paid); skilled-stay hold: dep 2026-09-22 19:50, notice 09-23 08:10, written hold
  signed 09-27 (late: held from 09-27; stamps effective_date/private_hold_start_date keyed 09-22 = stale), first period to 10-26,
  renewal signed/effective 10-29 (gap 10-27..28), release 10-30; Sept entry 09-27..30 (4) charged 1864.00 by base (paid);
  Part A episode ended hospital_transfer_no_return (24 covered days). Rate notice 2026-08-31 -> binding date 10-30.
  frozen 2026-11-02 11:15:00 EST.
- D gold 25 (span 32 after gap, cap 60, courtesy 3, booked 4); baselines D1 28, D2 30, D3 27, D4 23, D5 28, all 26.
- E gold 8400.80 (24 prior x 335.50 + 1 current x 348.80).
- Policies D (bedhold_ext_skilled_hold_days) and E (bedhold_ext_skilled_hold_charge) written + tools book_skilled_hold_days_804a4481 / sign_skilled_hold_charge_7094169f; shared sentences made policy-specific (rates sentence, A scope); task 0 gates re-run green.
### Task 1 build log (symptom -> cause -> change -> rerun)
- Gold (real tool replay): D=25 | E=8400.80. Factor sensitivity D: written_hold_start 30, skilled_last_held_rule 28,
  skilled_renewal_gap 27, skilled_cover_cap 23, interrupted_stay_courtesy 28, all-baseline 26. E: isolation 10350.20,
  notice_schedule 8720.00, extended_hold 8881.50, meal 8753.30, program 8645.80, housekeeping 8535.80, all-baseline 12050.00.
  Edge sensitivity: skip D -> E prices the September entry: 1447.00.
- probe failed: courtesy read CFIELD(medicare last_covered_date, end_reason filter) took an older episode listed first ->
  switched to XLATEST over medicare_ledger medicare_days_booked to_date (seeded the Part A ledger: 3 day blocks, coinsurance
  868.00 charged and paid; read find_medicare_ledger) -> probe unchanged 25.
- solvability: gold steps moved to 9/11 after the added read; payment rows mapped to bedhold_evt_payments_adjustments.
### Task 1 decoy / absent-record probe table                         result D | E
| none                                         | 25 | 8400.80 (gold) |
| older Part A episode + its ledger row first  | unchanged (after fix; was 28) |
| absent Part A ledger                          | D 28 (no courtesy tier) |
| closed private agreement listed first        | unchanged |
| second transfer notice to resident 09-26     | unchanged (earliest delivery counts) |
| hold election signed the day after notice    | D 30 (start = departure tier) |
| absent renewal election                      | D 23 (one-period cap) |
### Pairwise method-tier table (task 1)
- written_hold_start: signing date (adds created_at + notice inputs) | none held (posting+1 sentinel: count 0) |
  departure (no input) — each pair differs by its anchor input / operation.
- skilled_last_held_rule: same four anchors as task 0's last_held_day_rule (return-1 | release | end_date | posting).
- notice_schedule_skilled: split counted back from the entry's last day | all prior | all current.
### Manual gates (task 1)
- Independence: D factors read only records and shared plain bindings (dep, hold_state, posting_off); the first period is
  anchored on the booked September entry, not on written_hold_start's output. E as task 0's C plus housekeeping.
- Realism notes as in the dossier (operator items declared as overwrites). Persona asks only for the October signature.
## Final suite (no --task): EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK (branches mean 73.5,
## steps mean 12.5, history max 13, branches max 90) | GROUNDING OK | SCOPE OK; CACHE-DIFF info only; traceability after render.
ROUND 1: gates 7/7 green
## REWORK round 2 (audit revision_1)
- Tools (CG-11, CG-12): ordering phrases removed from both booking docstrings; bodies now refuse malformed YYYY-MM / YYYY-MM-DD and negative or fractional day counts, refuse non-positive amounts, and round half up via the _BedholdFormat class static helper (charge and balance).
- CG-13: all three bedhold_evt_charges replaced_by (and the rule restatements) again carry "whatever payer source covers the
  resident's stay otherwise".
- CG-1: rule and compute agree. The notice counts from the earlier of its latest delivery to the resident and its latest
  delivery to the representative, and a re-delivery to the same person replaces the earlier one. Applies to all four read sites
  (B, C, D, E).
- CG-2: the opening entry is now the private entry whose first day is the reservation's first privately held day, so it no
  longer depends on payer-entry reversals. The closing entry (C, E) is the latest-posted private entry, with its days net of
  reversals naming it. D's first period is anchored on the recorded first privately held day. The hold election is singular
  per reservation. CG-7 is closed with it: the opening entry can now hold 31 days.
- CG-6: the notice factors are now later-of pick / never-noticed (no split) / split at the schedule date. The never-noticed and
  split-at-schedule-date tiers apply only to agreements signed before the schedule date (private_rate_schedule: "A rate that
  has not been noticed at all never applies"). Baselines are the split at the schedule date.
- CG-14: D now reads the date the hold election was logged (created_at, "moment the election was logged"). Seed T1: election
  effective_date and reservation private_hold_start_date are both 2026-09-27, so the two-readings SOURCE-TASK is gone.
- CG-4: A declares an overwrite of the per-month booking sentence and is scoped to the Medicaid Hospital Leave tier, so the
  private-pay late-election example is out of scope. D's sibling overwrite excludes A's case by name (XF 17).
- Seeds T0 (XF 29): MA application 2025-12-15, eligible from 2026-01-01, admitted 2026-01-05. SSI-level income 30.00 gives
  patient pay 0.00, so the empty patient-pay ledger is the correct ledger. The private agreement was converted at admission and
  never billed privately; the isolation placement was made at admission, so there is no room change. The April reservation
  now holds room 418.
- Seeds T1 (XF 29): the agreement was signed 2026-06-20 ahead of a direct Part A admission on 2026-08-29, so it was never
  billed privately (no private ledger needed). The isolation placement was made at admission. The August private-pay hold was
  removed: it does not exist under a direct admission.
- Probe sweep (scratch copies). All results follow the rule wording:
  - T0, payer August entry reversed in full: A 9, B unchanged.
  - T0, September entry reversed by 1 day: A 17, B 7422.00.
  - T0, notice re-delivered to the representative on 09-12: B 7050.90 (a re-delivery replaces the earlier one).
  - T0, agreement signed after the schedule date: B 8092.35, C 5482.40.
  - T0, no rate notice: C 5278.40.
  - T1, no rate notice: E 8387.50.
  - T1, duplicate September entry posted earlier: D 21, E 7439.40.
- Gold values are unchanged on both tasks; gate block 7/7 green.
### BLOCKED (not closed) — factor content: drawn counts cannot be met with real levers (two messages sent to coordinator)
- Coordinator ask: strike the courtesy days (CG-8) and the charge credits (meal, program, housekeeping) and the
  extended-hold percent; replace them with real levers without relaxing the drawn counts. Infeasibility proof:
  - Charges: three real pricing levers survive the audit tests: isolation tier, rate-notice binding (method, fixed above) and
    pre-notice days.
  - Bookings: only the written-cover cap is non-decoration. The MA reserve, last held day and late election are recorded on
    the reservation (private_hold_start_date, end_date, election effective_date). The booked payer entries reveal the reserve.
    The audit therefore reads them as stamps (CG-10) or as base restatements (CG-9).
  - T1's skilled booking needs 5 factors. A skilled hold has no payer reserve. Of the honest day dimensions:
    - start (late election or pre-notice) and end (census or expiry) can bite at most once each, because their tiers mask
      each other;
    - the cap is the only other.
    That leaves at most 3 to 4 even counting stamp-readable levers.
  - Late-renewal gaps fail T2 and contradict base expiry (CG-3, CG-5).
  - So courtesy, credits and gap factors remain in place, flagged, pending the coordinator's decision. The options are:
    (1) keep 1–2 operator schedule items per charge, keyed to the held room and applied uniformly;
    (2) change T1's tree so the 5-factor problem is not a day booking;
    (3) accept known reds.
- Still open as a result: CG-3, CG-5 (gap factors and lapsed-renewal worlds), CG-8 (courtesy), CG-9 and CG-10 (straw-man and
  stamp factors in A and D), and the O-2 credit realism.
REWORK round 2: gates 7/7 green
## REWORK round 3 (audit revision_2) — design change (what the tasks test), recorded per Plan Z rule
- Gate-proven (check_compute floors): a day booking cannot carry 4–5 independent real factors. Its outcomes are recorded on
  the reservation (end_date, private_hold_start_date) or stated in force by base. Every problem now prices a booked
  resident-private entry (claimed event bedhold_charge). Owners, edges, kinds and draws are kept:
  - T0: A (agent, posts the opening extension charge, 6) -> C value_input; B (user, signs the therapeutic-leave extension
    charge of an earlier leave, 4) -> C state_gate; C (user root, signs the closing extension charge, 5).
  - T1: D (agent, posts the skilled-stay opening charge, 6) -> E (user root, signs the skilled-stay closing charge, 5)
    value_input.
- Removed: both booking policies and their tools, the courtesy days (CG-8), the late-renewal gaps (CG-3, CG-5), the MA
  reserve and last-held-day factors (CG-9, R2-3), the late-election factor (CG-9, CG-14, R2-3), and isolation pricing (R2-5:
  neither world has a producible infection-control room change while the agreement was active). Worlds have only on-time
  written renewals (no lapse).
- Charge levers. Real: rate-notice binding (method, private_rate_schedule); days before the transfer notice (param,
  bedhold_evt_notice, retired in the two opening scopes by one shared sibling overwrite). Company-set (XF 27, the operator's
  published private bed-hold schedule, the same in every scoped schedule):
  - extended-hold percent by the leave's charged privately held days;
  - meal credit by leave length;
  - specialty-program credit by the room tier;
  - housekeeping credit by beds per room.
  The value_input edges are carried by the extended-hold percent: charges already posted on the leave.
- Round 3 progress: five charge policies were generated by /tmp/bedhold_0074/gen.py and the tools regenerated. The task 0 world was rebuilt (therapeutic leave plus hospital leave). Task 0 per-task gates are green. Gold: A 7736.40, B 3501.00, C 6306.05. Skipping A gives C 7099.35.
### Round 3 per-item closure (audit revision_2)
- CG-3, CG-5: late_renewal_gap and skilled_renewal_gap are deleted with the booking policies. Both worlds carry renewals
  logged before the first private period ended (T0 renewal logged 10-05, effective 10-09; T1 logged 10-06, effective 10-10),
  so no hold runs past an unrenewed maximum.
- CG-4(b) / R2-2: closing_private_days is deleted. No policy books days or counts from a reserve.
- CG-8: interrupted_stay_courtesy is deleted.
- CG-9: ma_reserve_allowance, last_held_day_rule, skilled_last_held_rule and written_hold_start are deleted.
  unnoticed_opening_days is now oe_notice_days / so_notice_days, whose base sentence ("No day held before the transfer notice
  was delivered is ever charged to the resident") is retired in exactly those two scopes by one shared sibling overwrite. The
  out-of-scope remainder is restated verbatim, so the factor's baseline contradicts no in-force clause.
- CG-10 / R2-3: no factor decides a quantity the reservation records. The first privately held day is now only a
  selector of the opening entry, not a factor outcome. end_date is not read.
- R2-1 (selections):
  - Entry days are SUM over booked resident-private rows filtered by from_date (opening) or to_date (closing), net of the
    reversals naming the selected entry.
  - Base grain ("bedhold_day_booked … grain: one row per reservation, service month and day payer") forbids a second booked
    resident-private row for the same month. The audit's reverse-and-rebook probe (a second row for the same month) is
    therefore not a producible state. The rule now states the grain ("A reservation carries one resident-private entry per
    service month, so the … entry is a single entry").
  - Partial reversals net correctly (probe table below).
- R2-4: the booking tools are deleted; no docstring carries before/after/first/last/then/later (grep).
- R2-5: no isolation factor. Both private agreements are converted at admission with isolation_placement false and no room
  change. Every agreement field read (signing date, notice date, tier parameters) is set by private_agreement_open /
  private_rate_notice_delivered.
- CG-1, CG-2 (closed members), CG-6, CG-7, CG-12, CG-13, CG-14 stay closed: same notice wording, method shapes, tool helper
  and shared replaced_by. The isolation member of CG-6 is gone.
- Observations:
  - O-1 / O-2: each scoped schedule is keyed to the agreement's room tier, which is the held room in both worlds.
  - O-7: there is a single shared scope sentence per retired clause.
  - O-8: the prerequisite effects name the charge rows read.
  - O-10: the date validator is gone with the booking tools.
### T1 / T2 table (task-world figure with the factor's baseline alone; T2 = a producible world where it alone moves)
| factor | T1 (gold -> baseline-alone) | T2 world (all other factors at baseline) |
| oe_notice_days | 7736.40 -> 8104.80 | notice delivered on day 2 of any opening entry |
| oe/te/ce/so/sc_rate_binding | A 8035.65, B 3636.00, C 6459.05, D 8143.40, E 11412.00 | agreement signed before a schedule date, notice late, entry dated before the binding date |
| oe/ce/so/sc_extended_hold | A 8169.00, C 7496.00, D 8297.30, E 13117.00 | any entry whose charged-plus-own days reach 15 |
| *_meal_credit | A 8032.50, B 3627.90, C 6573.95, D 8122.50, E 11440.60 | any leave of 4 or more days |
| *_program_credit | A 7866.60, B 3556.80, C 6423.85, D 8040.80, E 11311.60 | agreement on a secure-memory or bariatric tier |
| *_housekeeping_credit | A 7793.10, B 3525.30, C 6357.35, D 7957.20, E 11179.60 | agreement on a one- or two-bed tier |
| so_notice_days | 7854.60 -> 8681.40 | as oe_notice_days |
### Pairwise method-tier table (the only method factor of each schedule: rate binding)
| pair | distinguishing input / operation |
| late-notice vs never-noticed | the late-notice tier splits at a later-of pick (adds the notice date and a max); the never-noticed tier has no split |
| late-notice vs schedule-date split | the late-notice tier adds the notice date and the notice-days run and a max over the schedule date |
| never-noticed vs schedule-date split | the schedule-date split adds the schedule-date window; the never-noticed tier has one rate and no window |
### Decoy / absent-record probe sweep (scratch copies; T0 = A | B | C, T1 = D | E; every result follows the rule wording)
- T0, one-day reversal on the September entry: A 7368.00 (net 21 days).
- T0, one-day reversal on the October entry: C 5978.85.
- T0, notice to the resident 08-26 (earlier recipient): A 8104.80 (earliest of the per-recipient deliveries).
- T0, same-recipient re-delivery 09-12: A 6999.60 (replaces, per the rule).
- T0, unpaid-hold notice: unchanged (other notice type).
- T0, absent transfer notice: A 0.00 and C 0.00 (no day charged); B unchanged (own notice).
- T0, closed agreement listed first: unchanged (current-agreement read).
- T0, absent agreement: A 8222.55, B 3716.10, C 6628.15 (schedule-date split, no credits).
- T0, absent rate notice: C 6216.80 (never-noticed tier).
- T0, charge on the other reservation: unchanged (holding-scoped).
- T0, payment row: unchanged.
- T0, earlier private entry of another month: unchanged.
- T1, one-day reversal on the October entry: E 10650.80.
- T1, notice to the resident 09-11: D 8268.00.
- T1, absent notice: 0.00 / 0.00.
- T1, closed agreement first: unchanged.
- T1, agreement signed 07-15 or on 07-01: D 8143.40, E 11412.00 (schedule-date split).
- T1, notice exactly 60 days before 07-01: same (not "fewer than").
- T1, a charge already naming the closing entry: D 6969.20 (counted as charged days, per the rule).
- Same-month second booked entry: not producible (base grain), not probed.
### Gates (full block, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK
REWORK round 3: gates 7/7 green
## REWORK round 4 (audit revision_3 + coordinator ruling) — BLOCKED, artifacts unchanged
- Ruling applied to the lever inventory. The levers a factor may honestly carry:
  - rate-notice binding (method);
  - dietary credit keyed to the held bed (held room tier x leave length: the only multi-source candidate);
  - long-hold held-day threshold;
  - infection-control room-tier pricing, only where the agreement was active when the move was recorded.
  That is at most 4 per charge.
- Every other listed lever cannot become a factor:
  - In-force base statements, so as factors their baselines contradict base (R3-1 / CG-9 straw man): MA reserved-bed days
    (bedhold_agg_payer_day_limits), the no-charge-before-notice rule (bedhold_evt_notice), midnight census and service-month
    booking (bedhold_evt_day_counting).
  - Day bookings record their outcomes on the reservation (end_date, private_hold_start_date: CG-10).
- Draw (fixed by task index): T0 [6,4,5], T1 [5,6]. Four of the five computations need 5 or 6 factors. No claimed bedhold event
  type (charge, booking, reversal, adjustment, payment) computes a value from more than these levers.
- Value edges: once the long-hold count is held days (ruling) rather than charged days, a charge no longer changes a later
  charge. Both value_input edges (C<-A, E<-D) then lose their load, and only a booking prerequisite can carry a value edge.
- Not done: R3-1, R3-2, R3-3 and the floors. Closing them per the ruling leaves every computation at 2–4 factors and breaks both
  value_input edges, so check_extended and check_compute go red. R3-4 (seed payer holdings) is design-dependent and is deferred
  with the structural decision.
- Options sent to the coordinator: (a) accept 4-factor charges with red count gates; (b) allow one more real lever per charge as
  a factor whose baseline is the base standard; (c) restructure Plan Z or the draw.
## REWORK round 4 (final coordinator decision: (a) refused, (b) levers granted, (c) restructure in part) — delivered
- Restructure under (c): Plan Z owners and edges kept (A agent -value-> C; B user -gate-> C; C user root; D agent -value-> E;
  E user root); draw kept (T0 A=6 B=4 C=5; T1 D=6 E=5). What each problem prices moved to private-pay holds, where the
  agreement is active during the leave, so the granted room levers are producible from the private charter:
  - A post_therapeutic_opening_charge_70c1859c: opening entry of a Private Pay Therapeutic Leave Bed Hold;
  - B sign_hospital_stay_charge_706e62e1: the entry of a Private Pay Hospital Leave Bed Hold with a single resident-private entry;
  - C sign_therapeutic_closing_charge_4fa24c1a: closing entry of a Private Pay Therapeutic Leave Bed Hold;
  - D post_hospital_opening_charge_f00b38a9 / E sign_hospital_closing_charge_2a6f345f: opening / closing entry of a Private Pay Hospital Leave Bed Hold with more
    than one resident-private entry. Policy ids and tools renamed to the new scopes; the one shared scope sentence is
    identical in all five overwrites of bedhold_evt_charges (XF 15/17) and restates the base clause for every other entry.
- Leave months on the private ledger: room and board billed in advance is credited from the departure date with
  discharge_proration ('When the resident leaves ... credited ... discharge_proration'; 'Bed-hold days the resident elected
  while away are charged under the bed-hold reservation') and rebilled from the return day (midnight census).
### Round 4 per-item closure (audit revision_3)
- R3-1 (XF 16 / straw-man notice factor): the bedhold_evt_notice overwrite is removed from every schedule; oe/so_notice_days
  are gone. The notice rule is a non-factor baseline sentence (charged days = days less those held before the notice).
- R3-2 (credits keyed to the agreement tier): all program and housekeeping credits deleted; no credit or discount was added.
  The only per-day credit is the granted dietary credit keyed to the bed held as the reservation records it.
- R3-3 (no multi-source factor): dietary credit (bed held x leave length) in all five schedules; isolation rate (billing
  basis of the room-and-board charge credited from the departure date x private room held) in A, B, D; room-change tier
  (room change request naming the change date x agreement isolation flag x change date) in A, C, D, E.
- R3-4 (XF 29, payer holdings asserted but unseeded): no Medicaid or Medicare status is asserted any more. Each resident's
  private-pay history is seeded from admission: deposit, first-month partial, monthly advance bills, payments, the
  infection-control room change (room_change_proration credit + isolation_rate rebill), every leave's discharge_proration
  credit and return rebill, return-month and next-month bills; account_balance equals the ledger sum. The agreement's tier
  and room-change date are backed by a room change request; isolation of the held room is read from the credited bill.
- Factor floors: T0 6/4/5, T1 6/5; each computation has the rate-binding method factor and >= 2 parameter factors.
- O-9: task 1 agreement now signed 2026-06-19 for admission 2026-06-22. O-6: re-delivery replaces the earlier delivery to
  that person (rule-stated, probed). O-11: opening entries still count 0 days already charged; the tier rests on the entry's
  own days (rule-stated). O-12: the gate now names hospital leaves carrying a single private entry, so B's tool always
  resolves it. O-1 persists by design (XF 32): middle months of a 3+ month hold stay under base; neither world has one.
- Residual risk (flagged for the audit, not hidden): the two room-change factors (days from the change, tier moved to) are the
  coordinator's levers (5) and (6) and are two facets of one recorded change: each passes T1 on its world, but T2 holds only
  jointly (with the other at baseline the moved days are priced like the rest). Moving the held bed during a hold is the
  resident's own request; base bedhold_hold_end ('goes back to the same room') is not overwritten.
### T1 table, task 0 (figure with the factor's baseline alone; heading = gold | all-baseline)
- bedhold_ext_therapeutic_opening_charge [10191.70 | 11336.00]: to_rate_binding 10566.00; to_extended_hold 10747.40; to_dietary_credit 10558.30; to_isolation_rate 10754.10; to_room_change_days 9118.20; to_room_change_tier 9469.70
- bedhold_ext_hospital_stay_charge [6663.30 | 8284.00]: hs_rate_binding 6916.00; hs_extended_hold 7028.10; hs_dietary_credit 6931.20; hs_isolation_rate 7331.15
- bedhold_ext_therapeutic_closing_charge [7859.80 | 8284.00]: tc_rate_binding 8033.20; tc_extended_hold 9294.10; tc_dietary_credit 8127.70; tc_room_change_days 6620.50; tc_room_change_tier 6620.50
### T1 table, task 1 (figure with the factor's baseline alone; heading = gold | all-baseline)
- bedhold_ext_hospital_opening_charge [7715.10 | 8720.00]: ho_rate_binding 7998.20; ho_extended_hold 8136.00; ho_dietary_credit 7997.10; ho_isolation_rate 8101.75; ho_room_change_days 7014.00; ho_room_change_tier 7330.35
- bedhold_ext_hospital_closing_charge [10696.00 | 12208.00]: hc_rate_binding 11076.80; hc_extended_hold 12653.20; hc_dietary_credit 11090.80; hc_room_change_days 9625.00; hc_room_change_tier 9625.00
### T2 (each factor live, every other factor at baseline, on the task world)
- Moves alone on its own task world: every rate_binding, extended_hold, dietary_credit and isolation_rate factor (A, B, C, D, E).
- room_change_days / room_change_tier (A, C, D, E): no move alone; both live together they move (see residual risk above).
### Pairwise method-tier table (rate binding, the method factor of every schedule; XF 7)
- late notice (later-of pick on notice + notice days) vs no notice (constant 0 current days): pick over two dated inputs vs none.
- late notice vs otherwise (split at schedule date): adds the notice date and notice-days inputs and a max pick.
- no notice vs otherwise: 0 on its whole domain vs a date-span count (otherwise is 0 only before the schedule date).
### Decoy / absent-record probe sweep (scratch copies; every result follows the rule wording)
- 0 | therapeutic_opening_charge | closed older agreement (other tier, no notice, change date inside leave) | 10191.7 | 10191.7 | same
- 0 | therapeutic_opening_charge | payer_reserved entry dated later on same reservation | 10191.7 | 10191.7 | same
- 0 | therapeutic_opening_charge | unpaid_hold_notice delivered later | 10191.7 | 10191.7 | same
- 0 | therapeutic_opening_charge | room_change_proration credit from the departure date | 10191.7 | 10191.7 | same
- 0 | therapeutic_opening_charge | later private request of another type | 10191.7 | 10191.7 | same
- 0 | therapeutic_opening_charge | charge on another reservation of the resident | 10191.7 | 10191.7 | same
- 0 | hospital_stay_charge | closed older agreement (other tier, no notice, change date inside leave) | 6663.3 | 6663.3 | same
- 0 | hospital_stay_charge | payer_reserved entry dated later on same reservation | 6663.3 | 6663.3 | same
- 0 | hospital_stay_charge | unpaid_hold_notice delivered later | 6663.3 | 6663.3 | same
- 0 | hospital_stay_charge | room_change_proration credit from the departure date | 6663.3 | 6663.3 | same
- 0 | hospital_stay_charge | later private request of another type | 6663.3 | 6663.3 | same
- 0 | hospital_stay_charge | charge on another reservation of the resident | 6663.3 | 6663.3 | same
- 0 | therapeutic_closing_charge | closed older agreement (other tier, no notice, change date inside leave) | 7859.8 | 7859.8 | same
- 0 | therapeutic_closing_charge | payer_reserved entry dated later on same reservation | 7859.8 | 7859.8 | same
- 0 | therapeutic_closing_charge | unpaid_hold_notice delivered later | 7859.8 | 7859.8 | same
- 0 | therapeutic_closing_charge | room_change_proration credit from the departure date | 7859.8 | 7859.8 | same
- 0 | therapeutic_closing_charge | later private request of another type | 7859.8 | 7859.8 | same
- 0 | therapeutic_closing_charge | charge on another reservation of the resident | 7859.8 | 7859.8 | same
- 1 | hospital_opening_charge | closed older agreement (other tier, no notice, change date inside leave) | 7715.1 | 7715.1 | same
- 1 | hospital_opening_charge | payer_reserved entry dated later on same reservation | 7715.1 | 7715.1 | same
- 1 | hospital_opening_charge | unpaid_hold_notice delivered later | 7715.1 | 7715.1 | same
- 1 | hospital_opening_charge | room_change_proration credit from the departure date | 7715.1 | 7715.1 | same
- 1 | hospital_opening_charge | later private request of another type | 7715.1 | 7715.1 | same
- 1 | hospital_opening_charge | charge on another reservation of the resident | 7715.1 | 7715.1 | same
- 1 | hospital_closing_charge | closed older agreement (other tier, no notice, change date inside leave) | 10696.0 | 10696.0 | same
- 1 | hospital_closing_charge | payer_reserved entry dated later on same reservation | 10696.0 | 10696.0 | same
- 1 | hospital_closing_charge | unpaid_hold_notice delivered later | 10696.0 | 10696.0 | same
- 1 | hospital_closing_charge | room_change_proration credit from the departure date | 10696.0 | 10696.0 | same
- 1 | hospital_closing_charge | later private request of another type | 10696.0 | 10696.0 | same
- 1 | hospital_closing_charge | charge on another reservation of the resident | 10696.0 | 10696.0 | same
- 0 | therapeutic_opening_charge | ABSENT: no credit from the departure date (fall-through: own tier) | 10191.7 | 10754.1 | MOVED
- 1 | hospital_opening_charge | ABSENT: no credit from the departure date (fall-through: own tier) | 7715.1 | 8101.75 | MOVED
- 0 | therapeutic_opening_charge | ABSENT: no room change request (fall-through: tier held) | 10191.7 | 9469.7 | MOVED
- 1 | hospital_closing_charge | ABSENT: no room change request (fall-through: tier held) | 10696.0 | 9625.0 | MOVED
- 1 | hospital_opening_charge | ABSENT: no transfer notice (all days unnoticed) | 7715.1 | 0.0 | MOVED
- 1 | hospital_opening_charge | TIE/REPLACE: notice delivered again to the resident 2026-09-13 (earlier of latest per person = rep 09-11) | 7715.1 | 7715.1 | same
### Sweeps
- compute_basis quote sweep: every quote verbatim in its own rule; basis keys == compute bindings (0 misses).
- stale proof-text sweep: no date, amount or id in any prerequisite policy_source / condition / effect (0 hits).
- tools: no datetime/time/random/uuid/secrets substring; no factor id inside a tool name; no ordering word in docstrings;
  each body calls ctx.create/ctx.update itself, refuses a non-positive amount and stores amount half up to the cent as documented.
### Gates (full block, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK
REWORK round 4: gates 7/7 green
## REWORK round 5 (audit revision_4 + coordinator round-5 route) — delivered
- Route applied: every room change during a leave and every lever built on it is gone. Levers used are those of the
  coordinator's round-5 list: rate-notice binding (method), extended-hold percent on days already charged, dietary
  credit keyed to the bed held, isolation pricing from the agreement's placement before the leave, MA reserved days per
  hospitalization, census return day, days after the hold ended (return / release). Owners and edge kinds of Plan Z
  kept; draw kept (T0: A=4, B=6, C=5; T1: D=5, E=6). Tools now take the charged day count (integer days) as an argument
  and record it on the charge; amounts are stored with an exact Decimal half-up helper; compute rounds RND(x + 1e-9, 2).
- Scopes (one shared scope sentence, identical in all five overwrites): A/C opening and closing entry of a released
  Private Pay Therapeutic Leave Bed Hold with more than one private entry; B the entry of a single-entry Private Pay
  Hospital Leave Bed Hold; D/E opening and closing private entry of a Medicaid Hospital Leave Reserved Bed hold with more
  than one private entry. Tools: A post_therapeutic_opening_charge_78fe9a0a, B sign_hospital_stay_charge_56dfc7d9, C sign_therapeutic_closing_charge_194aeb06, D post_hospital_opening_charge_991dca72, E sign_hospital_closing_charge_702d4c7f.
### Round 5 per-item closure (audit revision_4)
- R4-1 (room change during a leave vs base hold_end same-room return): removed from every rule, compute, factor and seed;
  no room change request and no in-leave room change remain in either world.
- R4-2 (room-change factors weigh only jointly): all eight factors deleted. Every remaining factor moves the result alone
  with every other factor at baseline (T2 table below, verified by evaluation, not by argument).
- R4-3 (request selector second reading): the request read is deleted with the lever.
- R4-4 (gate sentence broader than its condition): the sentence now names 'every earlier private-pay hospital leave of the
  resident that carried a single resident-private entry', the same set as the condition and as B's scope, so B's tool
  resolves the gate in every engaged world.
- R4-5 (seeds): renewals are private_extension elections (T0 effective 2026-10-05, T1 effective 2026-10-06); T0 carries the
  October advance room-and-board bill (two rate spans, issued 2026-09-25) with its discharge_proration credits and the
  return rebill; T1's agreement is converted for October, so no private bill is owed. The earlier single-entry charge
  is posted on statement day 3 (O-16). Task 1's Medical Assistance case, pending accruals, settlements, estimated and
  actual patient pay with payments and the application signature are seeded from the application.
- O-14: isolation pricing is a factor of all five schedules. O-15: no bariatric move remains. O-11 persists by the rule's
  definition (an opening entry has no earlier charge). O-1 persists by design (XF 32).
- Day factors rest on records the base rules read: the reservation's return_date / release_date / end_date and the
  departure date with the tier's per-hospitalization limit; the bookings they correct are producible (base: 'a booked day
  later found to fall after the return ... or booked in error is reversed against its booked entry'), booked at month
  end or when the leave's end was logged.
### T1 table, task 0 (factor's baseline alone; heading gold | all-baseline)
- bedhold_ext_therapeutic_opening_charge [9118.20 | 11336.00]: to_rate_binding 9464.00; to_extended_hold 9617.40; to_dietary_credit 9484.80; to_isolation_rate 10032.10
- bedhold_ext_hospital_stay_charge [6663.30 | 10464.00]: hs_rate_binding 6916.00; hs_extended_hold 7028.10; hs_dietary_credit 6931.20; hs_isolation_rate 7331.15; hs_return_day 7014.00; hs_after_hold_end 8066.10
- bedhold_ext_therapeutic_closing_charge [4720.20 | 8284.00]: tc_rate_binding 4863.00; tc_extended_hold 5590.50; tc_dietary_credit 4931.70; tc_isolation_rate 5194.50; tc_after_hold_end 6017.00
### T1 table, task 1 (factor's baseline alone; heading gold | all-baseline)
- bedhold_ext_hospital_opening_charge [7715.40 | 10900.00]: ho_rate_binding 8008.00; ho_extended_hold 8137.80; ho_dietary_credit 8025.60; ho_isolation_rate 8488.70; ho_reserved_days 8767.50
- bedhold_ext_hospital_closing_charge [4059.90 | 7412.00]: hc_rate_binding 4214.60; hc_extended_hold 4808.70; hc_dietary_credit 4243.20; hc_isolation_rate 4468.75; hc_return_day 4372.20; hc_after_hold_end 4996.80
### T2 table (factor alone live, all others at baseline, evaluated on the task world)
- T2 | task 0 | to_rate_binding | all-baseline 11336.00 | alone live 10946.00 | MOVES
- T2 | task 0 | to_extended_hold | all-baseline 11336.00 | alone live 10769.20 | MOVES
- T2 | task 0 | to_dietary_credit | all-baseline 11336.00 | alone live 10969.40 | MOVES
- T2 | task 0 | to_isolation_rate | all-baseline 11336.00 | alone live 10348.00 | MOVES
- T2 | task 0 | hs_rate_binding | all-baseline 10464.00 | alone live 10104.00 | MOVES
- T2 | task 0 | hs_extended_hold | all-baseline 10464.00 | alone live 9940.80 | MOVES
- T2 | task 0 | hs_dietary_credit | all-baseline 10464.00 | alone live 10125.60 | MOVES
- T2 | task 0 | hs_isolation_rate | all-baseline 10464.00 | alone live 9552.00 | MOVES
- T2 | task 0 | hs_return_day | all-baseline 10464.00 | alone live 10028.00 | MOVES
- T2 | task 0 | hs_after_hold_end | all-baseline 10464.00 | alone live 8720.00 | MOVES
- T2 | task 0 | tc_rate_binding | all-baseline 8284.00 | alone live 8104.00 | MOVES
- T2 | task 0 | tc_extended_hold | all-baseline 8284.00 | alone live 7041.40 | MOVES
- T2 | task 0 | tc_dietary_credit | all-baseline 8284.00 | alone live 8016.10 | MOVES
- T2 | task 0 | tc_isolation_rate | all-baseline 8284.00 | alone live 7562.00 | MOVES
- T2 | task 0 | tc_after_hold_end | all-baseline 8284.00 | alone live 6540.00 | MOVES
- T2 | task 1 | ho_rate_binding | all-baseline 10900.00 | alone live 10525.00 | MOVES
- T2 | task 1 | ho_extended_hold | all-baseline 10900.00 | alone live 10355.00 | MOVES
- T2 | task 1 | ho_dietary_credit | all-baseline 10900.00 | alone live 10547.50 | MOVES
- T2 | task 1 | ho_isolation_rate | all-baseline 10900.00 | alone live 9950.00 | MOVES
- T2 | task 1 | ho_reserved_days | all-baseline 10900.00 | alone live 9592.00 | MOVES
- T2 | task 1 | hc_rate_binding | all-baseline 7412.00 | alone live 7157.00 | MOVES
- T2 | task 1 | hc_extended_hold | all-baseline 7412.00 | alone live 6300.20 | MOVES
- T2 | task 1 | hc_dietary_credit | all-baseline 7412.00 | alone live 7172.30 | MOVES
- T2 | task 1 | hc_isolation_rate | all-baseline 7412.00 | alone live 6766.00 | MOVES
- T2 | task 1 | hc_return_day | all-baseline 7412.00 | alone live 6976.00 | MOVES
- T2 | task 1 | hc_after_hold_end | all-baseline 7412.00 | alone live 6104.00 | MOVES
### Pairwise method-tier table (rate binding, the method factor of every schedule; XF 7)
- late notice vs no notice: a later-of pick over the notice date plus notice days vs no current days at all.
- late notice vs otherwise: adds the notice date and notice-days inputs and a max pick to the schedule-date split.
- no notice vs otherwise: 0 on its whole domain vs a date-span count (otherwise is 0 only before the schedule date).
### Decoy / absent-record probe sweep (scratch copies; expected outcome per rule wording)
- task 0 | therapeutic_opening_charge | second, closed older agreement (other tier, no isolation, no notice) | 9118.20 | same | OK
- task 0 | therapeutic_opening_charge | cancelled agreement record | 9118.20 | same | OK
- task 0 | therapeutic_opening_charge | payer-reserved entry with a later last day on the same reservation | 9118.20 | same | OK
- task 0 | therapeutic_opening_charge | unpaid-hold notice delivered later (other notice type) | 9118.20 | same | OK
- task 0 | therapeutic_opening_charge | same-date second transfer-notice delivery to the representative (tie) | 9118.20 | same | OK
- task 0 | therapeutic_opening_charge | charge and reversal on another reservation | 9118.20 | same | OK
- task 0 | therapeutic_opening_charge | reversal on the entry for another reason, already reflected (1 day) | 8767.50 | moved | OK
- task 0 | hospital_stay_charge | second, closed older agreement (other tier, no isolation, no notice) | 6663.30 | same | OK
- task 0 | hospital_stay_charge | cancelled agreement record | 6663.30 | same | OK
- task 0 | hospital_stay_charge | payer-reserved entry with a later last day on the same reservation | 6663.30 | same | OK
- task 0 | hospital_stay_charge | unpaid-hold notice delivered later (other notice type) | 6663.30 | same | OK
- task 0 | hospital_stay_charge | same-date second transfer-notice delivery to the representative (tie) | 6663.30 | same | OK
- task 0 | hospital_stay_charge | charge and reversal on another reservation | 6663.30 | same | OK
- task 0 | hospital_stay_charge | reversal on the entry for another reason, already reflected (1 day) | 6312.60 | moved | OK
- task 0 | therapeutic_closing_charge | second, closed older agreement (other tier, no isolation, no notice) | 4720.20 | same | OK
- task 0 | therapeutic_closing_charge | cancelled agreement record | 4720.20 | same | OK
- task 0 | therapeutic_closing_charge | payer-reserved entry with a later last day on the same reservation | 4720.20 | same | OK
- task 0 | therapeutic_closing_charge | unpaid-hold notice delivered later (other notice type) | 4720.20 | same | OK
- task 0 | therapeutic_closing_charge | same-date second transfer-notice delivery to the representative (tie) | 4720.20 | same | OK
- task 0 | therapeutic_closing_charge | charge and reversal on another reservation | 4720.20 | same | OK
- task 0 | therapeutic_closing_charge | reversal on the entry for another reason, already reflected (1 day) | 4407.90 | moved | OK
- task 1 | hospital_opening_charge | second, closed older agreement (other tier, no isolation, no notice) | 7715.40 | same | OK
- task 1 | hospital_opening_charge | cancelled agreement record | 7715.40 | same | OK
- task 1 | hospital_opening_charge | payer-reserved entry with a later last day on the same reservation | 7715.40 | same | OK
- task 1 | hospital_opening_charge | unpaid-hold notice delivered later (other notice type) | 7715.40 | same | OK
- task 1 | hospital_opening_charge | same-date second transfer-notice delivery to the representative (tie) | 7715.40 | same | OK
- task 1 | hospital_opening_charge | charge and reversal on another reservation | 7715.40 | same | OK
- task 1 | hospital_opening_charge | reversal on the entry for another reason, already reflected (1 day) | 7364.70 | moved | OK
- task 1 | hospital_closing_charge | second, closed older agreement (other tier, no isolation, no notice) | 4059.90 | same | OK
- task 1 | hospital_closing_charge | cancelled agreement record | 4059.90 | same | OK
- task 1 | hospital_closing_charge | payer-reserved entry with a later last day on the same reservation | 4059.90 | same | OK
- task 1 | hospital_closing_charge | unpaid-hold notice delivered later (other notice type) | 4059.90 | same | OK
- task 1 | hospital_closing_charge | same-date second transfer-notice delivery to the representative (tie) | 4059.90 | same | OK
- task 1 | hospital_closing_charge | charge and reversal on another reservation | 4059.90 | same | OK
- task 1 | hospital_closing_charge | reversal on the entry for another reason, already reflected (1 day) | 3747.60 | moved | OK
- task 0 | therapeutic_opening_charge | ABSENT: no isolation placement (room priced at its own tier) | 10032.10 | moved | OK
- task 0 | hospital_stay_charge | ABSENT: no return date (no return-day or after-return days off) | 8416.80 | moved | OK
- task 0 | therapeutic_closing_charge | ABSENT: no release date (no days after the hold ended) | 6017.00 | moved | OK
- task 1 | hospital_opening_charge | ABSENT: no transfer notice (all days unnoticed -> 0) | 0.00 | moved | OK
- task 1 | hospital_opening_charge | SECOND delivery to the resident 2026-09-10 (latest per person; earlier of the two = representative 2026-08-25) | 7715.40 | same | OK
- task 1 | hospital_closing_charge | EDGE: return date after the entry's last day (nothing taken off) | 5309.10 | moved | OK
- task 1 | hospital_opening_charge | EDGE: departure 5 days earlier (reserved days end before the entry: 0 covered) | 8767.50 | moved | OK
### Sweeps
- compute_basis quotes verbatim in their own rule; basis keys == compute bindings; baseline and prerequisite sentences
  in the rule; one shared scope sentence; no factor reads another factor's binding (0 misses).
- Stale proof-text: no date, amount or id in any prerequisite policy_source / condition / effect (0 hits).
- Tools: no datetime/time/random/uuid/secrets substring, no factor id in a tool name, no ordering word in docstrings;
  each body refuses a non-whole or < 1 day count and a non-positive amount, stores amount half up via Decimal, and calls
  ctx.create / ctx.update itself.
### Gates (full block, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK
REWORK round 5: gates 7/7 green
## REWORK round 6 (audit revision_5)
- R5-2 (task 0 back-dated release): the written release is now logged 2026-10-15 10:05, the day it takes effect, matching
  the reservation's release_date / end_date 2026-10-15; no reading puts the release day anywhere else. Ruth came back
  2026-10-20 to the next available bed (431); the room-and-board rebill now runs 2026-10-20..2026-10-31 (account_balance
  recomputed from the ledger, initial_state and db_closure alike). The October entry stays booked 2026-10-01..2026-10-19:
  the clerk booked the leave through the day before her return instead of through the release day, a booking base
  reverses on discovery ("a booked day later found to fall after ... or booked in error is reversed against its booked
  entry"). Rationale, objective and provenance texts updated; C's gold and figures unchanged (gates recomputed them).
- R5-1 (ho_reserved_days, hs_return_day, hc_return_day, hs_after_hold_end, tc_after_hold_end, hc_after_hold_end): kept.
  These are the levers the coordinator's route names ("MA reserved days ...", "census day counting (departure/return/
  same-day/observation), release-effective timing"), re-issued unchanged for this round; the audit marks the item
  coordinator-waivable. What forces them: the fixed draw (T0 B=6, C=5; T1 D=5, E=6) against the four clean levers each
  charge carries (rate binding, extended hold, dietary credit, isolation). Struck, every schedule keeps 4 factors and the
  drawn counts fail check_compute. Each factor's baseline is the base charge clause read literally ("Each booked
  resident_private entry is charged once: the days times the bed-hold daily rate"), the booked days; the factor tiers
  read the reservation's return_date / release_date / departure date and the tier's per-hospitalization limit.
- O-19: whole_days and half_up_cents now return the documented refusal for non-numeric or non-finite input instead of
  raising (tool bodies enforce their docstrings for every input).
- O-17 (long isolation placements): kept; contact precautions for a colonized wound can run for months, and each
  placement is billed on the isolation basis month by month on the private ledger. O-11, O-1, O-18 unchanged.
- Re-checked after the seed edit: probes on C (release read, other-reservation charges, closed agreement) unchanged;
  T1/T2 tables of round 5 unchanged (no rule, compute or scored seed field moved).
### Gates (full block, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK
REWORK round 6: gates 7/7 green
## REWORK round 7 (KB audit _kb_verdict.md revision_1: S1, S2)
- S1 (isolation rule says the move is recorded before the leave; compute never tested the date) — class closed in all
  five schedules (to/hs/tc/ho/hc_isolation_rate): new binding {p}_agr_move = the agreement's last_room_change_date;
  both isolation tiers now require it to be dated no later than the departure date (DAYS(move, departure) >= 0). Rule
  sentence reworded to the tested condition ("the agreement's last room change, the center's infection-control move,
  being dated no later than the departure date"); ladder texts, compute_basis and cross_category reads updated. Scored
  figures unchanged (both worlds record the move before every leave).
- S2 (no sentence placed a rate notice delivered on or after the schedule date) — class closed in all five
  *_rate_binding factors: the late-notice tier now reads "delivered fewer than the agreement's rate-change notice days
  before the schedule date, or on or after the schedule date", which is what the compute already did and what the
  private charter's later-of rule (schedule date vs notice plus the notice days) gives. Ladder and tier_taken texts
  updated; scored figures unchanged.
- S3 (decided placement note) and S4 (base parameter name, BLUEPRINT-KNOWN): not touched, as routed.
- Re-checked: probes over the changed read (move after departure, move absent, move on the departure date, second closed
  agreement with a later move) all follow the rule; T1 and T2 hold for all 26 factors; compute_basis quote sweep, stale
  proof-text sweep and factor-independence check clean.
### Gates (full block, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK
REWORK round 7: gates 7/7 green
## REWORK round 8 (KB cross-product re-judge, _kb_verdict.md revision_3: S5, S6)
- S5 (task 1: converted agreement with no balance or deposit must be closed): world changed so the agreement legitimately
  stays converted. The family had not paid the May room-and-board bill when the Medical Assistance application went in;
  at disposition (2026-06-25, within 30 days of the conversion) the deposit is applied to the open balance first (private
  docs: "Applied to the open balance first; any remainder refunded"; "A deposit applied at disposition is posted as a
  payment from the security deposit"): disposition row now applied_to_balance and a deposit_application payment against
  the May charge; 384.00 of May stays owed. No late charge (none while the stay is converted) and no collection referral
  (none while converted to Medicaid pending). Agreement: payer_converted, account 384.00, deposit 0.00 — open by
  agreement_closing_rule ("A converted agreement stays open while any private charge ... remains on it"). The bed-hold
  reads (status, signing, notice, isolation, tier, move date) are unchanged, so no scored value moves. Rationale and the
  private-ledger objective updated.
- S6 (task 0: 2026-07-10 payment applied in full to a charge with a smaller open balance): the July payment is now the
  July charge's open balance after the 07-08 credit (2,688.00); the August charge is paid in full on 08-10 and the July
  return rebill is paid on 08-10 by its own payment. No past-due room-and-board month remains, so no late charge is owed.
  account_balance recomputed (unchanged in total). No scored value moves.
- Class sweep (bounded, exhaustive, one pass): every seeded row of every other product in both worlds re-checked against
  the published private and medicaid documents (spans and day counts, rates, charge bases, credits inside their charge
  spans at the charge's rate, every payment applied no more than the named charge's open balance at its posting date,
  deposit at 30 days of the admission rate, disposition within 30 days of conversion, agreement balance = sum of open
  balances, patient pay = income - PNA - premiums, accrual = days x the rate he was billed, settlements = accruals,
  application signature before submission). 68 rows/records, 0 defects; listed below.
- extended yaml and task_tools.py: unchanged this round. Scored values: none moved (COMPUTE recomputes every figure).
  Probe/T1/T2: no read of any computation changed (only account_balance, payment and disposition rows, which no bed-hold
  compute reads); stale-text sweep over rationale, objectives, closures, traces and personas clean.
### Cross-product seed rows checked (round 8)
- task 0 | private_ledger 2784fef3 | 2026-01-05 | private_room_board_charge | 10368.00 | OK span 2026-01-05..2026-01-31 = 27 days x 384.00 (first_month_partial)
- task 0 | private_ledger 6af2a192 | 2026-01-05 | private_deposit_received | 11520.00 | OK deposit 30 x 384.00 at admission while pending/active
- task 0 | private_ledger 11af5eb1 | 2026-01-05 | private_payment | 10368.00 | OK applied 10368.00 <= open 10368.00 (check, representative)
- task 0 | private_ledger da27b14a | 2026-01-25 | private_room_board_charge | 10752.00 | OK span 2026-02-01..2026-02-28 = 28 days x 384.00 (standard)
- task 0 | private_ledger bd210852 | 2026-02-10 | private_payment | 10752.00 | OK applied 10752.00 <= open 10752.00 (check, representative)
- task 0 | private_ledger a0519971 | 2026-02-25 | private_room_board_charge | 11904.00 | OK span 2026-03-01..2026-03-31 = 31 days x 384.00 (standard)
- task 0 | private_ledger c1f1c36d | 2026-03-10 | private_payment | 11904.00 | OK applied 11904.00 <= open 11904.00 (check, representative)
- task 0 | private_ledger 1e3f82cb | 2026-03-14 | private_adjustment | 6912.00 | OK discharge_proration 18 x charge rate 384.00, inside the charge span
- task 0 | private_ledger b8b4487b | 2026-03-15 | private_room_board_charge | 6528.00 | OK span 2026-03-15..2026-03-31 = 17 days x 384.00 (standard)
- task 0 | private_ledger 665415e3 | 2026-03-25 | private_room_board_charge | 11520.00 | OK span 2026-04-01..2026-04-30 = 30 days x 384.00 (standard)
- task 0 | private_ledger 355908dd | 2026-04-10 | private_payment | 11136.00 | OK applied 11136.00 <= open 11520.00 (check, representative)
- task 0 | private_ledger 4759e2ba | 2026-04-25 | private_room_board_charge | 11904.00 | OK span 2026-05-01..2026-05-31 = 31 days x 384.00 (standard)
- task 0 | private_ledger da789c90 | 2026-05-10 | private_payment | 11904.00 | OK applied 11904.00 <= open 11904.00 (check, representative)
- task 0 | private_ledger 93bcb7a7 | 2026-05-25 | private_room_board_charge | 11520.00 | OK span 2026-06-01..2026-06-30 = 30 days x 384.00 (standard)
- task 0 | private_ledger 26c73429 | 2026-06-10 | private_payment | 11520.00 | OK applied 11520.00 <= open 11520.00 (check, representative)
- task 0 | private_ledger 22957560 | 2026-06-16 | private_room_board_charge | 5760.00 | OK span 2026-06-16..2026-06-30 = 15 days x 384.00 (isolation_rate)
- task 0 | private_ledger d1bb6d14 | 2026-06-16 | private_adjustment | 5760.00 | OK room_change_proration 15 x charge rate 384.00, inside the charge span
- task 0 | private_ledger c0daf344 | 2026-06-25 | private_room_board_charge | 11904.00 | OK span 2026-07-01..2026-07-31 = 31 days x 384.00 (isolation_rate)
- task 0 | private_ledger 99718209 | 2026-07-08 | private_adjustment | 9216.00 | OK discharge_proration 24 x charge rate 384.00, inside the charge span
- task 0 | private_ledger 8ddea75c | 2026-07-10 | private_payment | 2688.00 | OK applied 2688.00 <= open 2688.00 (check, representative)
- task 0 | private_ledger be6d9617 | 2026-07-25 | private_room_board_charge | 11904.00 | OK span 2026-08-01..2026-08-31 = 31 days x 384.00 (isolation_rate)
- task 0 | private_ledger 4c06a889 | 2026-08-01 | private_room_board_charge | 1920.00 | OK span 2026-07-27..2026-07-31 = 5 days x 384.00 (isolation_rate)
- task 0 | private_ledger fdf812c0 | 2026-08-10 | private_payment | 11904.00 | OK applied 11904.00 <= open 11904.00 (check, representative)
- task 0 | private_ledger 612a6469 | 2026-08-10 | private_payment | 1920.00 | OK applied 1920.00 <= open 1920.00 (check, representative)
- task 0 | private_ledger ab1d5fbb | 2026-08-25 | private_room_board_charge | 11520.00 | OK span 2026-09-01..2026-09-30 = 30 days x 384.00 (isolation_rate)
- task 0 | private_ledger 54840741 | 2026-09-05 | private_adjustment | 9984.00 | OK discharge_proration 26 x charge rate 384.00, inside the charge span
- task 0 | private_ledger 869baba5 | 2026-09-10 | private_payment | 1536.00 | OK applied 1536.00 <= open 1536.00 (check, representative)
- task 0 | private_ledger b5dcc902 | 2026-09-25 | private_room_board_charge | 4608.00 | OK span 2026-10-01..2026-10-12 = 12 days x 384.00 (isolation_rate)
- task 0 | private_ledger 6f9cf688 | 2026-09-25 | private_room_board_charge | 7562.00 | OK span 2026-10-13..2026-10-31 = 19 days x 398.00 (isolation_rate)
- task 0 | private_ledger 2e7bdbc1 | 2026-09-25 | private_adjustment | 4608.00 | OK discharge_proration 12 x charge rate 384.00, inside the charge span
- task 0 | private_ledger 2494a02a | 2026-09-25 | private_adjustment | 7562.00 | OK discharge_proration 19 x charge rate 398.00, inside the charge span
- task 0 | private_ledger 78ab8c28 | 2026-10-20 | private_room_board_charge | 4776.00 | OK span 2026-10-20..2026-10-31 = 12 days x 398.00 (isolation_rate)
- task 0 | private_ledger c82fe9dd | 2026-10-25 | private_room_board_charge | 11940.00 | OK span 2026-11-01..2026-11-30 = 30 days x 398.00 (isolation_rate)
- task 0 | private_agreements dfd84afb | status active | account_balance 16716.00 = sum of open balances 16716.00 | deposit 11520.00 | OK
- task 0 | open private charges at frozen time: 2026-03 6528.00; 2026-04 384.00; 2026-06 5760.00; 2026-10 4776.00; 2026-11 11940.00
- task 1 | private_ledger 70a2dcff | 2026-02-02 | private_room_board_charge | 10368.00 | OK span 2026-02-02..2026-02-28 = 27 days x 384.00 (first_month_partial)
- task 1 | private_ledger 5e102549 | 2026-02-02 | private_deposit_received | 11520.00 | OK deposit 30 x 384.00 at admission while pending/active
- task 1 | private_ledger 90e6bc33 | 2026-02-02 | private_payment | 10368.00 | OK applied 10368.00 <= open 10368.00 (check, representative)
- task 1 | private_ledger c7ded083 | 2026-02-25 | private_room_board_charge | 11904.00 | OK span 2026-03-01..2026-03-31 = 31 days x 384.00 (standard)
- task 1 | private_ledger ce626de9 | 2026-03-10 | private_payment | 11904.00 | OK applied 11904.00 <= open 11904.00 (check, representative)
- task 1 | private_ledger 7e924e31 | 2026-03-25 | private_room_board_charge | 11520.00 | OK span 2026-04-01..2026-04-30 = 30 days x 384.00 (standard)
- task 1 | private_ledger 8dae43a3 | 2026-04-10 | private_payment | 11520.00 | OK applied 11520.00 <= open 11520.00 (check, representative)
- task 1 | private_ledger 6069b4a3 | 2026-04-14 | private_room_board_charge | 6528.00 | OK span 2026-04-14..2026-04-30 = 17 days x 384.00 (isolation_rate)
- task 1 | private_ledger a0df6fdf | 2026-04-14 | private_adjustment | 6528.00 | OK room_change_proration 17 x charge rate 384.00, inside the charge span
- task 1 | private_ledger 62e9f29a | 2026-04-25 | private_room_board_charge | 11904.00 | OK span 2026-05-01..2026-05-31 = 31 days x 384.00 (isolation_rate)
- task 1 | private_ledger 1451f392 | 2026-05-25 | private_room_board_charge | 11520.00 | OK span 2026-06-01..2026-06-30 = 30 days x 384.00 (isolation_rate)
- task 1 | private_ledger 88e557d6 | 2026-06-05 | private_adjustment | 11520.00 | OK payer_conversion_credit 30 x charge rate 384.00, inside the charge span
- task 1 | private_ledger d0098f84 | 2026-06-25 | private_deposit_disposition | 11520.00 | OK applied_to_balance 11520.00 within 30 days of the conversion, open balance first
- task 1 | private_ledger 8aeeb18e | 2026-06-25 | private_payment | 11520.00 | OK applied 11520.00 <= open 11904.00 (deposit_application, security_deposit)
- task 1 | private_agreements f19f9229 | status payer_converted | account_balance 384.00 = sum of open balances 384.00 | deposit 0.00 | OK
- task 1 | open private charges at frozen time: 2026-04 6528.00; 2026-05 384.00
- task 1 | medicaid_cases 768fa88d | patient pay 1476.10 = income - 45.00 PNA - premiums = 1476.10 | OK
- task 1 | medicaid_ledger 9d1ead6e | 2026-06-05 | medicaid_patient_pay_charge | 1476.10 | OK estimated_pending 2026-06 = patient pay
- task 1 | medicaid_ledger b033790b | 2026-06-10 | medicaid_patient_pay_payment | 1476.10 | OK
- task 1 | medicaid_ledger 7273d1e4 | 2026-06-30 | medicaid_pending_accrual | 11520.00 | OK 30 days x 384.00
- task 1 | medicaid_ledger 22fb808b | 2026-07-01 | medicaid_patient_pay_charge | 1476.10 | OK estimated_pending 2026-07 = patient pay
- task 1 | medicaid_ledger b7897ea2 | 2026-07-10 | medicaid_patient_pay_payment | 1476.10 | OK
- task 1 | medicaid_ledger 37e40b5c | 2026-07-31 | medicaid_pending_accrual | 11904.00 | OK 31 days x 384.00
- task 1 | medicaid_ledger 8a186214 | 2026-08-01 | medicaid_patient_pay_charge | 1476.10 | OK estimated_pending 2026-08 = patient pay
- task 1 | medicaid_ledger 3f96b9a0 | 2026-08-03 | medicaid_pending_settlement | 11520.00 | OK settles accrual 2026-06 approved_ma_covered amount equal
- task 1 | medicaid_ledger e03a6af1 | 2026-08-03 | medicaid_pending_settlement | 11904.00 | OK settles accrual 2026-07 approved_ma_covered amount equal
- task 1 | medicaid_ledger 6851909c | 2026-08-10 | medicaid_patient_pay_payment | 1476.10 | OK
- task 1 | medicaid_ledger 06ab4b82 | 2026-09-01 | medicaid_patient_pay_charge | 1476.10 | OK actual_notice 2026-09 = patient pay
- task 1 | medicaid_ledger 37d32583 | 2026-09-10 | medicaid_patient_pay_payment | 1476.10 | OK
- task 1 | medicaid_ledger e604285d | 2026-10-01 | medicaid_patient_pay_charge | 1476.10 | OK actual_notice 2026-10 = patient pay
- task 1 | medicaid_ledger 35855ce3 | 2026-10-09 | medicaid_patient_pay_payment | 1476.10 | OK
- task 1 | medicaid_ledger 15eb95c2 | 2026-11-01 | medicaid_patient_pay_charge | 1476.10 | OK actual_notice 2026-11 = patient pay
- task 1 | medicaid_requests 9c07edc3 | application_signature by resident 2026-06-03 14:00:00 EDT | OK before the 06-05 submission
### Gates (full block, no --task)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK
REWORK round 8: gates 7/7 green
