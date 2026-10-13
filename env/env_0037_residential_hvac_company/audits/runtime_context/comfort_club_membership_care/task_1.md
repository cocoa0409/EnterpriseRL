# Runtime-context blind audit — comfort_club_membership_care / task 1

## blind_answer

- Freeze time: 2026-10-05T19:10Z (written to disk before any source-layer or GT material was opened).
- Auditor: independent erl-kb-doc-policy-audit run (not the renderer, not the policy-side auditor).
- Scope: difficulty `comfort_club_membership_care`, product `plan`, task index 1.
- Visible materials used: system background (`background` key of blueprint.yaml only); `/tmp/erl37/kbviews/comfort_club_membership_care/task_1.runtime.json` (sha256 bcf4fca0…c4ff, matches views.sha256); published plan KB title/content `/tmp/erl37/kbviews/docs_visible/plan/*.json` (64 docs; 7-product hash e8cdd6997a624be025c5d73e5a36acfd36a1f07ae43cba307e8324f3f0f86282, recomputed); runtime tool schemas; tool-shaped calls `dbq.py comfort_club_membership_care 1 call …`.
- Explicitly not read: `*.extended.yaml`, `task_tools.py`, task JSON, raw `initial_state`, docs hidden meta, render plan, worklogs, `audits/`, verification scripts. No recursive grep over `env/`.
- DB side is blind (tool-shaped only).

### 1. What the user expresses; simulator mode
"My Comfort Club lapsed at the end of August… I want to pay this year's membership today, by card over the phone." Identity: phone 6145551736 + address 1863 Bethel Rd. Authorisation: "go ahead with whatever has to be recorded on Harbison's side to put the membership back in order… if they mention fees you say that's fine, put them on the account." Payment is a user-owned tool the agent hands over; he pays "with the reference and the amount exactly as the representative gives them", method card by phone. Passive simulator; tier, ductless unit and missed visits disclosed only if asked.

### 2. Act now / wait / refuse — grounds
Act now. `find_plan_agreements`: Comfort Club Gold, status `lapsed`, annual, term 2025-09-01 to 2026-08-31, auto_renew False, consecutive_terms 7, enrolled 2019-09-01, locked_annual_rate 229.00, systems_covered 2, dues_balance 0.00. KB "Reinstatement Grace Window": reinstatement allowed when the date of handling is no later than term end + renewal grace days; "Term, Renewal and Reinstatement Schedule": Gold grace 45 -> last day 2026-10-15; 2026-10-05 inside. "One Agreement per Customer" cl.3: a lapsed agreement inside grace "is reinstated rather than enrolled again". Gold carries a price lock (schedule: "Yes").

### 3. Objects and correlation keys
- agreement de6bb8a8-2723-4a9b-84e8-1101ec267790; customer a8e9ac1a-1ff4-48b3-a508-d713666ef209.
- Lapsed term = term_start 2025-09-01; forfeits charged to it: d77e143d late_cancel_forfeit cooling 2026-06-18 (one). Excluded: no_show_forfeit 2025-06-10 (term 2024-09-01; already carries missed_appointment_fee 25.00 posted 2025-06-10).
- Missed-visit fees on ledger: only c471462f (2025-06-10). No fee for the 2026-06-18 forfeit.
- Install contract c99c8845 signed 2026-03-10; member_install_credit 250.00 posted 2026-03-12; mfr_registration 12 years. Protection: active Harbison 2-Year Workmanship Warranty, purchase_channel with_installation. Service call e7a60676 (2025-07-14): repair_parts 96.00 + repair_labor 153.00.

### 4. Scored parameters (date of handling 2026-10-05; lapsed term's last day 2026-08-31 -> 35 days)
**A. Reinstatement fee** ("Reinstatement Fee: Amount Charged" + factors). Tier fee Gold 25.00.
- Lapse length (factor "Reinstatement Fee and the Length of the Lapse"): 35 > 30 -> 25.00 × 35 / 30 = 29.17 -> rounded up to whole dollar 30.00.
- Tenure share (factor "Tenure Share…"): 7 terms at lapse, no reinstatement fee anywhere on ledger -> 0.5 -> 15.00.
- Forfeit surcharge (factor "Reinstatement Surcharge for Forfeited Tune-Ups"): exactly one forfeit in lapsed term -> +5.00.
- Installation courtesy (factor "Reinstatement Courtesy … Harbison Installation"): credit posted 2026-03-12, 6 whole months back -> 10.00.
- Protection courtesy (factor "Reinstatement Courtesy … Protection Contract"): active contract of another tier -> 5.00.
- Fee = 15.00 + 5.00 − 10.00 − 5.00 = **5.00**. Fall-back (computation doc only): 25.00.

