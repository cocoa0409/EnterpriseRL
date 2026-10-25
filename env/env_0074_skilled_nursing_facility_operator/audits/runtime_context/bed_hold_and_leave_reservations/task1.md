# Runtime-context blind audit — bed_hold_and_leave_reservations / task 1

## revision_1

## blind_answer

- Freeze time: 2026-10-23T05:08Z, before any source-layer read. Auditor: independent KB-audit agent.
- Visible materials: `.audit_views/runtime/bed_hold_and_leave_reservations/task1.runtime.json` (sha256 8bedf6a737dffa800b10bdd7f637566564f58d5880702d47768aa55d5b5d65b7; frozen_time `2026-11-05 11:15:00 EST`); docs/bedhold title+content (50 files, tree 88bc62df190873bb, meta not read); share tools via `db_query.py … 1 --list`; DB via `db_query.py bed_hold_and_leave_reservations 1 '<calls>'` (blind on the DB side). private/trust unpublished → **conditional** where relied on.
- Forbidden list as task 0; contamination_disclosure: none.

### 1. Request
Caller Marisol Quintero, spouse and `representative_name` of Harold Quintero (customer 509100e1…, York); target: "sign the October bed-hold charge for your husband's held bed"; she signs herself; pays later. Simulator passive (DOB 1941-06-03, SSN4 4290, phone; "If the agent says other steps have to come first, you say that is fine"). Verify with DOB + SSN4.

### 2. Act now / wait / refuse
Act now. Reservation 6680ad7e `Medicaid Hospital Leave Reserved Bed`, `status returned`, `leave_start_date 2026-08-25`, `return_date 2026-10-14`, `private_hold_start_date 2026-09-06`; entries: payer_reserved 08-25..08-31 (7), 09-01..09-05 (5); resident_private 5eece24c 09-06..09-30 (25), 5292a774 10-01..10-17 (17); no charges. Private extensions on file (09-06, 10-06; election_private_hold_terms: MA tiers "Yes" may continue privately). hc_hub: closing entry = "the resident-private entry with the latest last day on the reservation, when it is not also the opening entry" → 5292a774. Signer = resident or representative. hc_hub's wait unmet (item 6) → the closing waits on one other charge, writable now.

### 3. Objects
- Closing: reservation 6680ad7e-1cb3-4098-bd41-8e9b0a63d52e, entry 5292a774-429f-4d5d-a92c-10663c5b6e0e.
- Opening: entry 5eece24c-f041-4a34-8234-6e2fa3771ee2 (begins on the recorded first privately held day 09-06).
- Excluded: reservation 820cb727 (Aug 10–12 hospitalization, returned 08-13 — a separate hospitalization: "the continuous absence from the transfer to the return"; payer days only).
- Agreement read: private agreement f19f9229 `status payer_converted` (the "converted to another payer source" fallback), `variant_name Private Long-Term Care Room`, signed 2026-01-28, `rate_notice_delivered_date 2026-08-31`, `isolation_placement True`, `last_room_change_date 2026-04-14`.

