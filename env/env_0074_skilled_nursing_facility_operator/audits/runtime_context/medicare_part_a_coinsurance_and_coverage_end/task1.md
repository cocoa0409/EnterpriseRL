# Runtime-context blind audit — medicare_part_a_coinsurance_and_coverage_end / task 1

## revision_1

## blind_answer

- Freeze: written 2026-10-22T18:14Z, before any source-layer material was opened. Auditor: independent KB-audit agent.
- Freeze hashes: published corpus `docs/medicare/*.json` (56 files) = `ece4e2042e50f5ee725e0527ff80321a1d41596f85394e0b8f72fa0aafd98af8`; runtime view `task1.runtime.json` = `fdce5879297dd463a1aa23e030fe1876d26ace968dd1faa5673a2b1e71fc718f`.
- Visible materials / forbidden list / entry conditions: identical to task0 revision_1 (blueprint background only, frozen_time `2026-01-28 10:40:00 EST`, user_scenario, 56 doc titles/contents without meta, share-tool schemas, `db_query.py ... 1` returns). DB side blind.
- contamination_disclosure: none.

### 1. What the user expresses

Marcus Albright (son, representative) opens: "I'd like to pay my mother's December Medicare coinsurance by bank draft from my checking account today." Object = Denise Albright's December coinsurance; method = bank draft (ACH); no figure. DOB 1960-06-10 + phone 717-555-0168 verify (2 matches). Conditionally: Conestoga Mutual Medigap, Plan K -> Plan N from December 10; Dec 1 overnight at home, bed not held; Dec 3 hospital, back Dec 5, room held; Dec 6 hospital overnight, back the 7th, bed not held; authorises "whatever the business office needs to do on her account so that December can be paid". He runs the bank draft himself.

### 2. Act / wait / refuse

Act now: rate-year correction -> reduction for reversed covered days -> hand over the bank draft. Grounds:
- `coinsurance_bank_draft_payments`: "A bank-draft payment toward a resident coinsurance charge is not taken until the records carry, against that charge, a reduction for every uncertified-day reversal posted against its booked-days entry after the charge itself was posted and taking back days that take a resident share above nothing under the split in effect on them."
- Ledger: resident charge `4cf64f04` (posted 2026-01-02, 27 days at 217.00, 542.50) on Dec block `87943da2`; uncertified reversal `6374f879` (2025-12-04..12-12, 7 days) posted 2026-01-21, after the charge; the only `uncertified_day` adjustment (`6ff86bff`, 1047.50) names the carrier charge `be35f9a1`, not the resident charge. Days 12-04..12-09 of the span take the earlier share 50% (>0) -> state does not hold.
- `reversed_day_charge_reductions`: "A reduction for reversed covered days on a resident coinsurance charge is fixed only after the records carry a rate-year correction against that charge whenever the charge's recorded daily rate is above the rate of the year in which its days were furnished and its days take a resident share above nothing under the split in effect on them." Charge records 217.00 for 2025 days (2025 rate 209.50, `daily_coinsurance_rate_schedule`); no `rate_year_correction` adjustment exists -> state does not hold.
- No returned payments -> bank draft accepted method. Coverage `484a162d` `active`.

### 3. Object and keys

Coverage `484a162d-1724-4844-835e-7ee220ca71ec` (Full-Coinsurance Medigap, plan N, resident share 0%, supplemental_effective_date 2025-12-10). Latest days_21_100 entry `87943da2-e26f-4f81-b2e3-5701892570f7` (2025-12, 29 booked, benefit 38-66). Resident charge `4cf64f04-8217-4237-9fdc-5e203089df9f`. Block before = `c0aa2b97` (last benefit day 37), its resident charge `b1e459e7` (17 days, 209.50, 1780.75). Reversals on `87943da2`: LOA 12-01 (posted 01-02), hospital 12-06 (posted 01-02), uncertified 12-04..12-12 (7, posted 01-21, `6374f879`). Bed-hold leave booked for 2025-12: `a9eafb05` 12-03..12-04 (2 held days, reservation `427e8b1d`); reservations `9fdb0b25` (Dec 1 therapeutic leave) and `c33c633a` (Dec 6) declined, no held days. Excluded: carrier charge `be35f9a1` and its adjustment; Nov rows (paid).