**B. Locked rate** ("Locked Rate of a Reinstated Comfort Club Term" + factors). Current Gold first-system rate 249.00.
- Retained rate (factor "Price Lock Retention After a Lapse"): 35 days > 15; term count incl. reinstated term 8 ≥ 6 -> 229.00 + (249.00 − 229.00)/2 = 239.00.
- Maintenance surcharge (factor "Locked-Rate Surcharge for Missed Maintenance"): completed cooling/heating tune-ups within 12 months: heating 2025-10-16 only -> exactly one -> +5.00.
- Registration credit (factor "Registered Manufacturer Parts Warranties"): 12 years -> 6.00.
- Protection credit (factor "Locked-Rate Credit … Active Protection Contract"): other tier -> 3.00.
- Locked = 239.00 + 5.00 − 6.00 − 3.00 = **235.00** (≤ 249.00). Fall-back: 249.00.

**C. Missed-visit fee** for the 2026-06-18 forfeit ("Comfort Club Missed-Visit Fee Amount" + factors). Gold missed-appointment fee 25.00.
- Repeat-miss (factor "Missed-Visit Fee for Repeat Misses"): forfeits within 24 months: 2025-06-10, 2026-06-18 -> two -> 35.00.
- Tenure cap (factor "Missed-Visit Fee Cap by Membership Tenure"): enrolled 2019-09-01 -> 85 whole months ≥ 84 -> cap 30.00 -> 30.00.
- Attendance (factor "Missed-Visit Fee Reduction for Kept Tune-Ups"): completed cooling/heating tune-ups within 24 months: 2024-10-09, 2025-10-16 -> two -> −3.00 -> 27.00.
- Forfeit treatment (factor "Treatment of Late Cancellations"): most recent forfeit is a late cancellation, count ≥ 5 -> half, rounded down to whole dollar -> 13.50 -> **13.00**. Billing period = month posted **2026-10**. Fall-back: 25.00.

**D. Reinstated-term dues** ("Reinstated-Term Dues: Gross Dues, Discount and Amount Billed" + factors), after A–C are on record:
- First-system rate (factor "Price Lock and the First-System Rate of a Reinstated Term"): locked rate on agreement 235.00 (as just decided) < 249.00; 85 months ≥ 60 -> 235.00.
- Additional-system share (factor "Additional-System Rate for Members with a Recent Harbison Installation"): contract signed 2026-03-10, <12 months -> 0.6 -> 169.00 × 0.6 = 101.40 for the one system beyond the first.
- Gross = 336.40.
- Loyalty (factor "Loyalty Discount … and the Appointment Record"): 8 terms ≥ 7, but a missed-appointment fee charge is on the ledger dated 2026-10-05 (just posted for the lapsed-term forfeit) -> enhanced condition fails -> tier's 5%.
- Trouble-free (factor "Trouble-Free Discount"): repair parts + labor billed within 24 months = 249.00 < 500.00 -> 1.5%.
- Protection bundle (factor "Protection Bundle Discount"): active contract bought with installation -> 2%.
- Combined 8.5% once: 336.40 × 0.915 = 307.81.
- Gap (factor "Reinstated-Term Dues by Reinstatement Gap"): gap 35 > 30 and ≥ 5 terms -> × whole month steps from 2026-10-05 ending on/before 2027-08-31 (10) / 12 -> 256.51 (unrounded path also 256.505 -> 256.51).
- Term dues = **256.51**, payment_method card_by_phone. Fall-back: 249.00 + 169.00 = 418.00 whole term.
- Interpretive note: whether the fee posted *on* the date of handling falls "within the 12 months before the date of handling" is not spelled out in the loyalty doc; I read it as inside (the dues ledger doc defines the 12-month window as running back from the date of handling, with the date one year earlier outside), and the blocked-side sentence "The dues of a reinstated term are not fixed until the dues ledger carries a missed-visit fee for every visit forfeited in the lapsed term" only bears weight on that reading. With the other reading the dues would be 242.49. Flagged for comparison.

### 5. Executable sequence, owners, terminal state
verify (agent) -> look-ups (agent) -> `reinstate_lapsed_agreement_6e8e1b28` (agent; fee 5.00) -> `set_reinstated_rate_lock_0c66ac3f` (agent; 235.00) and `post_missed_visit_fee_325d3ccb` (agent; 2026-10, 13.00) in either order -> hand over `pay_reinstated_term_dues_c2f743bd` (owner user; card_by_phone, 256.51). Replay: reinstated term 2026-09-01..2027-08-31, consecutive_terms 8, visits 4; lock 229.00 -> 235.00; fee posted; dues paid, status paid, dues_balance 18.00 (the two fees, billed separately).

