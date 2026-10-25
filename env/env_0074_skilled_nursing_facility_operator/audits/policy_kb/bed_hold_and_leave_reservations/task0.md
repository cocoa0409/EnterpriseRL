# Policy-KB bijection audit — bed_hold_and_leave_reservations / task 0

## revision_1

Scope: extended policies bedhold_ext_therapeutic_opening_charge (to_*), bedhold_ext_hospital_stay_charge (hs_*), bedhold_ext_therapeutic_closing_charge (tc_*); their base refs (bedhold_evt_charges, _evt_notice, _evt_day_counting, _hold_end, _agg_payer_day_limits) and the rest of the bedhold base charter; task tools post_therapeutic_opening_charge_78fe9a0a, sign_hospital_stay_charge_56dfc7d9, sign_therapeutic_closing_charge_194aeb06. Corpus: docs/bedhold, 50 files, tree 88bc62df190873bb. Gate snapshot (re-run 2026-10-23T04:57 via kb_snapshot.sh): EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; check_docs bedhold DOCS OK; check_traceability TRACEABILITY OK (0 misses).

## source_to_kb

Mechanical sweep: every rule sentence of the three policies was matched against its prefix's documents (scratch /tmp/erl0074_kbaudit_bedhold/rule_cov.txt); every sentence below 0.9 token overlap was read by hand — all are parameter-name→figure renderings or sentence-split artefacts, except the items judged below.

- Overwrite (all five policies, same superseded_clause / replaced_by): retired clause carried as retired in charge_basis_c14d12e1 §"Retired clause" ("…is **no longer in force**"); replaced_by carried verbatim in §"Current basis"; base clauses not named (payer days never billed, patient pay unchanged, statement day/due days/no late charge, charged once) carried in force in §"Clauses in force". No undeclared retirement found.
- Entry definitions: to_base §1 / to_hub (opening entry, "beginning on the reservation's recorded first privately held day", net of reversals; "business office posts … once the entry is booked"); hs_base / hs_hub (single-entry PP hospital leave, "whose leave has ended"; hs_base adds "the reservation's one resident-private entry, the entry with the latest last day" — a derivation, equal by entailment); tc_base / tc_hub (closing entry of a released PP therapeutic hold, latest last day, not the opening entry).
- Agreement selection ("active, else notice period, else converted") and notice counting ("earlier of its latest delivery to the resident and … to the representative"): carried in every *_rate / *_iso doc and in every *_base doc respectively.
- Baselines: to_base, hs_base, tc_base each carry the baseline rule complete (charge = charged days × daily charge, half up once on the total; schedule-date split; the 12 restated rates and 2026-07-01; notice-day exclusion incl. "all of its days where no transfer notice is on file"); fall-backs computable and definite (11,336.00 / 10,464.00 / 8,284.00 = GT baseline_result). The policy's generic combination sentence is carried in the computation document (see src S3).
- Factor ladders (every tier, every task-irrelevant branch):
  - *_rate_binding (to/hs/tc): three rows — signed before & notice fewer than notice days → later-of split; signed before & no notice → all prior; otherwise (signed on/after, notice ≥ notice days, no agreement) → split at 2026-07-01; "never more than the entry's days". Complete in to_rate, hs_rate, tc_rate. "the agreement's rate-change notice days" named as an agreement term of the Private Pay Long-Term Care Residency agreement (private, unpublished → conditional C1).
  - *_extended_hold: >30 → 85, 15..30 → 95, <15 → 100, count = days on charges posted on the reservation + entry days net of reversals; both boundaries stated (to_ext, hs_ext, tc_ext).
  - *_dietary_credit: ≥4 days & memory tier (both memory tiers named) → 16.80; ≥4 other → 14.10; shorter → none; length departure→entry last day both counted (to_diet, hs_diet, tc_diet).
  - *_isolation_rate: three tiers incl. "the room held is not the agreement's room" fallback (to_iso, hs_iso, tc_iso); private product named by its official name.
  - hs_return_day: on an entry day → 1; after last day → 0; none recorded → 0 (hs_ret table).
  - hs/tc_after_hold_end: return / release (day of release last held day) / hospital-discharge expiry / ended after or not ended; clamp "never more than the entry's days" (hs_after, tc_after table).