### 4. Scored figures

Record test (all five computation docs): one days_21_100 entry in 2025-12; one block ending at benefit day 37; one bed-hold leave, none taken back; one reversal per reason, no booking error; LOA 12-01 / hospital 12-06 cover no held night (12-03/04), 1 day each; uncertified span 12-04..12-12 = 9 calendar days, less held 12-04 and hospital 12-06 = 7 = its count; supplemental date 12-10 after 12-01 and block before's resident charge 1780.75 = 17 x 209.50 x 50% exactly; standing charge day count 27 = 29 - (LOA 1 + hospital 1) posted on or before 2026-01-02; last service date 2025. Bank draft extra: no hospital/LOA reversal posted after 01-02; open balance > 0 (checked at each step). Passes.

(a) Rate-year correction (`rate_year_correction_computation` + factors): days the charge prices = 27; calendar days before 12-10 = 12-01..12-09 = 9; off: uncertified (baseline bullet, only if posted on or before the charge date) -> posted 01-21, 0; bed-hold factor 12-03, 12-04 -> 2; hospital factor (posted on or before charge date) 12-06 -> 1; LOA factor (posted on or before) 12-01 -> 1. Before = **5**, other = **22**. Earlier share factor -> **50%**; tier share 0%. Year-of-service factor ("The Year-of-Service Rate Used in Rate-Year Corrections"): 2025 -> **209.50** (baseline 204.00). First figure 217.00 x (5 x 50) = 54250 -> 542.50; second 209.50 x 250 = 52375 -> 523.75; correction = **18.75** (<= open balance 542.50). Args: charge `4cf64f04`, days_entry `87943da2`, service_month 2025-12, amount 18.75.

(b) Reduction for reversed covered days (`reversed_day_reduction_computation` + factors): lapse `6374f879`, day count 7; span part before 12-10 = 12-04..12-09 = 6; off: LOA overlap (baseline clause 6) 0; bed-hold overlap factor: held 12-04 inside span -> 1; hospital overlap factor: 12-06 -> 1. Before = **4**, other = **3**. Daily rate factor ("Daily Rate Applied When Reducing ...") : rate-year correction on record + 2025 -> **209.50** (baseline: the recorded 217.00). Earlier share 50%. Sum 209.50 x 200 = 41900 -> **419.00** (<= open balance 523.75). Args: charge `4cf64f04`, reversal_entry_id `6374f879`, amount 419.00.

(c) Bank draft (`bank_draft_amount_computation` + factors): covered days = 29 - (1 + 1 + 7) = 20; before 12-10: 9 calendar days, off: held 2 (12-03, 04), hospital 1 (12-06), LOA factor 1 (12-01), uncertified factor: part 12-04..12-09 = 6 less held 12-04 and hospital 12-06 = 4 -> before = **1** (12-02), other = 19 at 0%. Rate 209.50, earlier share 50%. 209.50 x 50 = 10475 -> 104.75; less net payments 0 -> **104.75**; open balance after (a)(b) = 542.50 - 18.75 - 419.00 = 104.75 -> not above -> taken. Args: medicare_coverage_id `484a162d`, charge_entry_id `4cf64f04`, amount 104.75.

Fall-backs (computation documents alone): rate-year correction = 217 x 900 - 204 x 900 -> 1953.00 - 1836.00 = **117.00**; reduction = 217.00 x 6 x 100 = 1302.00 capped at open balance -> **523.75** (after 18.75) or 542.50; bank draft = 217.00 x 9 x 100 -> 1953.00 > open balance -> not taken. All differ from 18.75 / 419.00 / 104.75.

