# Runtime-context blind audit — medicare_part_a_coinsurance_and_coverage_end / task 0

## revision_1

## blind_answer

- Freeze: written 2026-10-22T18:10Z, before any source-layer material was opened. Auditor: independent KB-audit agent (not the renderer, not the policy-side auditor).
- Freeze hashes: published corpus `docs/medicare/*.json` (56 files, `cat *.json | sha256sum`) = `ece4e2042e50f5ee725e0527ff80321a1d41596f85394e0b8f72fa0aafd98af8`; runtime view `task0.runtime.json` = `2f1722ac336640731dac386f6c6a0b14d7c136256b2e4ba09413a5e95a595ff6`.
- Visible materials used: blueprint `background` (lines 1-4 of blueprint.yaml only), frozen_time `2026-01-08 10:20:00 EST`, user_scenario, title/content of the 56 published `docs/medicare` documents (no `meta` read), share-tool schemas from `db_query.py --list`, and share-finder returns through `db_query.py medicare_part_a_coinsurance_and_coverage_end 0`.
- Explicitly not read: `*.extended.yaml`, `task_tools.py`, `tasks/*/tasks/*.json`, worklog/plan, `initial_state`, document meta, `audits/render_source/`, everything under `audits/policy_task/` except the coordinator-quoted verdict line, products/*.yaml charters. Entry conditions (Step 0): policy verdict `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN` (checked last line); gate snapshot DOCS OK / TRACEABILITY OK (0 misses) supplied by the coordinator, not re-run. DB side is blind (tool-shaped queries only).
- contamination_disclosure: none. The brief carried no scored value.

### 1. What the user expresses

Joan Calloway (daughter, representative) opens: "I'd like to pay my dad's December Medicare coinsurance by card today." Target object = December Medicare coinsurance of Harold Dunmore; timing = today; method = card; she never offers a figure. Identity details given on request: DOB 1937-08-14 and phone 717-555-0143 (2 matches -> `verify_customer_identity` passes: "the caller is verified when at least 2 of them match"). Conditionally she reports Commonwealth Mutual Medigap K -> L from December 16, the Dec 6 hospital trip with the room held (back Dec 8), and the Dec 10 overnight with the bed not held; she authorises "whatever the business office needs to do on his account so that December can be paid". She runs the card payment herself when it is handed over. Simulator role: conveys needs, answers passively, executes the user tool.

### 2. Act / wait / refuse at the frozen moment

Act now, in order: post the resident coinsurance charge for the December block, then hand over the card payment. Grounds:
- `coinsurance_card_payments`: "A card payment toward a coinsurance block is taken only after the records carry a resident coinsurance charge for the coverage's latest booked coinsurance block, whenever that block's covered days take a resident share above nothing under the split in effect on them."
- Ledger: December block `b6959ca7` (`medicare_days_booked`, service_month 2025-12, days_21_100, day_count 29, benefit days 27-55, 2025-12-01..2025-12-31) carries only a `medigap_carrier` charge `336eafc4` (26 days, 209.50, 3561.50); no resident charge for it exists.
- Its days take a resident share above nothing: tier on file Plan L (`cost_sharing_split_by_tier`: resident 25%), and days before 2025-12-16 take the earlier share (50%, see 4).
- Certified-funds bar not triggered: no dishonored/returned payment in the ledger (`payment_posting_and_returned_payments`: limit 2 within 12 months).
- Coverage `ad6fb62b` status `active`.

### 3. Narrowest object and correlation keys

Coverage `ad6fb62b-c3e0-45b9-8ff1-ed7b440184e4`; latest booked days 21-100 entry (largest last service date) = `b6959ca7-0102-4c57-ac00-b5d846a9201c`. Excluded: Nov block `b8e7bbd1` (paid in full by check 628.50 on 2025-12-22 and by carrier), days_1_20 entry `607228a9`, carrier charge `336eafc4` (secondary party, not the resident charge). Block before = `b8e7bbd1` (last benefit day 26 = 27 - 1), its resident charge `df1b6673` (6 days, 209.50, 628.50, not a rebill). Bed-hold leave for 2025-12: `bedhold_day_booked` `1040aa5a` 2025-12-06..2025-12-07 (2 held days, reservation `82ee86ba`, Medicare Skilled Stay Hospital Leave Bed Hold, hold elected); reservation `98d77a7c` (Dec 10) was declined and books no held days. Reversals on `b6959ca7`: hospital_day 2025-12-10 (1, `4c95d7f4`), uncertified_day 2025-12-13..14 (2, `83f7710b`), both posted 2026-01-02.

### 4. Scored figures

Record test (resident-charge computation doc, same in the card-payment doc): one days_21_100 entry in 2025-12 (yes); one entry ending at benefit day 26 (yes); one bed-hold leave booked for 2025-12 and none taken back (yes); one reversal per reason, no booking error (yes); hospital reversal 12-10 does not cover held nights 12-06/07 and counts its 1 day (yes); uncertified 12-13..14 counts its 2 days, no held/hospital/LOA day inside (yes); supplemental date 12-16 after first service date 12-01, and block before's resident charge 628.50 = 6 x 209.50 x 50% exactly (yes); last service date 2025 (>= 2024). Passes.

(a) Resident coinsurance charge (`resident_coinsurance_charge_computation` + factors):
- Daily rate: factor doc "Daily Coinsurance Rate by Year of Service for Resident Charges": last service date 2025-12-31 in 2025 -> **209.50** (baseline 217.00). Tier rests on `b6959ca7.to_date`.
- Earlier share: factor doc "Earlier Coinsurance Share Read from the Preceding Block": block before's resident charge 628.50 vs 6 x 209.50 = 1257.00 -> exactly half -> **50%** (baseline 100%). Tier rests on `df1b6673`.
- Covered days: 29 booked - (1 + 2) reversed = **26** (= posting tool `day_count`).
- Calendar days before 12-16: 12-01..12-15 = 15. Off: LOA (baseline clause 6) none; bed-hold nights factor ("Bed-Hold Leave Nights within a Medicare Part A Coinsurance Block (Resident Charge)") 12-06, 12-07 both before the date -> 2 (rests on bedhold ledger `1040aa5a`, product Bed-Hold and Leave Reservations); hospital-day factor 12-10 before the date -> 1 (rests on `4c95d7f4`); uncertified-day factor 12-13..14 before the date, no held/hospital/LOA day inside -> 2 (rests on `83f7710b`). Days before = 15 - 5 = **10**; other days = 26 - 10 = **16** (= 12-16..12-31).
- Sum = 209.50 x (10 x 50 + 16 x 25) = 209.50 x 900 = 188550; /100, half-up once -> **1885.50**.
- Posting args: liable_party `resident`, service_month `2025-12`, day_count 26, daily_coinsurance_rate 209.50, amount 1885.50.

(b) Card payment (`card_payment_amount_computation` + factors): same rate factor (209.50), same earlier-share factor (50%); covered days 26 once the charge stands; before-days 15 - LOA 0 (baseline clause f) - held 2 - hospital 1 - uncertified 2 = 10; sum 188550 -> 1885.50; less net payments on the new charge 0 -> **1885.50**; not < 0, not > 5000.00; not above the new charge's open balance 1885.50 -> taken. Record test: the standing charge's day count 26 = 29 - 3 reversals posted on or before 2026-01-08 (yes).

Fall-back (computation documents alone, no factor): resident charge = 217.00 x (15 x 100 + 11 x 25) = 385175 -> **3851.75** (rate 217.00 and earlier share 100% are the baselines' own constants). Card payment fall-back on a 3851.75 charge = 3851.75 (on the correctly posted 1885.50 charge it would exceed the open balance and not be taken). Both differ from 1885.50.

Factor findability (record words that led there): "booked-days entry ... last service date 2025-12-31" -> year-of-service rate docs; "supplemental_effective_date 2025-12-16" + baseline wording "earlier share of 100 percent" + Nov resident charge row at 209.50 x 6 = 628.50 -> earlier-share docs; bedhold ledger `bedhold_day_booked` 2025-12-06..07 / reservation "Medicare Skilled Stay Hospital Leave Bed Hold" -> KB_search "bed hold" returns the bed-hold nights docs first; ledger `adjustment_reason` `hospital_day` / `uncertified_day` -> the hospital-day / uncertified-day docs. Observation (carried to Step 3b): the computation documents' "Record test" sentence already names the block before's 100/50/25 percent billing, the bed-hold leave and the hospital/LOA/uncertified reversals, and the "2024 or later" year floor, so the search is partly pre-solved by the baseline document.

### 5. Tool sequence

find_customers (name/DOB/phone) -> verify_customer_identity (customer_id, DOB 1937-08-14, phone 717-555-0143) -> find_medicare_coverages -> find_medicare_ledger -> find_bedhold_reservations / find_bedhold_ledger -> KB_search/grep -> unlock_agent_discoverable_tool `post_coinsurance_charge_97c12690` -> call (medicare_coverage_id `ad6fb62b-...`, days_entry_id `b6959ca7-...`, liable_party resident, service_month 2025-12, day_count 26, daily_coinsurance_rate 209.50, amount 1885.50) [agent-owned; return gives new charge id] -> unlock_user_discoverable_tool `pay_coinsurance_by_card_ebeca5a6` -> user calls (medicare_coverage_id, charge_entry_id = new resident charge id, amount 1885.50) [user-owned]. Terminal state: resident charge posted and fully paid; carrier charge 3561.50 still open (secondary share, followed up separately; not part of this call).

### 6. Problem tree from the visible materials alone

- P0 (root, customer's own write): card payment on the December block.
- P1: resident coinsurance charge for the latest booked coinsurance block.
- Edge P0 waits on P1. Hop chain: (i) visible sentence in `coinsurance_card_payments` (quoted in 2) names a record-visible state; (ii) query: ledger has no `liable_party: resident` charge naming `b6959ca7`; split in effect gives resident share > 0; so the state does not hold; (iii) searching "resident coinsurance charge ... latest booked coinsurance block" finds `original_coinsurance_charge_posting`: "The resident coinsurance charge is the resident's own original charge for the coverage's latest booked coinsurance block ... It falls due once that block stands booked on the episode" with the posting tool that "Posts one liable party's original coinsurance charge" -> the write that brings the state about. Mark: **state-derived**.
- P1 has no prerequisite sentence in its documents. Rate-year correction (`rate_year_corrections`) "falls due when such a charge stands" but a charge posted at 209.50 for a 2025 block bills nothing above that year's rate -> no write. Reduction for reversed covered days applies only to an uncertified reversal "posted ... after the charge was posted"; `83f7710b` was posted 2026-01-02, before the charge -> no write.
- Order: P1 (agent) -> P0 (user).

Counter-proofs:
- "Do only the card payment": the card tool needs a `charge_entry_id` of the resident charge and the visible sentence bars the payment until that charge is on record; paying against the carrier charge `336eafc4` is excluded ("applied to the resident's original coinsurance charge").
- Closest alternative split: retired clause "The tier that sets the split is the one in effect on the days of service" (retired in `coinsurance_block_pricing`) would also give 50%/25% here because Plan K preceded; the record-test sentence states that for a passing block the figures count days "as their own policies state", so the computation documents govern; the numbers coincide in this world.
- Closest alternative rate: 217.00 (2026 posting year / baseline) excluded by the year-of-service factor and `daily_coinsurance_rate_schedule` ("not the year a charge is posted").
- Closest alternative day count: 31 calendar days or 29 booked excluded by "booked days less every day reversed".
- Declined Dec-10 leave books no held days; the 12-10 night enters only through the hospital-day reversal (no double count).

## gt_comparison

Reveal: 2026-10-22T18:16Z, after the blind_answer above was on disk (sha256 of this file at freeze `1013b608966ea464e138814773a7fe4fd98658338553ccf9c9934cbe8744839b`). Read: `medicare.extended.yaml` (sha256 `203ecd58…ada6`), `task_tools.py` (`91fc2fae…08ada6`), `tasks/0.json` (evaluation_criteria, computations, prerequisite_closure). Fresh snapshot 2026-10-22T18:14: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses).

| Item | Blind | Source / GT | Same? |
|---|---|---|---|
| Act now, no refusal | post resident charge, then card | GT writes the same two | same |
| Write 1 | `post_coinsurance_charge_97c12690`(ad6fb62b, b6959ca7, resident, 2025-12, 26, 209.50, 1885.50) | identical args | same |
| Write 2 (user) | `pay_coinsurance_by_card_ebeca5a6`(ad6fb62b, new charge id, 1885.50) | identical (charge id `mlc_0cd346cc42d8` generated) | same |
| Tree | P0 card -> P1 resident charge, state-derived | `prerequisite_closure`: one edge card -> resident_block_share, form state, policy_source verbatim the sentence quoted in blind item 2 | same |
| Factor tiers | rate 209.50; earlier share 50; held 2; hospital 1; uncertified 2 | factor_trace identical | same |
| Fall-back | 3851.75 | `baseline_result` 3851.75 (resident charge); card baseline recorded as 0.00 (no charge standing at freeze) — both differ from 1885.50 | same |
| Hop marks | no pre-solved hop | — | — |

Cross-product: f_held_nights reads the Bed-Hold and Leave Reservations ledger (product `bedhold`, not yet published). The 2 held nights (2025-12-06..07, `1040aa5a`) and the reading that the declined Dec-10 reservation books no held day are **conditional** on the bedhold corpus agreeing when it is published (later re-judge).

Verdict: **PASS** (KB-RUNTIME). The blind route equals the source solution; no conclusion needed hidden material.

## revision_2

### blind_answer (re-audit, frozen 2026-10-22T19:45Z before re-reading the source)
- Trigger: renderer round 3 for E1 (`RENDER.log` tail: `RENDER round 3: DOCS OK`). Fresh snapshot 2026-10-22T19:39:06: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Runtime view hash unchanged; source hashes unchanged (`203ecd58…`, `91fc2fae…`).
- Corpus tree sha256 now `21f7544f55080c56cea18e414502da4d088801dcac1ef100b76ab045887e4cf6` (was `ece4e204…`). A title/content diff of all 56 documents against the revision_1 dump shows that only hypothetical examples / illustrations changed (35 hunks); every rule sentence, table of figures, factor ladder, prerequisite sentence, tool table and title is byte-identical.
- No sentence used as evidence in revision_1's blind answer was changed; no example was load-bearing in it. Re-deriving from the new corpus with the same tool returns gives the same tree, hop marks (all state-derived), factor tiers and figures as revision_1 — no item of the revision_1 blind answer changes. The revision_1 blind answer stands unmodified.
- contamination_disclosure: the auditor has seen the source and GT since revision_1 (disclosed); revision_2's blind check is therefore limited to confirming that the changed text (examples only) does not alter any visible derivation.

### gt_comparison
Same as revision_1: every write, argument and terminal state equals GT. **PASS** (KB-RUNTIME). Held-night tiers remain conditional on the unpublished bedhold corpus.

## revision_3

### blind_answer (re-audit, 2026-10-23T06:30Z)
- Entry: `RENDER.log` tail `RENDER round 4: DOCS OK`. Snapshot 2026-10-23T06:24:59: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Runtime views unchanged; corpus tree `77516c6824109cc2…`; source `medicare.extended.yaml` now `ddc0242f…` (S5 rework), `task_tools.py` unchanged.
- Diff of the corpus against revision_2: (a) one new sentence in the shares clause of each of the five computation documents ("When the tier on file prohibits balance billing, as the QMB Medicaid Crossover tier does, the <figure> bills the resident nothing for any day on or after the tier's supplemental effective date, … QMB protection not reaching back before it."); (b) the QMB examples in `resident_coinsurance_charge_computation` and `bank_draft_amount_computation` were rewritten. Nothing else changed.
- Effect on this task's visible derivation: none. The coverage is not in a tier that prohibits balance billing (task0 is Plan L; task1 is Full-Coinsurance Medigap, `cost_sharing_split_by_tier`: "Balance billing prohibited: No"), so the new sentence does not apply. The revision_1 tree, hop marks (state-derived), factor tiers and figures stand unchanged.
- contamination_disclosure: source and GT were already seen (disclosed in revision_2).

### gt_comparison
GT (`tasks/*.json`, re-read 2026-10-23) has unchanged writes and expected values. **PASS** (KB-RUNTIME). The held-night tiers remain conditional on the bedhold corpus.

## revision_4 (cross-product re-judge, 2026-10-23)

### blind_answer
- Entry: snapshot 2026-10-23 (`kb_snapshot.sh`): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Source `ddc0242f…`, tools `91fc2fae…` and docs/medicare `77516c68…` are unchanged since revision_3. Other corpora read for this pass: bedhold `24cc3f6d…` (all 50 titles; the 22 non-charge-computation documents in full), private `9c9f001f…` (daily-rate schedule). Also published: medicaid `b89c3e2b…`, trust `600f4bac…`, ancillary `73c2a1c3…`, therapy `d4b962bb…`.
- Other-product holdings: every finder for private, medicaid, trust, ancillary and therapy returns "No … records" for this resident. The only cross-product rows are Bed-Hold and Leave Reservations rows.
- The visible derivation is unchanged since revision_3. contamination_disclosure: source and GT were already seen (disclosed in revision_2).

### gt_comparison
- Cross-product rows checked (task0, Harold Dunmore), each against the published bedhold documents (and the private schedule) as of its posting date:
  1. Reservation `82ee86ba` — **OK**. Medicare Skilled Stay Hospital Leave Bed Hold (Part A stay + hospital leave, `payer_day_coverage_tiers`). Status returned. Departure 2025-12-06 20:50, emergency. Return 2025-12-08. end_date 2025-12-07 = the last held day, since the return day is never a leave day (`leave_day_census_terms`). held_days 2. private_hold_start 2025-12-06: the election falls inside the 24-hour window, so the hold runs from the departure date (`election_private_hold_terms`). charge_balance 768.00 with no payments (due 30 days after 2026-01-03).
  2. Notice `050fe7cf` — **OK**. Transfer notice to the representative 2025-12-06 22:30, within the 24 emergency hours after 20:50 (`notice_terms`).
  3. Election `c2e7a0f5` — **OK**. Hold by the representative, created 2025-12-07 08:40 (inside 24 hours of the 22:30 notice), effective 2025-12-06 (`hold_elections` item 4).
  4. Held-days entry `1040aa5a` — **OK**. resident_private, because every held day on this tier is the resident's own charge and Part A never pays a held day. Service month 2025-12. Days 2025-12-06..07, 2 days (away at midnight on the 6th and 7th; an observation night counts as hospital leave). Booked 2025-12-08 when the leave ended (`leave_day_booking`). No day falls after the return, so no reversal is owed.
  5. Charge `dbae3bbd` — **OK**. Posted 2026-01-03, the billing day 3 of the following month (`charge_billing_terms`). Names `1040aa5a`. 2 days x 384.00 = 768.00: the current basis in `charge_basis` (this entry is none of the five specially priced entries), at bed-hold percent 100 of the private schedule's Semi-Private Long-Term Care Room rate in effect July 2025 to June 2026, 384.00 (private `daily_rate_schedule_and_rate_notice`). No day was held before the notice's delivery date.
  6. Reservation `98d77a7c` — **OK**. Same tier, declined, departure 2025-12-10 21:30, return 2025-12-11, end_date 2025-12-10, end_reason declined, held 0, balance 0. A declined reservation books no held day (`leave_day_booking`: no booking while declined). Opened after `82ee86ba` was returned (`one_reservation_per_leave`).
  7. Notice `6063179c` — **OK**. 2025-12-10 22:15, within 24 hours of 21:30.
  8. Election `45b8c16a` — **OK**. Decline by the representative, effective 2025-12-10, created 22:30.
- Conditional items settled: the f_held_nights tier (2 held nights, 2025-12-06..07, both before 2025-12-16) rests on rows that the published bedhold corpus produces exactly. The declined Dec-10 reservation books none, so that night enters only through the Medicare hospital-day reversal. **Settled — no change** to 1885.50.
- Owed-at-once writes in a now-published corpus that could move a scored read: none.
  - bedhold: no held-day reversal is owed (no day after the return, no payer days, no error). No charge reduction is owed (no day before notice delivery, no payer days available). No booking is possible on the declined reservation. The charge is already posted, and paying it would not change any row the medicare factors read.
  - private, medicaid, trust, ancillary, therapy: no holdings, so nothing is owed.
  - medicare: as in revision_1, the only owed write is the resident charge, which is part of the tree.

**PASS** (KB-RUNTIME), with no conditional items remaining.