- Prerequisites (tc only; to and hs have none and their documents state none):
  - tc→to, form state: policy_source "The therapeutic closing charge is fixed only after the opening entry of the leave carries its bed-hold charge." verbatim in tc_hub_465f8191 §"When the charge is fixed and posted"; same-form record restatement in the same section. Resolution basis: to_hub "The therapeutic opening charge is the private bed-hold charge on the therapeutic opening entry … The business office posts the therapeutic opening charge once the entry is booked." + ledger (no charge naming 5ac4a563). Connective "only after", strength hard, form state — match. In no other policy's document (grep: only tc_hub and hc_hub carry "only after the opening entry", each its own).
  - tc→hs, form state: policy_source "The therapeutic closing charge is not posted until the resident-private entry of every earlier private-pay hospital leave of the resident that carried a single resident-private entry carries its own bed-hold charge." verbatim in tc_hub; basis hs_hub ("the resident-private entry of a Private Pay Hospital Leave Bed Hold whose leave has ended with a single resident-private entry … signs …") + reservations/ledger. Match; tc_hub only.
  - condition / resolved_by / effect: no home in any document (confirmed).
- Task-tool contracts: hub parameter tables, owners (post_* agent via unlock_agent/call_agent; sign_* user via unlock_user), receipts and error behaviour equal task_tools.py docstrings and bodies.
- Base charter atoms (variants' 46 parameters and the 8 base rules + measures): carried in payer_day_coverage_tiers, payer_reserved_day_limits (incl. payer_days_left formula), election_private_hold_terms, hold_elections, hold_end_readmission_terms, hold_end_release, leave_day_census_terms, leave_day_booking, notice_terms, bed_hold_notices, charge_billing_terms, charge_basis, payments_reductions, one_reservation_per_leave; every per-tier value checked against the variants table.

## kb_to_source

- Every normative sentence traced to a rule, ladder, parameter (with its description, e.g. "as stated in the center's Medicaid bed-hold notice", "CMS guidance F625", "42 CFR 483.15(e)(1)") or base constraint (written_election authorization → "a statement in conversation … is not the written election"; one_open_reservation dedup → "the test is made on the system's reservation records … before the reservation is opened"; open-balance measure → payments_reductions table). No added confirmation, review, notification or step.
- Cross-problem operational guidance: none (each hub names only its own tool; no "first call …").
- Opening world state written as policy fact: none. Examples are labelled hypothetical; none equals a scored value (9,118.20 / 6,663.30 / 4,720.20 / 26 / 19 / 15) or mirrors this world (checked every illustration; closest: hs_rate's hypothetical 60 notice days equals the unpublished private figure, labelled hypothetical, and hs is N-independent here).

## bijection_verdict
**PASS.** No omission, softening, retired-surface defect or addition found. Conditional C1: the closing charge's value rests on the private corpus rendering the Private Long-Term Care Room tier's rate-change notice days (60) findable under "rate-change notice days" / written rate notice.

## dependency_form
- Prerequisite sentences: verbatim on the blocked side only (tc_hub); the same-form "Put in the terms the records use" restatement stays a state (ledger shows a charge naming the opening entry; no earlier single-entry PP hospital leave entry without its charge) and names no action, performer, tool or document.
- Depended-on documents (to_*, hs_*) never mention the closing charge (grep "closing" → none).
- No other problem's tool name, route, checklist or aggregated chain in any document; charge_basis's "each of those five entries is priced by its own schedule" is the source's replaced_by sentence and states no order.
- Titles general (e.g. "Bed-Hold and Leave Reservations: The Therapeutic Closing Charge Agreement", "Private Bed-Hold Charge Agreement for a Single-Month Hospital Leave"); none restates the caller's request.
- Factor documents: none says which tier customers fall on, none names another factor or the computation document; each names the result it modifies.
- Computation documents: no "unless otherwise"/"adjustments may apply"/pointer; they do carry the policy's own generic combination sentence ("each schedule rate is first taken to the applicable percent, any per-day credit is then subtracted … the days not charged at the end of the entry are its last days") — source-originated assembly, recorded as src S3, not a rendering addition.
- Blind hops: both state-derived, none pre-solved.
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
- C1: settled; 60 days on every private tier, later-of rule (see runtime_context revision_3).
- C2: settled. The private accommodation_tiers table's isolation billing tier column (Private LTC / Private Bariatric / Private Suite → Semi-Private LTC; Private Secure Memory → Semi-Private Secure Memory) equals the *_iso ladders. The private one-open-agreement lifecycle (pending admission, active, notice period, converted are the open statuses) agrees with bedhold's agreement selection (active, else notice period, else converted). The private room-change record (move date, center-directed infection-control flag) is the field the r2 iso date test reads.

### Cross-product seeded rows read by gold steps (find_private_agreements, find_private_ledger), checked against docs/private as of each posting date
Agreement dfd84afb: tier Private LTC after the 06-16 center-directed move; active; signed 01-02 / admitted 01-05; rate notice 08-14; move 06-16; isolation true; deposit 11,520.00 = 30 × 384.00 (admission tier SP-LTC, preceding schedule); account_balance 16,716.00 = charges 146,390.00 − payments 85,632.00 − credits 44,042.00. **OK.**

| Row (id prefix, date) | What it is | Verdict |
|---|---|---|
| 6af2a192 01-05 | admission deposit 11,520.00 | OK (30 days × 384.00) |
| 2784fef3 01-05 | Jan first-month partial, 27 × 384.00 = 10,368.00 | OK (admission day chargeable) |
| 11af5eb1 01-05 | payment 10,368.00 → 2784fef3 | OK |
| da27b14a 01-25 | Feb 28 × 384 = 10,752.00 | OK (advance, statement day 25) |
| bd210852 02-10 | payment 10,752.00 | OK |
| a0519971 02-25 | Mar 31 × 384 = 11,904.00 | OK |
| c1f1c36d 03-10 | payment 11,904.00 (open 11,904.00) | OK |
| 1e3f82cb 03-14 | discharge proration 18 × 384 = 6,912.00 from 03-14 | OK (departure day not chargeable here; the hold day is charged on bed-hold 67fc3039) |
| b8b4487b 03-15 | Mar re-bill 03-15..31, 17 × 384 = 6,528.00 | OK (return day chargeable) |
| 665415e3 03-25 | Apr 30 × 384 = 11,520.00 | OK |
| 355908dd 04-10 | payment 11,136.00 (open 11,520.00) | OK (≤ open balance) |
| 4759e2ba / da789c90 | May 11,904.00 / payment | OK |
| 93bcb7a7 / 26c73429 | Jun 11,520.00 / payment 06-10 | OK |
| d1bb6d14 06-16 | room-change proration 15 × 384 = 5,760.00 | OK (room_change_credit: charge for the tier left; come-off tier = the charge's tier SP-LTC; schedule on 06-16 = preceding) |
| 22957560 06-16 | isolation span 06-16..30, 15 × 384 = 5,760.00 | OK (center-directed move, isolation billing tier) |
| c0daf344 06-25 | Jul 31 × 384 = 11,904.00, isolation basis | OK on amount (no notice yet: the earlier rate applies); basis see O1 |
| 99718209 07-08 | discharge proration 24 × 384 = 9,216.00 from 07-08 | OK |
| 8ddea75c 07-10 | payment **11,904.00** naming c0daf344 | **NOT what the docs produce — S6** |
| be6d9617 07-25 | Aug 31 × 384 = 11,904.00 | OK |
| 4c06a889 08-01 | Jul re-bill 07-27..31, 5 × 384 = 1,920.00 | OK |
| fdf812c0 08-10 | payment 4,608.00 (open 11,904.00) | OK on its own; its remaining 7,296.00 is past due under S6 |
| ab1d5fbb 08-25 | Sep 30 × 384 = 11,520.00 | OK |
| 54840741 09-05 | discharge proration 26 × 384 = 9,984.00 | OK |
| 869baba5 09-10 | payment 1,536.00 = open balance | OK |
| b5dcc902 / 6f9cf688 09-25 | Oct split at 10-13 (08-14 + 60): 12 × 384 = 4,608.00 and 19 × 398 = 7,562.00 | OK (later-of rule; split per rate) |
| 2e7bdbc1 / 2494a02a 09-25 | both Oct spans credited, discharge proration | OK (resident on leave) |
| 78ab8c28 10-20 | Oct re-bill 10-20..31, 12 × 398 = 4,776.00 | OK |
| c82fe9dd 10-25 | Nov 30 × 398 = 11,940.00 | OK |

S6 (seed, ledger exactness): payment_posting_and_returned_payments_f2993a3e says "A payment names the charge it pays and is applied only up to that charge's open balance" and defines "*Amount applied*: the lesser of the payment and the charge's open balance". On 2026-07-10, charge c0daf344's open balance was 11,904.00 − 9,216.00 (credit 99718209, 07-08) = 2,688.00. The seeded payment 8ddea75c applies 11,904.00. Under the docs, the August charge's 7,296.00 remainder stands open past the 30-day grace (due 08-10). The late_charge_rule would then put 1.5 % per month on it (109.44), and those late-charge rows are missing. No bed-hold computation reads the private ledger, so no scored value moves. No published tool posts a late charge, so a solver cannot make one mid-conversation.

O1 (observation, not routed): private_rate_schedule_rule clause 4 ("Charges priced at a rate held back for a late notice carry the prior-rate notice-hold charge basis") and room_and_board_billing_rule ("…isolation billing tier's rate with the isolation charge basis…") both claim the Jul–Oct 12 charges. The private corpus states no precedence, and the seed uses isolation_rate. No bed-hold read depends on the basis.

### Owed-at-once writes under the now-published products
- Field map of every published task tool: bedhold tools write bedhold_ledger/bedhold_reservations. Private tools write private_ledger and update only private_agreements.account_balance/deposit_balance (task_tools.py lines 61/95/139/167/200). Medicaid tools touch medicaid_ledger/patient_pay_balance; medicare tools medicare tables; trust tools trust tables. The bed-hold computations read bedhold_ledger, bedhold_reservations and the agreement's status, signed date, rate notice date, tier, isolation flag and last room change. No tool of another product writes any of these.
- Owed candidates for Ruth: (i) late-notice credit — settled on the latest-span charge (Nov), whose span starts after 10-13: zero, none owed. (ii) Additional deposit after the 06-16 move: 30 days × current SP-LTC 398.00 (isolation billing tier; notice taken effect 10-13) − held 11,520.00 = 420.00. The customer pays it (`pay_additional_deposit_f9f00bc8`, user tool), the persona declines payment, and it raises deposit_balance only. (iii) Room-change credit already on the June charge. None can move a scored read.
- Ruth holds no medicare, medicaid, trust, ancillary or therapy record.

### Verdict
bijection **PASS**, dependency_form **PASS** (bedhold corpus unchanged since r2). New source/seed item: S6.

## revision_4 (2026-10-23, round 4)

Entry: RENDER.log tail "RENDER round 3: DOCS OK"; kb_snapshot (round 4) — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged; extended yaml f9fc40ef…b2de and task_tools 788ee1d3… unchanged; docs/bedhold tree 24cc3f6db0001c26 unchanged; docs/private and docs/medicaid identical to the round-3 dumps. tasks/{0,1}.json rewritten 2026-10-23 10:43 (seed rework, round 8). Scratch /tmp/erl0074_kbaudit_bedhold/r4/.

### S6 — closed
Seed diff against round 3: payment 8ddea75c 2026-07-10 is now 2,688.00, equal to the open balance of c0daf344 after the 07-08 credit (11,904.00 − 9,216.00), as payment_posting_and_returned_payments requires ("applied only up to that charge's open balance"). Payment fdf812c0 2026-08-10 is now 11,904.00 on be6d9617 (open 11,904.00), and a new payment 612a6469 2026-08-10 of 1,920.00 pays the July re-bill 4c06a889 (open 1,920.00).
Re-check of every row of the 33-row private ledger (the 30 unchanged rows as in the revision_3 table):
- per-charge open balances: c0daf344 0.00, 4c06a889 0.00, be6d9617 0.00; every other month nets as before;
- no room-and-board month is past due beyond the 30-day grace at any date, so no late charge is owed;
- totals: charges 146,390.00 − payments 85,632.00 − credits 44,042.00 = 16,716.00 = account_balance (the October re-bill 4,776.00 + November 11,940.00, neither past due at 11-04).

All rows are OK. The additional-deposit payment record is unchanged (no dishonored payment, no late charge → 30 days), so the customer-paid 420.00 owed is as before and touches only deposit_balance.

### Owed-at-once writes
Unchanged: no tool of any published product writes the bed-hold tables or the agreement fields read. None can move a scored read.

### Verdict
bijection PASS, dependency_form PASS, no regression. No new item.