Factor findability: `to_date` 2025-12-31 -> year-of-service docs; 217.00 recorded on a 2025 block -> rate-year docs and `secondary_denials_and_qmb_writeoffs` ("A charge priced at the wrong year's rate is corrected with the reason 'rate-year correction'"); supplemental_effective_date + baseline "earlier share of 100 percent" + Nov charge 1780.75 = half of 3561.50 -> earlier-share docs; bedhold ledger `bedhold_day_booked` 12-03..04 -> bed-hold docs; ledger reasons `hospital_day`, `leave_of_absence_day`, `uncertified_day` -> the matching docs. Observation (to Step 3b): the record-test sentence in each computation document names the block-before share test, the bed-hold leave and the reversals, pre-signalling factor existence.

### 5. Tool sequence

find_customers -> verify_customer_identity (DOB, phone) -> find_medicare_coverages -> find_medicare_ledger -> find_bedhold_reservations / find_bedhold_ledger -> KB -> unlock + call `correct_coinsurance_rate_feac0074` (18.75) [agent] -> unlock + call `reduce_coinsurance_for_reversed_days_0894f336` (419.00) [agent] -> unlock_user_discoverable_tool `pay_coinsurance_by_bank_draft_32bb229d` -> user pays 104.75 on `4cf64f04` [user]. Terminal: resident charge open balance 0.

### 6. Problem tree

- P0 (root, customer write): bank draft on the resident charge.
- P1: reduction for the uncertified reversal posted after the charge. Edge P0 -> P1 from the bank-draft sentence (state form: "a reduction for every uncertified-day reversal ... posted ... after the charge"); query shows reversal `6374f879` posted 01-21 > 01-02 and no reduction on `4cf64f04`; `reversed_day_charge_reductions` describes in the same words the write ("applies to the resident's original coinsurance charge ... for the days of the uncertified-day reversal posted against that block's booked-days entry after the charge was posted"). **state-derived**.
- P2: rate-year correction. Edge P1 -> P2 from the reduction sentence (state form: "records carry a rate-year correction against that charge whenever the charge's recorded daily rate is above the rate of the year"); query: 217.00 on 2025 days, no correction; `rate_year_corrections` describes the write ("takes back what a resident's original coinsurance charge ... billed above that year's rate ... posted against the charge with the reason 'rate-year correction'"). **state-derived**.
- P2 has no prerequisite sentence. Order P2 -> P1 -> P0. Also the reduction's daily-rate factor reads "when the records carry a rate-year correction against the charge" — consistent with the order.

Counter-proofs: "only the bank draft" is barred by the bank-draft sentence; bank draft of 542.50 (open balance) is excluded because the computation gives 104.75 and the charge must first carry the reduction. Reduction before correction is barred by the reduction sentence and would also price at 217.00 (factor "otherwise the daily rate the charge records") -> 434.00 instead of 419.00. Hospital/LOA reversals posted 01-02 (same day as the charge) count for the rate-year correction ("on or before"). Uncertified days before the charge date do not enter the rate-year correction because the reversal was posted after the charge. Declined leaves (Dec 1, Dec 6) book no held nights.

## gt_comparison

Reveal: 2026-10-22T18:16Z, after the blind_answer above was on disk (sha256 at freeze `2f6e21e56f15c337a3d65f0ec050d20effcb6c4093f2e8a5d84f6f8ee70cec0f`). Read: `medicare.extended.yaml` (`203ecd58…`), `task_tools.py` (`91fc2fae…`), `tasks/1.json` (evaluation_criteria, computations, prerequisite_closure). Snapshot 2026-10-22T18:14 all green (see task0).

