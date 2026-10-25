# Runtime-context blind audit — bed_hold_and_leave_reservations / task 0

## revision_1

## blind_answer

- Freeze time: 2026-10-23T05:05Z, written before any source-layer read (extended yaml, task_tools.py, task JSON, worklog, plan, audits/ except XF_recipe.md and the last line of policy_task/_difficulty.md). Auditor: independent KB-audit agent (not the renderer, not the policy auditor).
- Visible materials: `.audit_views/runtime/bed_hold_and_leave_reservations/task0.runtime.json` (sha256 967ee5a378d11a6515e7e0aaf2917a13ef5b977d40d7a87b21d1a96c3fd70955; frozen_time `2026-11-04 10:30:00 EST`); docs/bedhold/*.json title+content only (50 files, tree sha256 88bc62df190873bb; the `meta` key was not read); share-tool schemas via `db_query.py … 0 --list`; DB returns via `db_query.py bed_hold_and_leave_reservations 0 '<calls>'` (share finders, KB_search, grep) — DB side is blind (tool-shaped). Products published: medicare, medicaid, bedhold, ancillary, therapy; private and trust NOT published — figures resting on them are marked **conditional**.
- Forbidden and not opened: bedhold.extended.yaml, task_tools.py, tasks/*.json, worklog.md, plan.md, raw initial_state, doc meta, render plan, verification scripts, other audit conclusions. contamination_disclosure: none (brief gave only gate lines, no scored value; all searches path-scoped to docs/bedhold and the runtime view).

### 1. Request, timing, authorisation, simulator behaviour
Caller Daniel Pellegrino, POA for resident Ruth Pellegrino ("I hold power of attorney"); target object: "the October bed-hold charge" for the September-5 home stay; action: sign the bed-hold charge agreement himself on this call; not paying today. Simulator is passive: gives DOB 1939-02-11, SSN4 4718, phone one at a time; "If the agent says other steps have to come first, you say that is fine"; signs any signing step "exactly as given". Identity: `find_customers{full_name}` → customer 979bfd0e…, representative_name Daniel Pellegrino, power_of_attorney; `verify_customer_identity` with DOB + SSN4 (2 matches) verifies.

### 2. Act now / wait / refuse
Act now. Reservation bf66de92 `variant_name: Private Pay Therapeutic Leave Bed Hold`, `status: released`, `release_date 2026-10-15`; ledger carries two resident-private entries (5ac4a563: 2026-09-05..09-30, 26 days; e1427af6: 2026-10-01..10-19, 19 days), no charge on either. tc_hub: "the closing entry of a released Private Pay Therapeutic Leave Bed Hold that carries more than one resident-private entry — the resident-private entry with the latest last day on the reservation" → October entry e1427af6 is the therapeutic closing entry; the signer is "the resident or representative". Elections on file (hold 2026-09-05 created 09-04 15:30, within 24 h of the 09-04 15:00 notices; private_extension effective 10-05; release 10-15) — no eligibility bar. But tc_hub's two waits are unmet now (item 6), so the closing charge itself waits until two other charges are on file; both of those are writable now.

### 3. Narrowest objects and correlation keys
- Closing: reservation bf66de92-fe81-4283-99eb-0cc280e97844, entry e1427af6-fc1f-44ac-b7fa-789b8eca5cb3.
- Opening (same reservation): entry 5ac4a563-add5-497a-a367-259046bacbfb (begins on `private_hold_start_date 2026-09-05` — to_hub "the resident-private entry beginning on the reservation's recorded first privately held day").
- Earlier private-pay hospital leaves with a single resident-private entry: fb07a840 (March, entry 0043d3ae, charge 67fc3039 already names it — excluded, "a booked entry that a charge on the reservation's ledger already names is not charged again"); 1ed7c997-1ba3-4402-aaef-1212dbe8483b (July, returned 2026-07-27, single entry 63313f5e-2c96-47c3-97cb-fb362d04b80d 07-08..07-31, 24 days, no charge) — included.
- Agreement read by the iso/rate rules: private agreement dfd84afb (`status active`, `variant_name Private Long-Term Care Room`, `agreement_signed_date 2026-01-02`, `rate_notice_delivered_date 2026-08-14`, `isolation_placement True`, `last_room_change_date 2026-06-16`).

### 4. Scored parameters (formula in words, inputs, tiers, value)
Rounding: half up to the cent once on the total. Combination (each *_base doc): rate taken to the percent, per-day credit subtracted, times charged days; start-uncharged = first days, end-uncharged = last days, current-schedule days counted back from the entry's last day.
Rate-change notice days of the agreement are not on the record and are not in any published document (private product unpublished) → **conditional**. Record corroboration: the private ledger prices room-and-board at 384.00 through 2026-10-12 and 398.00 from 2026-10-13 (`6f9cf688… from_date 2026-10-13 daily_rate 398.0`), i.e. 2026-08-14 + 60 days; I use 60.

(a) Therapeutic opening charge — entry 5ac4a563, 26 days, none reversed.
- Notice: latest to resident 2026-09-04 15:00, to representative 2026-09-04 15:00 → 09-04; no entry day before it → 0 uncharged.
- iso (to_iso): agreement active, isolation placement, agreement tier = room held tier (Private Long-Term Care Room, room 431), move 06-16 before the leave → priced at Semi-Private Long-Term Care Room (384.00 / 398.00).
- rate (to_rate row 1): signed before 2026-07-01, notice 08-14 fewer than 60 days before 07-01 → current from later of 07-01 and 2026-10-13 → 0 current days in Sept → 26 prior.
- diet (to_diet): leave 09-05..09-30 = 26 days ≥ 4, non-memory tier → 14.10/day.
- ext (to_ext): posted charges on bf66de92 = 0 days + entry 26 = 26 → 95 %.
- Daily 384.00×0.95 − 14.10 = 350.70; 26 × 350.70 = **9,118.20**; day_count **26**.
- Fall-back (to_base alone): 26 days, Private LTC current 436.00 → 11,336.00 (definite, different).

(b) Hospital stay charge — reservation 1ed7c997, entry 63313f5e, 24 days.
- Notice: latest to representative 07-08 22:40, to resident 07-09 08:15 → earlier 07-08; no day before → 0 at start.
- after (hs_after): returned 07-27 → 07-28..07-31 = 4 uncharged; ret (hs_ret): return day 07-27 on the entry → 1 uncharged → 19 charged (07-08..07-26).
- rate (hs_rate row 1): current from later of 07-01 and 08-14+N (≥ 08-14 whatever N) → 0 current days in a July entry → all prior (N-independent).
- iso: Semi-Private LTC (move 06-16 before 07-08 leave). diet: 24 days → 14.10. ext: 0 + 24 = 24 → 95 %.
- 19 × 350.70 = **6,663.30**; day_count **19**. Fall-back: 24 × 436.00 = 10,464.00.

(c) Therapeutic closing charge — entry e1427af6, 19 days (10-01..10-19).
- Notice 09-04 → 0 at start. after (tc_after): released 10-15 → 10-16..10-19 = 4 uncharged at end → 15 charged (10-01..10-15). (tc has no return-day schedule; status released.)
- rate: current from 2026-10-13 (conditional on N=60) → current days 10-13..10-19 = 7 counted back from last day; charged current = 10-13..10-15 = 3; charged prior = 12.
- iso Semi-Private LTC. diet: leave 09-05..10-19 = 45 days → 14.10. ext: posted charges on bf66de92 after (a) = 26 days + entry 19 = 45 > 30 → 85 %.
- Prior daily 384×0.85 − 14.10 = 312.30 ×12 = 3,747.60; current 398×0.85 − 14.10 = 324.20 ×3 = 972.60; total **4,720.20**; day_count **15**.
- Fall-back (tc_base alone): 19 × 436.00 = 8,284.00.
- Without (a) posted first the ext count would be 19 → 95 % → a different figure: the wait bears weight.

### 5. Executable sequence
find_customers → verify_customer_identity(DOB, SSN4) → find_bedhold_reservations / find_bedhold_ledger / find_bedhold_elections / find_private_agreements (+ private ledger) → unlock_agent_discoverable_tool(`post_therapeutic_opening_charge_78fe9a0a`) + call (bf66de92, 5ac4a563, 26, 9118.20) [agent] ; unlock_user_discoverable_tool(`sign_hospital_stay_charge_56dfc7d9`) → user signs (1ed7c997, 63313f5e, 19, 6663.30) ; then unlock_user_discoverable_tool(`sign_therapeutic_closing_charge_194aeb06`) → user signs (bf66de92, e1427af6, 15, 4720.20). Terminal: three posted charges; caller told October charge posted. (a) and (b) in either order; both strictly before (c).

### 6. Problem tree from visible materials alone
- Root: therapeutic closing charge (user signs).
- Hop 1 — tc_hub: "The therapeutic closing charge is fixed only after the opening entry of the leave carries its bed-hold charge." / "…once the reservation's ledger shows a bed-hold charge naming the opening entry of the leave". Ledger: no `bedhold_charge` with days_entry_id 5ac4a563. Writer found by the words "opening entry … bed-hold charge": to_hub "The therapeutic opening charge is the private bed-hold charge on the therapeutic opening entry … The business office posts the therapeutic opening charge once the entry is booked." → **state-derived**.
- Hop 2 — tc_hub: "The therapeutic closing charge is not posted until the resident-private entry of every earlier private-pay hospital leave of the resident that carried a single resident-private entry carries its own bed-hold charge." Records: reservation 1ed7c997 (Private Pay Hospital Leave Bed Hold, July, single resident-private entry 63313f5e, no charge). Writer found by "private-pay hospital leave … single resident-private entry … bed-hold charge": hs_hub "the resident-private entry of a Private Pay Hospital Leave Bed Hold whose leave has ended with a single resident-private entry on the reservation. The resident or representative signs…" → **state-derived**. (March fb07a840 already charged → no hop.)
- Neither to_hub nor hs_hub states a wait of its own → leaves. Order: {opening, stay} → closing.
- No hop pre-solved: no document names another problem's tool or a route.

### Counter-proofs
- "Do only the one thing asked": tc_hub's two sentences forbid fixing/posting the closing charge while the ledger lacks a charge naming 5ac4a563 and while 63313f5e has none; both states verifiable false at the opening → excluded by visible rule + records.
- Closest alternatives: (i) price the closing over all 19 days — excluded by tc_after "the entry's days dated after the release date … the day of release being the last held day" + `release_date 2026-10-15`; (ii) price at the Private LTC rate — excluded by to/tc/hs_iso + `isolation_placement True`; (iii) rate-notice reading: a notice delivered *after* 2026-07-01 could be read as falling in the "otherwise" row (all July+ days current), giving opening 26×364.00 = 9,464.00, stay 19×364.00 = 6,916.00, closing 15×324.20 = 4,863.00. I take row 1 ("delivered fewer than the … notice days before 2026-07-01"; "binds a resident only through notice" — tc_rate) and the private ledger's own 10-13 switch corroborates it, but no document states the post-date case in words — to be checked against the source (possible ambiguity). (iv) The rate-change notice days figure is not published (private) → closing value conditional on it; opening and stay are robust to any N ≥ 47 / any N respectively.
- Findability: iso via record field `isolation_placement` (grep "isolation placement" → the 5 iso docs); rate via `rate_notice_delivered_date` (grep "rate notice"); after via `release_date`/`return_date`; diet/ext via the result's name and the reservation's held days (grep "therapeutic closing" returns all tc docs). No computation document announces a variation (see policy_kb dependency_form for the generic combination sentence).

## gt_comparison

Reveal time 2026-10-23T05:20Z (bedhold.extended.yaml sha256 4718b6c8…dbe4c2dfcdbda, task_tools.py 788ee1d3…ccd4f4, tasks/0.json). blind_answer above left untouched.

| Item | Blind | Source / GT | Same? |
|---|---|---|---|
| Root / tree | closing ← {opening (state), stay (state)} | prerequisite_closure: tc→to (value_input, state), tc→hs (state_gate, state); A,B commute, C last | same |
| Hop marks | both state-derived | policy_source sentences verbatim in tc_hub | same |
| Opening | bf66de92 / 5ac4a563 / 26 / 9,118.20 (agent post) | same args, agent `call_agent_discoverable_tool` | same |
| Stay | 1ed7c997 / 63313f5e / 19 / 6,663.30 (user signs) | same | same |
| Closing | bf66de92 / e1427af6 / 15 / 4,720.20 (user signs) | same | same |
| Fall-backs | 11,336.00 / 10,464.00 / 8,284.00 | baseline_result 11336.0 / 10464.0 / 8284.0 | same |
| Factor tiers | to: rate row1, ext 95, diet 14.10, iso SP-LTC; hs: + ret 1, after 4; tc: after 4, ext 85 | factor_trace identical | same |
| Rate-change notice days | 60 (inferred from private ledger 10-13 switch; conditional) | CPARAM private rate_change_notice_days = 60 on every private tier | same (conditional on private publication) |
| Post-07-01 rate notice | read under row 1 | compute row 1 when DAYS(schedule, notice)+N > 0 | same — wording point recorded as src S2 |

Hidden-only explanation needed: none beyond the unpublished private figure (conditional). No visible addition/omission changes a permitted action, parameter, order or result.

**Verdict: PASS** (conditional on the private corpus rendering the agreement tier's rate-change notice days, 60).

## revision_2 (2026-10-23, re-audit round 2)

Entry: RENDER.log tail "RENDER round 2: DOCS OK"; kb_snapshot 2026-10-23T06:25:36 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged (967ee5a3…0955 / 8bedf6a7…65b7); extended yaml f9fc40ef…b2de (was 4718b6c8…); task_tools unchanged 788ee1d3…; docs/bedhold 50 files, tree 24cc3f6db0001c26 (was 88bc62df190873bb).

contamination_disclosure: this auditor read the source layer and GT in revision_1, so this revision is **not blind**; it is a docs-only re-derivation of the changed documents, frozen here before the round-2 source was compared. revision_1 text untouched.

### blind_answer (re-derivation on the round-2 corpus)
Doc diff vs revision_1 (scratch /tmp/erl0074_kbaudit_bedhold/docs_r2.txt): *_iso now state the date test ("the agreement's last room change, the center's infection-control move, being dated no later than the departure date", + "Date boundary" paragraph and a "not on the agreement" fallback); *_rate row 1 now reads "…fewer than the agreement's rate-change notice days before 2026-07-01, or on or after 2026-07-01", examples replaced by a D-generic case list; illustrations reworked in charge_basis, hc/hs_after, hc_ret, ho_base, ho_ma, to_base, tc_after, payer_reserved_day_limits, payments_reductions. Nothing else changed.
- DB returns unchanged (private agreement last_room_change_date 2026-06-16, rate notice 2026-08-14; reservations/ledger identical).
- Opening (bf66de92 / 5ac4a563): iso — move 2026-06-16 ≤ departure 2026-09-05 → Semi-Private LTC; rate — notice 08-14 is "on or after 2026-07-01" → row 1, now stated in words (closes the round-1 reading point); 26 × 350.70 = **9,118.20**, 26 days.
- Stay (1ed7c997 / 63313f5e): move 06-16 ≤ 07-08 → SP-LTC; row 1 → all prior; 19 × 350.70 = **6,663.30**, 19 days.
- Closing (bf66de92 / e1427af6): 12 × 312.30 + 3 × 324.20 = **4,720.20**, 15 days (rate-change notice days 60 still unpublished → conditional C1).
- Tree unchanged: tc_hub sentences verbatim; hops to→ and hs→ state-derived; nothing pre-solved. Fall-backs unchanged (11,336.00 / 10,464.00 / 8,284.00).

### gt_comparison
GT unchanged (tasks/0.json: 9118.2 / 6663.3 / 4720.2; days 26/19/15; same order). Item-by-item same. The only remaining alternative of revision_1 (post-07-01 notice under "otherwise") is now excluded by visible text. **PASS** (conditional C1).

## revision_3 (2026-10-23, round 3 — cross-product re-judge)

Entry: all seven corpora published (docs/private 69 files, docs/trust present). kb_snapshot 2026-10-23T10:12:51 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes unchanged since revision_2: runtime views 967ee5a3…0955 / 8bedf6a7…65b7; extended yaml f9fc40ef…b2de; task_tools 788ee1d3…; docs/bedhold tree 24cc3f6db0001c26 (no bedhold document changed). Scratch: /tmp/erl0074_kbaudit_bedhold/r3/.

Not blind (disclosed in revision_2). The bedhold corpus is unchanged, so the revision_2 derivation stands. Conditional C1 is now settled against docs/private: daily_rate_schedule_and_rate_notice_1ab0eb50 "A new scheduled rate needs 60 calendar days of written notice … takes effect on the **later** of … the schedule's effective date, and the date the written rate notice was delivered for that agreement plus 60 calendar days. The figure of 60 days applies to all six tiers." private_rate_schedule_rule_2c76df2a also names the "rate change notice days", so a reader can link the term in the bedhold *_rate documents to the figure. With N = 60 the GT values follow (task 0: 9,118.20 / 6,663.30 / 4,720.20; task 1: 7,715.40 / 4,059.90). Task 0's private ledger (398.00 from 2026-10-13) agrees. **PASS**, no longer conditional.

## revision_4 (2026-10-23, round 4)

Entry: RENDER.log tail "RENDER round 3: DOCS OK"; kb_snapshot (round 4) — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged; extended yaml f9fc40ef…b2de and task_tools 788ee1d3… unchanged; docs/bedhold tree 24cc3f6db0001c26 unchanged; docs/private and docs/medicaid identical to the round-3 dumps. tasks/{0,1}.json rewritten 2026-10-23 10:43 (seed rework, round 8). Scratch /tmp/erl0074_kbaudit_bedhold/r4/.

The bed-hold corpus and the source are unchanged. The bed-hold records and the agreement fields the bed-hold factors read (status, signed date, rate-notice date, tier, isolation flag, last room change) are unchanged in the reworked seed (runtime DB re-queried). The gold is unchanged (computations and call arguments identical to revision_3). The revision_2/3 derivation stands. **PASS.**