### 6. Problem tree derived from the visible materials alone
Problems: P0 = member pays reinstated-term dues (root, user-owned); P1 = reinstatement; P2 = price lock of the reinstated term; P3 = missed-visit fee for the lapsed-term forfeit.
Edges and order: P0 <- P1, P0 <- P2, P0 <- P3; P2 <- P1; P3 <- P1. Order: P1, then P2 and P3 (mutually independent), then P0.
- P0 <- P1 (**state-derived**): "The dues of a reinstated term are fixed only after the agreement shows active status with a term starting the day after the lapsed term ended." Record: status lapsed. "Reinstating a Lapsed Comfort Club Agreement": "Reinstatement returns the agreement to active status, starts the new term on the day after the lapsed term ended" — the write that brings the state about.
- P0 <- P2 (**action-named**): "The dues of a reinstated term are not billed until the price lock for that term has been decided." "Comfort Club Price Lock for a Reinstated Term": "the price lock … is decided once for the reinstated term and written as the agreement's locked rate". Weight: the first-system-rate factor reads "Agreement's locked rate" (229.00 before vs 235.00 after).
- P0 <- P3 (**state-derived**): "The dues of a reinstated term are not fixed until the dues ledger carries a missed-visit fee for every visit forfeited in the lapsed term." Records: forfeit 2026-06-18 in lapsed term, no fee for it. "Comfort Club Missed-Visit Fee on Forfeited Tune-Ups": "a visit recorded as a no-show or a late-cancellation forfeit is charged a missed-visit fee on the agreement's dues ledger". Weight via the loyalty rule's "no missed-appointment fee charge on its dues ledger dated in those 12 months".
- P2 <- P1 (**state-derived**): "The locked rate for a reinstated term is set only once the agreement shows active status with a current term that began the day after the lapsed term ended."
- P3 <- P1 (**state-derived**): "A missed-appointment fee for a visit forfeited in a lapsed term is not posted until the agreement is back in active status with its reinstated term on record."
No hop pre-solved: no blocked-side document names another problem's tool or a route. Observation for 3b: the reinstatement document says "the locked rate and the dues of the reinstated term are decided by the policies that settle them" — a depended-on-side remark that other policies exist for the lock and the dues (judged after reveal).

Counter-proof "do only what he asked" (hand over the payment of 418.00 or any amount on the lapsed agreement): the dues are "fixed only after the agreement shows active status…", "not billed until the price lock … has been decided" and "not fixed until the dues ledger carries a missed-visit fee…" — all three unmet at the opening; excluded by the visible blocked-side sentences.
Closest alternatives excluded: enrol a new agreement (excluded: "reinstated rather than enrolled again"); flat tier reinstatement fee 25.00 (lapse/tenure/courtesy factors); keep locked 229.00 (retention rule: 35 > 15 keep days); whole-term dues (gap > 30 and ≥ 5 terms); charging the 2025-06-10 forfeit again (already carries its fee, not in lapsed term).

## gt_comparison
- Reveal time: 2026-10-05T19:06Z, after the blind answer was frozen (blind-version sha256 of this file: fb01e89cf9cbc9455415c30e9d5c605d6b31ae7a0d0960c1e6cb356d2ac144fe, recorded 2026-10-05T19:05:30Z). Correction of metadata only: the "Freeze time 19:10Z" line in blind_answer is a clerical error; the sha256 recorded at 19:05:30Z is the authoritative freeze point. The blind_answer text is otherwise unchanged.
- Source read: `plan.extended.yaml` (base + `plan_ext_reinstatement_fee`, `plan_ext_reinstated_rate_lock`, `plan_ext_missed_visit_fee`, `plan_ext_reinstated_term_dues`, overwrites, measures), `task_tools.py` (owners), `tasks/1.json` (evaluation_criteria, computations, prerequisite_closure, charter_scope).
- contamination_disclosure: none.

| Item | Blind answer | Source / GT | Same? |
|---|---|---|---|
| Act / wait / refuse | act now: reinstate inside Gold 45-day grace | GT reinstates | same |
| reinstatement_fee | 5.00 (fall-back 25.00) | expected 5.0, baseline 25.0; lapse 35 -> 30.00, share 0.5, +5, −10, −5 | same |
| locked_annual_rate | 235.00 (fall-back 249.00) | expected 235.0, baseline 249.0; retained 239.00, +5, −6, −3 | same |
| missed-visit fee / period | 13.00, 2026-10 (fall-back 25.00) | expected 13.0, billing_period 2026-10 | same |
| term_dues / method | 256.51, card_by_phone (fall-back 418.00) | expected 256.51, baseline 418.0; loyalty 5% because the fee posted today lies within 12 months | same (including the interpretive point flagged in the blind answer) |
| Problem tree | P0<-P1 state, P0<-P2 action-named, P0<-P3 state, P2<-P1 state, P3<-P1 state | five edges with the same forms (the P0<-P2 edge declared `form: action` with a fallback_reason) and identical policy_source sentences; order reinstate -> lock -> fee -> dues | same; my hop marks match the declared forms |
| Tools / owners | 3 agent writes, 1 user payment | same | same |

The blind interpretive point (whether a fee dated on the date of handling is "within the 12 months before the date of handling") resolves to the GT reading. It is the source's own phrase rendered unchanged; the source measure convention ("rolling 12 calendar months ending on the date of handling") agrees with it. Recorded as a policy-side wording note in the policy_kb file, not as a KB defect.

**Verdict: PASS** (no KB-RUNTIME RED).