### 4. Scored parameters
Rate-change notice days: unpublished (private) → conditional; no ledger corroboration on this customer (no private room-and-board after the 06-01 conversion). I use 60 (task-0 world's private ledger switch implies 60 for the same tier).

(a) Hospital opening charge — entry 5eece24c, 25 days.
- Notice: resident 08-25 22:00, representative 08-25 22:00 → 08-25; 0 before.
- ma (ho_ma): MA hospital tier 15/hospitalization; departure 08-25 day 1, 09-08 day 15; days from departure to entry start = 12 → 15 − 12 = 3 payer-covered first days (09-06..09-08), "however the entry was booked". Start grounds: notice 0, ma 3 → larger = 3 → 22 charged (09-09..09-30).
- iso (ho_iso): agreement payer_converted is the one read; isolation; tier = room held (Private LTC, room 437); move 04-14 before leave → Semi-Private LTC.
- rate (ho_rate row 1): signed before 07-01, notice 08-31 → current from later of 07-01 and 08-31+60 = 10-30 → 0 current in Sept (any N ≥ 31 gives 0) → prior 384.00.
- diet: 08-25..09-30 = 37 days → 14.10. ext: 0 posted + 25 = 25 → 95 %.
- 22 × (384×0.95 − 14.10 = 350.70) = **7,715.40**; day_count **22**. Fall-back (ho_base alone): 25 × 436.00 = 10,900.00.

(b) Hospital closing charge — entry 5292a774, 17 days (10-01..10-17).
- Notice 0 at start. ret (hc_ret): return 10-14 on the entry → 1; after (hc_after): days after 10-14 = 10-15..10-17 = 3 → end uncharged 4 → 13 charged (10-01..10-13).
- rate: current from 10-30 (N=60, conditional) → 0 current → prior 384.00 (N ≤ 43 would put current days inside the charged days).
- iso Semi-Private LTC. diet: 08-25..10-17 = 54 days → 14.10. ext: posted on 6680ad7e after (a) = 22 + entry 17 = 39 > 30 → 85 %.
- 13 × (384×0.85 − 14.10 = 312.30) = **4,059.90**; day_count **13**. Fall-back (hc_base alone): 17 × 436.00 = 7,412.00.
- Without (a) first: count 17 → 95 % → 13 × 350.70 = 4,559.10 — the wait bears weight.

### 5. Sequence
find_customers → verify_customer_identity → find_bedhold_reservations / ledger / elections → find_private_agreements → unlock_agent_discoverable_tool(`post_hospital_opening_charge_991dca72`) + call (6680ad7e, 5eece24c, 22, 7715.40) [agent] → unlock_user_discoverable_tool(`sign_hospital_closing_charge_702d4c7f`) → user signs (6680ad7e, 5292a774, 13, 4059.90). Terminal: both charges posted.

### 6. Problem tree
- Root: hospital closing charge (user signs).
- Hop 1 — hc_hub: "The hospital closing charge is worked out only after the opening entry of the hold carries its bed-hold charge." / "…once the reservation's ledger shows a bed-hold charge naming the opening entry of the hold." Ledger: no charge naming 5eece24c. Writer found by "opening entry … bed-hold charge": ho_hub "The hospital opening charge … is the private bed-hold charge on the hospital opening entry … The business office posts the hospital opening charge once the entry is booked." → **state-derived**. ho_hub states no wait → leaf. Order: opening → closing.
- No pre-solved hop.

### Counter-proofs
- "Sign only the October charge": excluded by hc_hub sentence + ledger lacking a charge on 5eece24c.
- Alternatives: (i) charge the first private days 09-06..09-08 — excluded by ho_ma ("are payer-covered and are not charged, however the entry was booked"); (ii) add the notice and MA start counts — excluded by ho_base (f) "as many as the larger of the counts on each ground, never their total" (both 0/3 here, so moot); (iii) count per-hospitalization across the Aug 10 reservation — excluded by "continuous absence from the transfer to the return"; (iv) post-07-01 rate notice read under the "otherwise" row → all current → opening 22 × (398×0.95 − 14.10 = 364.00) = 8,008.00, closing 13 × (398×0.85 − 14.10 = 324.20) = 4,214.60 — same open point as task 0, to check against source; (v) rate-change notice days unpublished → conditional.
- Findability: iso via `isolation_placement`; rate via `rate_notice_delivered_date`; ma via the reservation's `variant_name` Medicaid Hospital Leave Reserved Bed + payer_reserved entries (grep "reserved days"); ret/after via `return_date`; diet/ext via the result name.

## gt_comparison

Reveal time 2026-10-23T05:20Z (same source hashes; tasks/1.json). blind_answer untouched.

| Item | Blind | Source / GT | Same? |
|---|---|---|---|
| Tree | closing ← opening (state) | prerequisite_closure hc→ho (value_input, state), order ho→hc | same |
| Hop mark | state-derived | policy_source verbatim in hc_hub | same |
| Opening | 6680ad7e / 5eece24c / 22 / 7,715.40 (agent post) | same | same |
| Closing | 6680ad7e / 5292a774 / 13 / 4,059.90 (user signs) | same | same |
| Fall-backs | 10,900.00 / 7,412.00 | baseline_result 10900.0 / 7412.0 | same |
| Factor tiers | ho: ma 3, rate row1, ext 95, diet 14.10, iso SP-LTC; hc: ret 1, after 3, ext 85 (22+17=39) | factor_trace identical; edge_load_bearing 4559.10 if skipped (blind: 4,559.10) | same |
| Notice days | 60 (conditional) | 60 | same (conditional) |

**Verdict: PASS** (conditional on the private corpus rendering the rate-change notice days; task-1 values hold for any N ≥ 44).

## revision_2 (2026-10-23, re-audit round 2)

Entry: RENDER.log tail "RENDER round 2: DOCS OK"; kb_snapshot 2026-10-23T06:25:36 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged (967ee5a3…0955 / 8bedf6a7…65b7); extended yaml f9fc40ef…b2de (was 4718b6c8…); task_tools unchanged 788ee1d3…; docs/bedhold 50 files, tree 24cc3f6db0001c26 (was 88bc62df190873bb).

contamination_disclosure: as task 0 — not blind (source read in revision_1); docs-only re-derivation, revision_1 untouched.

### blind_answer (re-derivation on the round-2 corpus)
- DB unchanged (agreement payer_converted, last_room_change_date 2026-04-14, rate notice 2026-08-31).
- Opening (6680ad7e / 5eece24c): iso — 04-14 ≤ departure 08-25 → SP-LTC; rate row 1 ("on or after 2026-07-01") → all prior; ma 3 (ho_ma table now "runs through 31 March", same rule); 22 × 350.70 = **7,715.40**, 22 days.
- Closing (6680ad7e / 5292a774): 13 × 312.30 = **4,059.90**, 13 days; ext 22 + 17 = 39 → 85.
- Tree unchanged (hc_hub sentence verbatim; hop state-derived). Fall-backs 10,900.00 / 7,412.00.

### gt_comparison
GT unchanged (7715.4 / 4059.9; 22/13; ho→hc). Same. **PASS** (conditional C1; holds for N ≥ 44).

## revision_3 (2026-10-23, round 3 — cross-product re-judge)

Entry: all seven corpora published (docs/private 69 files, docs/trust present). kb_snapshot 2026-10-23T10:12:51 — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes unchanged since revision_2: runtime views 967ee5a3…0955 / 8bedf6a7…65b7; extended yaml f9fc40ef…b2de; task_tools 788ee1d3…; docs/bedhold tree 24cc3f6db0001c26 (no bedhold document changed). Scratch: /tmp/erl0074_kbaudit_bedhold/r3/.

Not blind (disclosed in revision_2). The bedhold corpus is unchanged, so the revision_2 derivation stands. Conditional C1 is now settled against docs/private: daily_rate_schedule_and_rate_notice_1ab0eb50 "A new scheduled rate needs 60 calendar days of written notice … takes effect on the **later** of … the schedule's effective date, and the date the written rate notice was delivered for that agreement plus 60 calendar days. The figure of 60 days applies to all six tiers." private_rate_schedule_rule_2c76df2a also names the "rate change notice days", so a reader can link the term in the bedhold *_rate documents to the figure. With N = 60 the GT values follow (task 0: 9,118.20 / 6,663.30 / 4,720.20; task 1: 7,715.40 / 4,059.90). Task 0's private ledger (398.00 from 2026-10-13) agrees. **PASS**, no longer conditional.

## revision_4 (2026-10-23, round 4)

Entry: RENDER.log tail "RENDER round 3: DOCS OK"; kb_snapshot (round 4) — EXTENDED/TASK TOOL CONTRACT/REPLAY/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses). Hashes: runtime views unchanged; extended yaml f9fc40ef…b2de and task_tools 788ee1d3… unchanged; docs/bedhold tree 24cc3f6db0001c26 unchanged; docs/private and docs/medicaid identical to the round-3 dumps. tasks/{0,1}.json rewritten 2026-10-23 10:43 (seed rework, round 8). Scratch /tmp/erl0074_kbaudit_bedhold/r4/.

The bed-hold corpus and the source are unchanged. The bed-hold records and the agreement fields the bed-hold factors read (status, signed date, rate-notice date, tier, isolation flag, last room change) are unchanged in the reworked seed (runtime DB re-queried). The gold is unchanged (computations and call arguments identical to revision_3). The revision_2/3 derivation stands. **PASS.**
