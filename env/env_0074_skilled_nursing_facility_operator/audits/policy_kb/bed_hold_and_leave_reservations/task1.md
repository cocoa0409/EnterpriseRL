# Policy-KB bijection audit — bed_hold_and_leave_reservations / task 1

## revision_1

Scope: bedhold_ext_hospital_opening_charge (ho_*), bedhold_ext_hospital_closing_charge (hc_*), shared overwrite and base charter (as task 0); tools post_hospital_opening_charge_991dca72, sign_hospital_closing_charge_702d4c7f. Same corpus hash and gate snapshot as task 0.

## source_to_kb

- Overwrite / retired surface: as task 0 (charge_basis_c14d12e1) — PASS.
- Entry definitions: ho_base (b) / ho_hub (opening resident-private entry of an MA hospital hold with more than one resident-private entry, beginning on the recorded first privately held day; "business office posts … once the entry is booked"); hc_base 1 / hc_hub (closing entry, "and whose leave has ended", latest last day, not the opening entry).
- Baselines: ho_base (a)(c)(d)(e), hc_base 1–6 carry the baseline rule complete with the 12 rates and 2026-07-01; fall-backs 10,900.00 / 7,412.00 (= GT baseline_result).
- Combination: hc_base 7 verbatim generic sentence. ho_base (f): source "the days not charged at the start of the entry, as many as the larger of those held before the notice and those payer-covered, are its first days" rendered as "where days at the start go uncharged on more than one ground, as many as the larger of the counts on each ground, never their total" — in the ho domain the only start grounds are the notice (ho_base (e)) and the payer-covered days (ho_ma "The payer-covered days are the entry's first days"), so the two entail the same max(); "never their total" restates "the larger". Equivalent at entailment (see src S3 for the source's naming of a factor quantity in the assembly sentence).
- Factor ladders: ho/hc rate (3 rows, ho_rate Q&A, hc_rate table), ext (ho_ext prose + boundaries, hc_ext table), diet (ho_diet table, hc_diet Q&A), iso (ho_iso bullets incl. semi-private derivation, hc_iso table), hc_return_day (hc_ret), hc_after_hold_end (hc_after, four cases + clamp), ho_reserved_days (ho_ma: within limit → limit − days from departure to entry start, capped at entry days; begins after → none; tier with no per-hospitalization days → none; per-tier table 15/0/0/0/0/0; "however the entry was booked"). Every tier carried, thresholds in figures.
- Prerequisite hc→ho, form state: "The hospital closing charge is worked out only after the opening entry of the hold carries its bed-hold charge." verbatim in hc_hub_1cd655a6 §"When the charge is worked out" (+ same-form record restatement). Basis: ho_hub definition and "The business office posts the hospital opening charge once the entry is booked." + ledger (no charge naming 5eece24c). Connective/strength/form match; carried by no other policy's document.
- Tool contracts: hub tables = task_tools.py docstrings/bodies; owners match (post agent, sign user).

## kb_to_source
As task 0: no added obligation, step or confirmation; no cross-problem guidance; no world state as fact. Example sweep: payer_reserved_day_limits' hypothetical row "12 per hospitalization | 9 | 3" shares the figures 12 and 3 with this world (12 payer days booked, 3 payer-covered days on the opening entry) in different roles under a differently stated limit (12 vs the real 15) — labelled "hypothetical limits, for illustration only"; no scored value (7,715.40 / 4,059.90 / 22 / 13) appears. Observation only.

## bijection_verdict
**PASS.** Conditional C1 as task 0 (task-1 values hold for any rate-change notice days ≥ 44).

## dependency_form
- hc_hub carries the sentence; ho_* documents never mention the closing charge; no tool name besides each hub's own; no route/aggregation; titles general ("Medical Assistance Hospital Leave: The Closing Private Bed-Hold Charge", "Hospital Opening Charge on a Medical Assistance Reserved Bed Extension").
- ho_base (f)'s "more than one ground" phrase and the generic combination sentence are source assembly (src S3), not rendering additions.
- Blind hop state-derived.
**PASS.**

## revision_2 (2026-10-23, re-audit round 2)

Entry: RENDER.log tail "RENDER round 2: DOCS OK"; kb_snapshot 2026-10-23T06:25:36 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged (967ee5a3…0955 / 8bedf6a7…65b7); extended yaml f9fc40ef…b2de (was 4718b6c8…); task_tools unchanged 788ee1d3…; docs/bedhold 50 files, tree 24cc3f6db0001c26 (was 88bc62df190873bb).

### source_to_kb
- S1 (closed): every *_isolation_rate ladder now reads "an isolation placement recorded no later than the departure date … otherwise (no isolation placement, one recorded after the departure date, or the room held is not the agreement's room)", rule "the agreement's last room change, the center's infection-control move, being dated no later than the departure date", compute *_agr_move = CFIELD private last_room_change_date with DAYS(move, dep) >= 0 and a None move → own tier. All five *_iso docs carry the rule sentence verbatim, the tiered table/bullets with the date condition, the "not on the agreement" fallback and an on-the-day/day-after boundary — every tier, equal to compute.
- S2 (closed): every *_rate_binding ladder/rule row 1 now adds "or on or after the schedule date"; compute unchanged (DAYS(schedule, notice)+N > 0). All five *_rate docs carry row 1 with "or on or after 2026-07-01"; the new D-case list is correct for all four cases (D−1 days before → start 2026-07-02; exactly D → 2026-07-01; on/after → delivery + D; none → all prior).
- Everything else from revision_1 re-checked on the diff: overwrite/retired surface, baselines (fall-backs unchanged), all other ladders, the prerequisite sentence(s) in their blocked hub only, tool contracts — unchanged and intact (tc_after table still carries all four cases; only its illustration narrowed to release cases).

### kb_to_source
Reworked illustrations verified arithmetically (hc/hs_after return-12th → 13 days; ho_base 17–31 July → 15 current days, 22–30 June no notice → 0 charged; ho_ma 12/16 March → 6/2; to_base 18–30 June notice 20 June → 11 charged at 466.00 = 5,126.00, 19–31 July notice 21 July → 11 at 482.00 = 5,302.00; payer limits 15−10 = 5, 30−28 = 2; payments 1,194.00 → 694.00 / 554.00; charge_basis illustration now figure-free). No added obligation or step; no world state as fact. No example or table equals a scored value (grep of 9,118.20 / 6,663.30 / 4,720.20 / 7,715.40 / 4,059.90 / 350.70 / 312.30 / 324.20 / fall-backs / 4,559.10 → none) or mirrors a task world; the round-1 observations (payer-limit row 12/9/3; hs_rate's 60-day example) are gone — the payer table now uses the real 15/30 limits with counts (10, 15, 28) unlike task 1's 12.

### bijection_verdict
**PASS** — no regression; S1/S2 closed in source and carried losslessly.

### dependency_form
Unchanged surfaces re-checked: prerequisite sentence(s) verbatim on the blocked hub only; no other tool name, route or aggregation; new "Date boundary" paragraphs and D-cases are within-factor rules, name no other factor or document; titles unchanged. S3 (generic combination sentence in the computation docs) decided as placement; S4 BLUEPRINT-KNOWN. **PASS.**

## revision_3 (2026-10-23, round 3 — cross-product re-judge)

Entry: all seven corpora published (docs/private 69 files, docs/trust present). kb_snapshot 2026-10-23T10:12:51 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes unchanged since revision_2: runtime views 967ee5a3…0955 / 8bedf6a7…65b7; extended yaml f9fc40ef…b2de; task_tools 788ee1d3…; docs/bedhold tree 24cc3f6db0001c26 (no bedhold document changed). Scratch: /tmp/erl0074_kbaudit_bedhold/r3/.

### Conditionals settled
C1 and C2 are settled as in task 0's revision_3. The values hold with N = 60 (rate start 08-31 + 60 = 10-30, after both entries).

### Cross-product seeded rows read by gold steps (find_private_agreements, find_private_ledger, find_medicaid_cases, find_medicaid_ledger, find_medicaid_requests)
Private agreement f19f9229: Private LTC, payer_converted 06-01 → medicaid_pending (conversion date = the requested eligibility date 06-01, per payer_source_conversion clause 1); signed 01-28 / admitted 02-02; rate notice 08-31; move 04-14 (center-directed, isolation); account 0.00; deposit 0.00. Status: **see S5**.

| Row | What it is | Verdict |
|---|---|---|
| 5e102549 02-02 | deposit 11,520.00 = 30 × 384.00 | OK |
| 70a2dcff 02-02 / 90e6bc33 | Feb first-month partial 27 × 384 = 10,368.00 / payment | OK |
| c7ded083 02-25 / ce626de9 | Mar 11,904.00 / payment 03-10 | OK |
| 7e924e31 03-25 / 8dae43a3 | Apr 11,520.00 / payment 04-10 | OK |
| a0df6fdf 04-14 | room-change proration 17 × 384 = 6,528.00 | OK (come-off tier = the charge's tier; preceding schedule) |
| 6069b4a3 04-14 | isolation span 04-14..30, 17 × 384 = 6,528.00 | OK |
| 62e9f29a 04-25 / 356a96cf | May 11,904.00 isolation / payment | OK |
| 1451f392 05-25 | Jun 30 × 384 = 11,520.00 isolation | OK |
| 88e557d6 06-05 | payer-conversion credit 30 × 384 = 11,520.00 from 06-01 | OK. On 06-05 Harold held no hospital bed-hold reservation, so the extended computation applies (tier = isolation billing tier SP-LTC; schedule for a June span = preceding): 11,520.00. The base rule gives the same figure. The late-notice credit on this charge works out to zero (billed-rate gap negative), so none is owed. |
| d0098f84 06-25 | deposit refunded 11,520.00 to representative | OK (within 30 days of conversion; open balance 0; no deposit may be held for Medicaid pending) |

Medicaid case 768fa88d: Standard Patient Pay, eligible; application 06-05, requested and eligibility start 06-01 (within 3 retroactive months, first of the month); decision 08-03; patient pay 1,476.10 = 1,724.00 − 45.00 PNA − 202.90 premiums; effective 06-01; renewal 2027-06-01 (12 months); patient_pay_balance 1,476.10 = the open November charge; pending balance 0.00 (both accruals settled). **OK.** On the tier, see O2.
Request 9c07edc3: application signature by the resident 06-03, before submission 06-05. **OK.**

| Row | What it is | Verdict |
|---|---|---|
| 9d1ead6e 06-05 / b033790b 06-10 | Jun estimate 1,476.10 / payment | OK (pending; estimate formula; due the 10th) |
| 7273d1e4 06-30 | Jun accrual 30 × 384.00 = 11,520.00 | OK ("room and board the resident would owe privately": the isolation rate he was billed; no leave in June) |
| 22fb808b 07-01 / b7897ea2 07-10 | Jul estimate / payment | OK |
| 37e40b5c 07-31 | Jul accrual 31 × 384.00 = 11,904.00 | OK (no rate notice yet: the earlier rate applies) |
| 8a186214 08-01 / 6851909c 08-10 | Aug estimate / payment | OK |
| 3f96b9a0, e03a6af1 08-03 | both accruals settle approved_ma_covered | OK (days on or after the 06-01 start; no penalty period) |
| 06ab4b82 09-01 / 37d32583 09-10 | Sep actual_notice 1,476.10 / payment | OK ("Patient pay is unchanged for a month with Medicaid reserved bed days"; see O3) |
| e604285d 10-01 / 35855ce3 10-09 | Oct actual_notice / payment | OK |
| 15eb95c2 11-01 | Nov actual_notice 1,476.10, open | OK (due 11-10) |
| reconciliation | latest estimated month Aug: no accrual → not priced day by day → 31 × 286.47 = 8,880.57 > 1,476.10 → reduction 0 | no row owed, OK |
| actual-month review (October) | resident holds no trust account and no Medicare episode → outside its scope → base ceiling: days in centre × 286.47 > 1,476.10 | no row owed, OK |

S5 (seed vs published lifecycle; load-bearing; plausible): one_open_agreement_per_resident_05f584ee says "A converted agreement with no private balance or deposit left is closed", and agreement_closing_rule_0e7f3db4 says "a converted agreement closes once no private balance or deposit is left on it". Since the 06-25 deposit refund, agreement f19f9229 has carried account 0.00 and deposit 0.00, yet it is seeded payer_converted at 2026-11-05. Task 1's isolation and rate factors read the agreement only in status active, notice period or converted. Closed, the agreement would not be read: rate row 3 puts every day on the current schedule, and iso gives the room's own tier Private LTC. The values would then be opening 22 × (436 × 0.95 − 14.10) = 8,802.20 and closing 13 × (436 × 0.85 − 14.10) = 4,634.50, instead of 7,715.40 / 4,059.90. The charter's transition (payer_converted → closed, by agent) makes the unclosed state producible. The published documents state closing as a consequence, not a step left pending. No published tool closes an agreement, so a solver cannot flip it mid-conversation.

O2 (observation): patient_pay_deductions_schedule gives the Standard tier's entry as "no spouse and no dependents in the community". Harold's representative is his wife, who handles his bills. case_tier_rates_renewal_and_closing places the tier by the allowance on the notice ("none of these → Standard"), and the case records a community spouse allowance of 0.00. The seed follows the placement rule. Not load-bearing for bed-hold.
O3 (observation): in September Harold spent no day in the centre (5 MA-reserved days, then 25 privately held days). The base ceiling ("days in the center times the Medicaid daily rate") and the reserved-days clause ("unchanged") pull apart for such a month. The seed takes "unchanged", and the extended actual-month review, which takes privately held days out, does not cover this resident. No bed-hold read depends on it.

### Owed-at-once writes
As task 0: no tool of medicaid, private, medicare, trust, ancillary or therapy writes bedhold_ledger, bedhold_reservations or the agreement status, dates, tier, isolation flag or room-change date. The medicaid reduction tools (cost-of-care, true-up) owe nothing in this world and touch only medicaid tables. Agreement closing (S5) has no tool. **No scored read can move.**

### Verdict
bijection **PASS**, dependency_form **PASS**. New source/seed item: S5.

## revision_4 (2026-10-23, round 4)

Entry: RENDER.log tail "RENDER round 3: DOCS OK"; kb_snapshot (round 4) — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged; extended yaml f9fc40ef…b2de and task_tools 788ee1d3… unchanged; docs/bedhold tree 24cc3f6db0001c26 unchanged; docs/private and docs/medicaid identical to the round-3 dumps. tasks/{0,1}.json rewritten 2026-10-23 10:43 (seed rework, round 8). Scratch /tmp/erl0074_kbaudit_bedhold/r4/.

### S5 — closed
Seed diff against round 3: the May payment 356a96cf is removed, so the May charge 62e9f29a (11,904.00, due 05-10) was unpaid at conversion. The deposit disposition d0098f84 2026-06-25 is now applied_to_balance 11,520.00, with a matching payment 8aeeb18e (deposit_application / security_deposit, 11,520.00) naming 62e9f29a. Agreement account_balance is 384.00, deposit 0.00, status payer_converted.
Checked against docs/private:
- security_deposit_rule: "the deposit is applied to the agreement's open balance and any remainder is refunded". Open balance at 06-25 was 11,904.00 → 11,520.00 applied, nothing refunded, as posted ("A deposit applied to the balance is posted as a payment from the security deposit") within the 30 days after the 06-01 conversion. Payment ≤ open balance; oldest month first. OK.
- one_open_agreement / agreement_closing_rule: "A converted agreement stays open while any private charge, credit or deposit remains on it". 384.00 remains, so payer_converted is the status the docs produce, and S5 is closed. The agreement read by the bed-hold factors, and so the gold (7,715.40 / 4,059.90), is unchanged.
- late_charge_rule: the May month becomes past due only after 30 grace days from 05-10, i.e. later than 06-09. The stay was converted from 06-01 (recorded 06-05), and "Nothing is assessed while the stay is converted to another payer source", so no late-charge row is owed. OK.
- collection referral and nonpayment discharge notice are permissions ("only when …"), not owed writes. No published tool performs either, and neither would change a field the bed-hold factors read. Observation only.
- Not applicable: additional deposit (the agreement records a conversion); resumption deposit (not active again).

The other 12 private rows and every Medicaid row (case, request, 15 ledger rows) are byte-identical to round 3; the revision_3 verdicts stand.

### Owed-at-once writes
Unchanged: none can move a scored read.

### Verdict
bijection PASS, dependency_form PASS, no regression. No new item.