| Item | Blind | Source / GT | Same? |
|---|---|---|---|
| Write 1 | `correct_coinsurance_rate_feac0074`(484a162d, 4cf64f04, 87943da2, 2025-12, 18.75) | identical | same |
| Write 2 | `reduce_coinsurance_for_reversed_days_0894f336`(484a162d, 4cf64f04, 6374f879, 419.00) | identical | same |
| Write 3 (user) | `pay_coinsurance_by_bank_draft_32bb229d`(484a162d, 4cf64f04, 104.75) | identical | same |
| Tree | bank draft -> reduction -> rate-year correction, both hops state-derived | `prerequisite_closure`: bank_draft -> reversed_day_reduction (state_gate, form state) -> resident_rate_year_correction (value_input, form state); policy_source sentences verbatim as quoted in blind item 2 | same |
| Factor tiers | correction: rate 209.50, share 50, held 2, hospital 1, LOA 1; reduction: rate 209.50, share 50, held overlap 1, hospital overlap 1; bank draft: rate 209.50, share 50, held 2, hospital 1, LOA 1, uncertified 4 | factor_trace identical | same |
| Fall-backs | 117.00 / 523.75 / not taken | `baseline_result` 117.00 / 523.75 / 0.00 | same (bank draft: both readings differ from 104.75) |

Cross-product: f_held_nights / f_held_in_lapse read the Bed-Hold and Leave Reservations ledger (held days 2025-12-03..04, `a9eafb05`; declined reservations Dec 1 and Dec 6 book none) — **conditional** on the unpublished bedhold corpus (later re-judge).

Verdict: **PASS** (KB-RUNTIME). Solution unique and equal to GT. Note for Step 3b: the solver can read the scored reduction amount 419.00 and this task's world shape off a worked example (see policy_kb task1 E1); it does not change the solution, so it is recorded as KB-EXPLICIT, not here.

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
- Cross-product rows checked (task1, Denise Albright), each against the published bedhold documents as of its posting date:
  1. Reservation `9fdb0b25` — **OK**. Medicare Skilled Stay Therapeutic Leave Bed Hold (home visit). Declined, planned departure 2025-12-01 14:00, return 2025-12-02, end_date 2025-12-01, held 0, balance 0. It books no held day, consistent with the Medicare leave-of-absence reversal of 2025-12-01.
  2. Notice `96932048` — **OK**. 2025-12-01 13:30, at the time of the planned transfer.
  3. Election `c5eae7c5` — **OK**. Decline, representative, effective 2025-12-01.
  4. Reservation `427e8b1d` — **OK**. Medicare Skilled Stay Hospital Leave Bed Hold. Returned, emergency departure 2025-12-03 20:40, return 2025-12-05, end_date 2025-12-04, held 2, private_hold_start 2025-12-03, balance 768.00. Opened after `9fdb0b25` was declined.
  5. Notice `35b15762` — **OK**. 2025-12-03 22:10, within 24 hours.
  6. Election `c083ef2b` — **OK**. Hold, representative, created 2025-12-04 08:30 (inside 24 hours of the notice), effective 2025-12-03.
  7. Held-days entry `a9eafb05` — **OK**. resident_private, 2025-12, 2025-12-03..04, 2 days, booked 2025-12-05 when the leave ended. No reversal is owed.
  8. Charge `68614af0` — **OK**. 2026-01-03, names `a9eafb05`, 2 x 384.00 = 768.00 (same basis as task0).
  9. Reservation `c33c633a` — **OK**. Medicare Skilled Stay Hospital Leave Bed Hold. Declined, 2025-12-06 21:15, return 2025-12-07, end_date 2025-12-06, held 0. Opened after `427e8b1d` was returned.
  10. Notice `db64dc56` — **OK**. 2025-12-06 22:30, within 24 hours.
  11. Election `752ad5cb` — **OK**. Decline, effective 2025-12-06.
- Conditional items settled: the held-night tiers rest on rows the published bedhold corpus produces exactly. They are f_held_nights (2 nights, 12-03..04) for the rate-year correction and the bank draft, and f_held_in_lapse (1 night, 12-04, inside the 12-04..12-12 lapse) for the reduction. **Settled — no change** to 18.75 / 419.00 / 104.75.
- Owed-at-once writes that could move a scored read: none. There is no bedhold reversal, reduction or booking owed, and the other products have no holdings. Within medicare, the tree's three writes are the only ones owed: the carrier's uncertified-day adjustment of 1047.50 = 209.50 x (4 x 50 + 3 x 100) / 100 is already consistent, and no secondary-share correction is owed.

**PASS** (KB-RUNTIME), with no conditional items remaining.
