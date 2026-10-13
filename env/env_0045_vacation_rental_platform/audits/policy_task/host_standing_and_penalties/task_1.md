# Policy-task audit — host_standing_and_penalties / task 1

## source_derivation_frozen

- auditor: erl-task-policy-audit (independent Claude agent)
- freeze time: 2026-10-07T19:40Z — written before the GT of ANY task of this difficulty was revealed (task 0's derivation was frozen first; no reveal has happened)
- view used: `/tmp/erl45_views/r1/host_standing_and_penalties/task_1.view.json` sha256 ff5385848fb0cb228d55c1158f72e1b65b89e691de9fe579f0fb1f22107a74f4
- charter: `host.extended.yaml` bfe6e9be…c064cf1573b; tools: `task_tools.py` 0a815c03…dde860ad4e1b4a7 (see `_difficulty.md` § charter_global_frozen)
- masked and unread at freeze: the whole of `tasks/1.json` beyond the view, `worklog.md` files.
- contamination_disclosure: none. The policy's own `compute` was evaluated on the view world (temporary script, removed) only to cross-check the hand derivation.

World (frozen_time 2026-10-06T14:30:00, date 2026-10-06):
- customer 37f50368… Ines Albarran (phone 6195553178, id last4 3741).
- host_accounts af38dd1e…: Professional Host, active, opened 2020-03-02, business_name "Harbor & Pine Stays LLC", last_tier_change_date 2021-05-17, restricted_until "", suspended_date "".
- host_account_events: 8 host_service_fee_assessed rows, each 15.50 % of its base, the latest 2026-10-03 stay da444220… base 3460.00 fee 536.30 (prior: 2026-09-28 3a2b9279…, 2026-09-20, 2026-09-12, 2026-08-22, 2026-08-08, 2026-07-19, 2026-06-28); no host_service_fee_refunded row.
- stays: da444220… HPQ7M2XW4L, listing aa9c45de… (Entire Home), checked_in 2026-10-03, host_only_fee, nightly 3010 + cleaning 350 + pet 100 + extra-guest 0 = 3460.00.
- listings: 11 listed (Entire Home ×6: aa9c, 8f46, 9115, 62dc, 0f5c [first listed 2026-06-10], de69 [2026-10-02]; Luxury Villa ×2: d094, c939; Entire Apartment ×3: 61d2, 4174, dce7 [2026-07-15]); 1 snoozed (bcbd, Entire Guest Suite); 2 suspended for registration (0a3d Entire Home, 9370 Entire Apartment, suspended 2026-09-16). Instant Book off on 61d2 and dce7 only.
- listing_events: 2026-10-01 quality reviews — pass on the 9 older live listings (4.62, 4.58, 4.64, 4.60, 4.86, 4.83, 4.59, 4.61, 4.61), not_assessed on 0f5c (4.25) and dce7 (4.10); 2025-10-01 warning on 9115 (4.22); regulatory notices 2026-08-31 on the two suspended listings (cure deadline 2026-09-15).
- listing_reinstatement_requests: two, suspension_reason registration, request_status submitted, decided_at "" (0a3d, 9370; submitted 2026-10-01).
- protection_plans: active HostCover Plus on 10 live listings, Premier on the 2 villas, Essential on the 2 suspended listings.
Reachability: all via `find_customers`, `find_host_accounts`, `find_host_account_events`, `find_stays` (confirmation code from the persona), `find_listings`, `find_listing_events`, `find_listing_reinstatement_requests`, `find_protection_plans` after `verify_customer_identity` (persona gives phone and ID last4).

### policy_self_consistency (this task only)

- Charter-global conclusions cited, not restated: `_difficulty.md` § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders.
- Handling time: enrollment on the opening world at 2026-10-06 ("the date of the enrollment"); re-rating after the enrollment write (variant_name Professional Host Plus, last_tier_change_date 2026-10-06) at 2026-10-06 ("the re-rating").
- Real-world waits: none. The two reinstatement requests are counted in their recorded state ("submitted and still undecided") by the rule itself; nothing waits on their decision. The enrollment is a synchronous user write; the refund a synchronous agent write.
- **Consequence of `_difficulty.md` finding D-1 on this world (SOURCE-POLICY RED):**
  - Reading A (base text left undeclared): Professional Host Plus `entry_gate` "{live_listings_at_least: 25, min_avg_rating: 4.70}" and `parameter_schema` "professional_plus_min_live_listings: int, live listings needed for Professional Host Plus" / "professional_plus_min_avg_rating: decimal stars, lowest average guest rating for Professional Host Plus". The account has 12 live (listed or snoozed) listings and a listing rating of 4.57–4.66 → it does not qualify → it already holds the professional tier its records qualify it for (Professional Host) → tier_pct 15.50 is not lower than the 15.50 % the stay was assessed at → no re-rating, no enrollment, no refund; the fee of 536.30 is confirmed correct.
  - Reading B (extended rule): Professional Host Plus (below), refund 46.71.
  - The two passages reach different conclusions on the same world, and no overwrite names the entry_gate or the parameter meanings.

### problem_chain

- Root: "the host service fee taken on the stay that checked in on October 3 ... looks higher than you expected, and you would like it checked and corrected if it is wrong" → the only extended policy that refunds part of a host service fee assessed on a stay of an account with no host-funded guest refund is host_ext_professional_fee_rerating (target refund_rerated_host_fee_9248fd19, owner agent). The base refund path (host-funded guest refunds after payout release) has no guest refund in the world.
- Its prerequisite sentence: "A host service fee is not re-rated until the account holds the professional tier that its live listings and listing ratings qualify it for." At 2026-10-06 the account holds Professional Host; the enrollment computation over its records qualifies it for Professional Host Plus (below). False at the opening.
- Which write brings it about: the enrollment rule ("An enrollment places the account in Professional Host Plus when ...", "moves into Professional Host Plus only when the host enrolls it in person") → host_ext_professional_plus_enrollment, target enroll_professional_tier_a874e389, owner user. Its rule carries no prerequisite sentence.
- Derived tree: nodes {rerating (root, agent), enrollment (user)}; edge rerating → enrollment, kind value_input (tier_pct; also moved_on feeds the tier start); order: enrollment, then re-rating. n = 1, value_input edges = 1 ≥ 1. Acyclic. One owner=user write (the enrollment).
- Load-bearing run: skip the enrollment → tier_pct 15.50, gate "tier's host_service_fee_pct is lower than the percentage the stay was assessed at" (15.50 < 15.50) false → 0.0, no refund. With it → 46.71. Bears weight.
- Parallel edges: none.
- Tool layer: `enroll_professional_tier_a874e389` only `ctx.update`s; `refund_rerated_host_fee_9248fd19` only looks up customer_id and `ctx.create`s (task_tools.py L113–116, L146–159); neither checks the tier. PASS.
- Persona: raises only the fee on one stay; the listing facts it may give (about a dozen homes, a few added this year, two waiting on registration paperwork) come only "If the agent asks about your listings". "If the agent explains that your account first has to be enrolled or moved into something and that you have to do that yourself, you agree" is passive and conditioned on the agent. Persona closes once the refund is confirmed booked — where the derived solution closes. PASS.

### task_independent_derivation

1. Need/authorisation/timing: check and correct, if wrong, the host service fee on stay HPQ7M2XW4L now; she will enrol herself if told she has to; she accepts a refund. Expressed.
2. Now/wait/refuse: act now (both writes synchronous; the stay's fee is already assessed).
3. Objects: host account af38dd1e-2ab8-4f5f-9cd5-3530accc2887; stay da444220-b524-4628-b0d3-b680e36aba62; fee row 62b96310… (2026-10-03, base 3460.00, fee 536.30).
4. Step 1 — `verify_customer_identity(customer_id=37f50368-86df-49a8-94d3-fc2f4bcc0c59, phone_number=6195553178, government_id_last4=3741)` (agent).
5. Step 2 — enrollment (opening world, 2026-10-06):
   - live-listing count: registration-suspended listings with submitted, undecided reinstatement requests = 2 → listed 11 + snoozed 1 + 2 = **14** (baseline 12).
   - live-listing requirement: business_name present; Entire Home/Luxury Villa among listed+snoozed = 6 + 2 = 8 of 12 = 66.7 % ≥ 50 → live_requirement_home_heavy **14** (baseline 25).
   - listing rating: listed listings first listed within 6 whole months = 0f5c (2026-06-10, 3 months), dce7 (2026-07-15, 2 months), de69 (2026-10-02, 0) = 3 ≥ 2 → average of 3-month quality ratings with outcome pass or warning = 41.94 / 9 = **4.66** (baseline: all 11 ratings of the 3 months, 50.29 / 11 = 4.57).
   - rating floor: quality assessments dated within 12 whole months — the 2025-10-01 warning is exactly 12 whole months back and excluded → no warning/suspension → rating_floor_clean **4.60** (baseline 4.70).
   - 14 ≥ 14 and 4.66 ≥ 4.60 → **Professional Host Plus**.
   - write (handed to the host): `enroll_professional_tier_a874e389(host_account_id=af38dd1e-2ab8-4f5f-9cd5-3530accc2887, variant_name="Professional Host Plus")` (owner user). Effect: last_tier_change_date 2026-10-06.
6. Step 3 — re-rating (after the enrollment, 2026-10-06):
   - tier pct 15.00 (Professional Host Plus) < 536.30 / 3460.00 = 15.50 % → gate open.
   - tier start: qualifying date = first-listed date of the most recently first-listed listed listing = de69 2026-10-02; 2026-10-02 → move 2026-10-06 = 4 days < backdate_days 30 → tier start **2026-10-02** (baseline: move date 2026-10-06). Stays assessed on/after 2026-10-02: only da444220 (2026-10-03); 3a2b9279 (2026-09-28) and earlier are excluded. One refund.
   - starting pct: base 3460.00 ≥ 2500 and < 5000 → mid_booking_pct **14.75** (baseline 15.00).
   - tenure: opened 2020-03-02 → 79 whole months ≥ 60 → **0.25** (baseline 0).
   - Instant Book: 10 of 12 listed+snoozed = 83.3 % ≥ 75 → **0.20** (baseline 0).
   - HostCover: active Plus/Premier/Elite/Estate plans = 10 + 2 = 12 ≥ 12 listed+snoozed → **0.15** (baseline 0).
   - re-rated pct = 14.75 − 0.25 − 0.20 − 0.15 = 14.15; re-rated fee = 3460.00 × 14.15 % = 489.59.
   - refund = 536.30 − 0.00 − 489.59 = **46.71**.
   - on the opening world (before enrollment): 0.0 (gate closed at 15.50).
   - write: `refund_rerated_host_fee_9248fd19(host_account_id=af38dd1e-2ab8-4f5f-9cd5-3530accc2887, stay_id=da444220-b524-4628-b0d3-b680e36aba62, fee_base_amount=3460.00, amount=46.71)` (agent).
7. Sequence: verify_customer_identity (agent) → enroll_professional_tier_a874e389 (user) → refund_rerated_host_fee_9248fd19 (agent). Terminal: Professional Host Plus since 2026-10-06; one host_service_fee_refunded row for da444220, base 3460.00, amount 46.71.
8. Closest alternatives:
   - Reading A of D-1: no enrollment, no refund (SOURCE-POLICY RED, above).
   - "the fee was assessed correctly at the tier held at check-in, so nothing is wrong": excluded only by the prerequisite sentence's implication that the fee is re-rated once the account holds the tier its records qualify it for; the customer did not ask for an enrollment (enrollment `trigger: on_request`), but the persona authorises it when the agent explains it — observation T1-O1.
   - backdated tier start (2026-09-06): would add 3a2b9279, 9b572bb8, e0076f27; excluded by "fewer than backdate_days calendar days before the move" → tier start is the qualifying date.
   - live listings 14 (enrollment count) for the Instant Book / HostCover shares: excluded by "the account's listed and snoozed listings" (12); with 14 the HostCover discount would fall to none (12 < 14) and the refund to 41.52.

### factor_weight

Enrollment (scored value variant_name Professional Host Plus; whole-baseline fall-back: 12 < 25 → Professional Host ≠ derived):

| factor | label honest | tier / rows | baseline per baseline.rule | value under its baseline |
| --- | --- | --- | --- | --- |
| pending_reinstatement_live_count | method (composition of the count) — yes | tier 1: reinstatement requests 0dc5b79d…, c793a828… submitted, undecided | listed+snoozed 12 — matches | 12 < 14 → Professional Host (bears) |
| portfolio_mix_live_requirement | parameter — yes; multi-source | tier 1: business_name + 8/12 home/villa (listings rows) | 25 — matches | 14 < 25 → Professional Host (bears) |
| new_listing_rating_window | method — yes | tier 1: 3 new listed listings (0f5c, dce7, de69) | 3-month all-outcome average 4.57 — matches | 4.57 < 4.60 → Professional Host (bears) |
| quality_record_rating_floor | parameter — yes; multi-source | tier 1: no warning/suspension within 12 months | 4.70 — matches | 4.66 < 4.70 → Professional Host (bears) |

Re-rating (scored amount 46.71; whole-baseline fall-back: tier start = move date 2026-10-06 → stay of 2026-10-03 not re-rated → **0.00**, a definite answer ≠ 46.71):

| factor | label | tier / rows | baseline | amount under its baseline |
| --- | --- | --- | --- | --- |
| qualifying_date_tier_start | method — accepted (tier 1 sources the anchor from listings; see `_difficulty.md` D-O13) | tier 1: listing de690f66… first_listed_date 2026-10-02, move 2026-10-06 | move date — matches | 0.00 |
| booking_size_start_pct | parameter — yes | tier 2: fee row base 3460.00 | tier pct 15.00 — matches | 38.06 |
| account_tenure_discount | parameter — yes | tier 1: host_accounts.opened_date 2020-03-02 (79 months) | 0 — matches | 38.06 |
| instant_book_discount | parameter — yes; cross listing | tier 1: 10/12 instant_book | 0 — matches | 39.79 |
| hostcover_discount | parameter — yes; multi-source; cross protect | tier 1: 12 Plus/Premier plans vs 12 live | 0 — matches | 41.52 |

- Stamps: none. No field names "qualifies for Plus" or a discount tier; tiers rest on counts, dates and holdings.
- Cross-difficulty evidence seeded: listings, listing_events, listing_reinstatement_requests (listing difficulty) and protection_plans (protect difficulty) are present for this customer and conform to their charters: Entire Home thresholds 4.00/4.30, min reviews 5 (blueprint/products/listing.yaml) agree with pass ≥ 4.30, the 4.22 warning and the not_assessed rows; notice 2026-08-31 + 15 cure days = 2026-09-15, suspension 2026-09-16; plan levels are protect variants. Observation T1-O2: the listing charter assesses "every listing that is listed, snoozed or unlisted ... on the quality_assessment_schedule dates" (quarterly), but the seed carries only the 2026-10-01 round and one 2025-10-01 row — the 2026-01/04/07 rounds are absent, so the rating-floor tier "no warning or suspension within 12 months" rests on an incomplete quarterly history; no scored consequence is demonstrable (the 3-month windows contain only the 2026-10-01 round either way).
- Near-miss: enrollment — the not_assessed ratings (excluded by tier 1, including them gives 4.57 and flips the result), the 2025-10-01 warning (12 whole months back, excluded), the suspended listings (excluded from listed/snoozed, counted only through their pending requests). Re-rating — the stays assessed 2026-09-28 and earlier (excluded by the tier start), the Essential plans on suspended listings (not Plus-level), the suspended listings (not listed/snoozed).
- Counts surviving: enrollment 4 (2 parameter, 2 method); re-rating 5 (4 parameter, 1 method); task-level multi-source ≥ 1, cross-difficulty ≥ 1 (listing, protect). PASS.
- Realism (cited, `_difficulty.md` D-O15, D-O16): the prerequisite admits a ~12-listing portfolio to a programme the charter sizes at 25; the re-rated rate (14.15 %) sits below the new tier's own 15.00 %.

Frozen verdict before reveal: policy self-consistency **SOURCE-POLICY RED** (D-1 consequence above); problem tree PASS; factors PASS; unique solution under reading B PASS (observations T1-O1, T1-O2).

## source_gt_comparison

- Reveal: `tasks/1.json` opened 2026-10-07T19:22Z, after `tasks/0.json` and after the hash record of all frozen files at 2026-10-07T19:21:25Z (`task_1.md` 5e8d999d583aa793fd3bce931f1ece90a4cda0a462f3185d5d2f73e40170a9b6). Timestamp correction: the "freeze time 19:40Z" line above was an estimate written before the reveal; the hash record is the true freeze and precedes it.

| item | frozen derivation | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | check/correct fee on HPQ7M2XW4L now; host enrols herself if told | request_alignment; intent_source user_scenario passive enrollment line | same |
| read set | customer, host account, events, stays, listings, listing events, reinstatement requests, protection plans | find_customers, verify, find_host_accounts, find_host_account_events, find_stays, find_listings, find_listing_events, find_listing_reinstatement_requests, find_protection_plans | same |
| now / wait / refuse | act now | act now | same |
| object | account af38dd1e…, stay da444220…, base 3460.00 | same | same |
| enrollment variant_name | Professional Host Plus | Professional Host Plus | same |
| enrollment intermediates | 14 / 14 / 4.66 / 4.60 | 14 / 14 / 4.66 / 4.60 | same |
| refund fee_base_amount | 3460.00 | 3460.0 | same |
| refund amount | 46.71 | 46.71 | same |
| re-rating intermediates | tier start 2026-10-02; 14.75 − 0.25 − 0.20 − 0.15 = 14.15; fee 489.59 | identical factor_trace | same |
| tool / owner / order | verify (agent) → enroll (user) → refund (agent) | unlock_user + user call enroll → unlock + call refund | same |
| terminal state | Professional Host Plus since 2026-10-06; one refund row 46.71 on da444220 | same | same |

Problem tree vs `prerequisite_closure`: root host_ext_professional_fee_rerating = mine; edge rerating → enrollment, value_input, gate tier_pct, form state, policy_source identical; why_false rows (variant_name Professional Host, last_tier_change_date 2021-05-17, request 0dc5b79d… submitted, listing de690f66… first listed 2026-10-02) — same facts I used; resolution_order [enrollment, rerating] = mine; edge_load_bearing "0.00 instead of 46.71" = my skip run. Same.

`factor_weight` vs `factor_sensitivity` / `baseline_result`:
- enrollment: Professional Host ×4 / Professional Host ×4; whole baseline Professional Host / Professional Host. Same.
- re-rating: qualifying_date_tier_start 0.00 / 0.0; booking_size_start_pct 38.06 / 38.06; account_tenure_discount 38.06 / 38.06; instant_book_discount 39.79 / 39.79; hostcover_discount 41.52 / 41.52; whole baseline 0.00 / 0.0. Same.

Closest candidates and exclusion: (i) "the 15.50 % fee is correct for the tier held; nothing to correct" — GT lists it as an easy mistake; excluded by the prerequisite sentence plus the enrollment rule (the account's records qualify it for Plus), with the persona's passive consent covering the hand-over (observation T1-O1); (ii) backdated tier start (2026-09-06) — excluded by "fewer than backdate_days"; (iii) 14 counted listings for the discount shares (41.52) — excluded by "listed and snoozed". The D-1 reading (Plus not reached; no refund) is NOT excluded by any declared overwrite — see findings.

World-assertion check of the proof fields: "No other write moves an account into a professional tier" (solvability_contract step 10 action_semantics) and "task 0's tier write only records Superhost decisions" (design_rationale §2) are true of the policies but not of the tool module: `apply_superhost_decision_f25b833f` accepts and writes `variant_name="Professional Host Plus"` (docstring enum, body `ctx.update` with no check). The policy text resolves the hop ("only when the host enrolls it in person"), so no second scored solution follows; recorded as observation T1-O3 (`_difficulty.md` D-O6). All other spot-checked assertions (66.7 %, 41.94 / 9, 50.29 / 11, 79 months, 10/12, 12 ≥ 12, 489.59) are true.

Verdict: policy self-consistency **SOURCE-POLICY RED** (D-1, demonstrated below); problem tree PASS; factors bear weight PASS; unique solution PASS on the extended reading.

## findings

**T1-1 — SOURCE-POLICY RED (consequence of `_difficulty.md` finding D-1 on this task)**
- Symptom: the merged charter gives two incompatible answers to "does Harbor & Pine Stays qualify for Professional Host Plus, and is the fee on HPQ7M2XW4L to be re-rated?".
- Root cause: base `variants[Professional Host Plus].entry_gate: {live_listings_at_least: 25, min_avg_rating: 4.70}` and `parameter_schema` "professional_plus_min_live_listings: int, live listings needed for Professional Host Plus" / "professional_plus_min_avg_rating: decimal stars, lowest average guest rating for Professional Host Plus" are not named in host_ext_professional_plus_enrollment's `overwrite` (`_difficulty.md` § override_declarations, D-1).
- Evidence: host.extended.yaml L336, L76, L77 vs the enrollment rule (L1565–1570 requirement 14/19; L1576–1579 floor 4.60/4.65); world: 12 listed/snoozed listings, rating 4.57–4.66.
- Demonstrated consequence: reading A → 12 (or 14) < 25 and 4.66 < 4.70 → not Plus → the account already holds the tier its records qualify it for → tier_pct 15.50 is not below the assessed 15.50 % → no enrollment, no refund, fee confirmed. Reading B → enrollment to Professional Host Plus and refund 46.71 (= GT). Two answers on the same world.
- Affected: `host.extended.yaml` overwrite list of host_ext_professional_plus_enrollment; scored parts: step 10 (existence, variant_name), step 12 (existence, amount).
- Relation to previous revisions: first audit.

Observations (no RED):
- T1-O1 the customer asks only for a fee check; the enrollment that unlocks the correction is the agent's proposal (`trigger: on_request` on the enrollment) accepted through the persona's passive line — coherent, but the "fee is correct as assessed" stop is a natural reading for an agent that does not walk the enrollment rule.
- T1-O2 the listing quality history is incomplete against the listing charter's quarterly schedule (only the 2026-10-01 round plus one 2025-10-01 row).
- T1-O3 the agent-owned Superhost tool can write Professional Host Plus (D-O6); the proof's "no other write" holds only at the policy layer.
- T1-O4 realism (`_difficulty.md` D-O15, D-O16): the prerequisite admits a ~12-listing portfolio into a programme sized at 25 by the charter, by stacking three reliefs; the re-rated stay ends at 14.15 %, below the new tier's own 15.00 %.

---

## revision_2

### source_derivation_frozen (revision_2)

- auditor: same independent auditor; written from 2026-10-07T21:27:24Z (clock read), before round-2 `tasks/1.json` was opened
- view: `/tmp/erl45_views/r2/host_standing_and_penalties/task_1.view.json` sha256 c1d5de0a75063c2c5d917fa3c34294e82c8bb6e140f1a3c416dd2a067965355c; charter f59f802c…3c93c180; tools 23e4adf0…a97b2ff
- masked: round-2 `tasks/1.json` beyond the view; worklogs.
- contamination_disclosure: round-1 GT of this task was read in round 1 (round-1 world had 12 live listings; gold Professional Host Plus, refund 46.71 on base 3460.00). The round-2 world (26 listings, 74 listing events, 26 plans) and the round-2 enrollment policy differ; the derivation below is recomputed from them, cross-checked by evaluating the policy's own compute on the view (temporary script, removed).

World (from the view): account af38dd1e… Professional Host, opened 2020-03-02, business Harbor & Pine Stays LLC, last tier change 2021-05-17, restricted_until "". Listings: 23 listed, 1 snoozed (bcbd, Entire Guest Suite), 2 suspended for registration (0a3d, 9370, 2026-09-16) with two submitted, undecided registration reinstatement requests; 15 listed listings first listed 2026-01-20 … 2026-10-02 (newest de690f66… 2026-10-02); Instant Book off on 61d2, b981, dce7. Quality rounds: 2026-01-01 (10 pass + 1 warning on 9115b39d, 4.25, 31 reviews), 2026-04-01 (14 pass + 2 not_assessed), 2026-07-01 (19 + 3), 2026-10-01 (20 + 3). Seed check: every quality row's outcome reproduces from the listing charter's per-space-type thresholds and minimum reviews (0 mismatches), and every round covers exactly the listings listed/snoozed on its date (11 / 16 / 22 / 23) — T1-O2 closed. Plans: 22 Plus + 2 Premier on live listings, 2 Essential on the suspended ones. Fee rows and stays unchanged from round 1 (latest: stay da444220… HPQ7M2XW4L, 2026-10-03, base 3460.00, fee 536.30 at 15.50 %). Persona now says "about two dozen homes and apartments", "added quite a few this year".

#### policy_self_consistency (this task, revision_2)

- Charter-global conclusions: cited from `_difficulty.md` § revision_2.
- Round-1 T1-1 re-tested: the enrollment now compares with 25 live listings and 4.70 — the Professional Host Plus `entry_gate` values. The live-listing count (26 with the two pending registration reinstatements) and the listing rating (round-averaged, not_assessed half-weighted) are defined inside the declared-superseded Plus clause. A base-gloss reading "live = listed or snoozed" (from `max_active_listings`) would give 24 < 25; that residue is ruled an observation (`_difficulty.md` R2-O3) on the same line as D-1(b): the clause that named the measure is declared superseded and the published threshold is kept. **T1-1 closed.**
- Handling time: enrollment on the opening world 2026-10-06; re-rating after it. No real-world wait (requests are counted as "submitted and still undecided", nothing awaits their decision).

#### problem_chain (revision_2)

- Root: re-rating (agent). Prerequisite sentence unchanged; the account holds Professional Host while its records qualify it for Plus (below) → false at the opening. Resolving write: enroll_professional_tier_a874e389 (user), the only tool whose enum admits Professional Host Plus.
- Tree {rerating → enrollment}, value_input tier_pct, order enrollment → rerating, n = 1, one user write, acyclic. Skip the enrollment → tier_pct 15.50, gate closed → 0.00. Tools judge nothing. Persona raises only the fee; passive enrollment consent; closes after the refund. PASS.

#### task_independent_derivation (revision_2)

1–3. As round 1 (fee check on HPQ7M2XW4L; act now; account af38dd1e-2ab8-4f5f-9cd5-3530accc2887, stay da444220-b524-4628-b0d3-b680e36aba62).
4. `verify_customer_identity(customer_id=37f50368-86df-49a8-94d3-fc2f4bcc0c59, phone_number=6195553178, government_id_last4=3741)`.
5. Enrollment (opening world, 2026-10-06):
   - live-listing count: 2 pending registration reinstatements → 23 + 1 + 2 = **26** ≥ 25 (baseline 24).
   - rating window: opened 2020-03-02, 79 whole months ≥ 60 → **9 months** (baseline 3): rounds 2026-04-01 (6 months back), 2026-07-01, 2026-10-01; the 2026-01-01 round is 9 whole months back, excluded.
   - not_assessed weight: the 2026-01-01 warning is 9 months back, inside the 12-month record; no suspension outcome → **0.5** (baseline 1.0).
   - aggregation: 15 listed listings first listed within the 9-month window ≥ 2 → mean of per-round weighted averages: Oct (91.93 + 0.5 × 12.10) / (20 + 1.5) = 4.5572; Jul (90.20 + 0.5 × 12.30) / (19 + 1.5) = 4.7000; Apr (68.76 + 0.5 × 8.20) / (14 + 1.0) = 4.8573; mean 4.70485 → **4.70** ≥ 4.70 (baseline pooled 3-month, weight 1: (91.93 + 12.10) / 23 = 4.52).
   - → **Professional Host Plus**. `enroll_professional_tier_a874e389(host_account_id=af38dd1e-2ab8-4f5f-9cd5-3530accc2887, variant_name="Professional Host Plus")` (user).
6. Re-rating (after the enrollment, 2026-10-06): tier 15.00 < 15.50; qualifying date 2026-10-02 (de690f66…), 4 days before the move → tier start 2026-10-02 → only da444220 (2026-10-03) re-rated; start 14.75 (base 3460.00); tenure −0.25 (79 months); Instant Book 21 / 24 = 87.5 % → −0.20; HostCover Plus-or-higher 24 ≥ 24 live → −0.15; re-rated 14.15 % → fee 489.59 → refund **46.71**. `refund_rerated_host_fee_9248fd19(host_account_id=af38dd1e-2ab8-4f5f-9cd5-3530accc2887, stay_id=da444220-b524-4628-b0d3-b680e36aba62, amount=46.71)` (agent; the tool no longer takes a base).
7. Order: verify → enroll (user) → refund (agent). Terminal: Professional Host Plus since 2026-10-06; one refund row 46.71, fee_base_amount 0.0.
8. Closest alternatives: listing rating rounded per round (4.56 / 4.70 / 4.86 → 4.71) — same outcome; the rule says rounding "only at the end". Counting the 2026-01-01 round in the window (MONTHS = 9, excluded) — not done. Fee confirmed correct without enrollment (T1-O1, unchanged observation).

#### factor_weight (revision_2)

Enrollment (gold-as-derived Professional Host Plus; whole baseline Professional Host — 24 < 25):
| factor | label | tier / rows | baseline | under its baseline |
| --- | --- | --- | --- | --- |
| pending_reinstatement_live_count | method | tier 1: requests 0dc5b79d…, c793a828… | 24 | 24 < 25 → Professional Host |
| tenure_rating_window | parameter | tier 1: opened 2020-03-02 | 3 months | 4.56 (latest round only) < 4.70 → Professional Host |
| quality_record_not_assessed_weight | parameter; multi-source | tier 2: warning 2026-01-01, no suspension | 1.0 | rating < 4.70 → Professional Host |
| new_listing_round_averaging | method | tier 1: 15 new listed listings | pooled 4.69 | 4.69 < 4.70 → Professional Host |

Re-rating (46.71; whole baseline 0.00): tier start → 0.00; booking size → 38.06; tenure → 38.06; Instant Book → 39.79; HostCover → 41.52.
- Stamps: none. Near-misses: the 2026-01-01 round (outside the 9-month rating window, inside the 12-month warning record); not_assessed rows (weighted); suspended listings (counted only through pending requests; excluded from Instant Book / HostCover denominators); 2026-09-28 and earlier stays (before the tier start).
- Counts: enrollment 4 (2/2), rerating 5 (4/1); multi-source and cross-difficulty (listing, protect) present. PASS.

Frozen verdict (revision_2, before reveal): policy self-consistency PASS (T1-1 closed); problem tree PASS; factors PASS; unique solution PASS.

### source_gt_comparison (revision_2)

- Reveal: round-2 `tasks/1.json` opened 2026-10-07T21:28Z, after the revision_2 hash record at 21:27:55Z (`task_1.md` 7e38c4941e35a276f146aefa40198d28deaaef628a609addad76ae1d204fc79c).

| item | frozen (r2) | GT (r2) | same? |
| --- | --- | --- | --- |
| read set | customer, account, events, stays, listings, listing events, reinstatement requests, plans | same nine reads | same |
| enrollment call | (af38dd1e…, Professional Host Plus), user | identical, user | same |
| enrollment intermediates | 26; 9 months; weight 0.5; 4.5572 / 4.7000 / 4.8573 → 4.70 | identical | same |
| refund call | (af38dd1e…, da444220…, 46.71), agent | identical, agent | same |
| refund intermediates | tier start 2026-10-02; 14.75 − 0.25 − 0.20 − 0.15 = 14.15; 489.59 | identical | same |
| order / owners | verify → enroll (user) → refund (agent) | same | same |
| terminal | Professional Host Plus; refund 46.71 | same | same |

- Problem tree vs `prerequisite_closure`: same root, edge (value_input, tier_pct, state, same policy_source), resolution_order, why_false rows, load-bearing (0.00 vs 46.71). Same.
- factor_weight vs factor_sensitivity / baseline_result: enrollment Professional Host ×4 and whole baseline Professional Host — same (GT gives the not_assessed-weight baseline as 4.66; recomputed: (4.5230 + 4.6591 + 4.8100) / 3 = 4.664 → 4.66, true); re-rating 0.00 / 38.06 / 38.06 / 39.79 / 41.52, whole 0.00 — same.
- Closest candidate exclusion: per-round rounding (4.71) gives the same outcome; "fee correct, stop" excluded by the prerequisite sentence and the enrollment rule (T1-O1, observation unchanged); live count 24 by the `max_active_listings` gloss — ruled observation R2-O3.
- Proof-field assertions spot-checked (26 / 24; 21 of 24; 24 Plus-or-higher; 2026-01-01 round 9 whole months back; four complete rounds) — all true.
- Verdict (revision_2): **PASS** — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS.

### findings (revision_2)

| id | claim | verified |
| --- | --- | --- |
| T1-1 (SOURCE-POLICY RED) | changed | **closed** — enrollment compares with the published 25 / 4.70; the counted figures sit inside the declared-superseded Plus clause |
| T1-O1 (customer did not ask to enrol) | no change | unchanged, observation |
| T1-O2 (incomplete quarterly quality history) | changed | **closed** — four complete 2026 rounds; 0 outcome mismatches against the listing charter |
| T1-O3 (Superhost tool could write Plus) | changed | **closed** — enum now excludes professional tiers |
| T1-O4 (realism) | (via D-O15 / D-O16) | D-O15 closed in substance (26 counted listings for a 25-listing programme); D-O16 unchanged (re-rated 14.15 % below the tier's 15.00 %) |

New: none RED. Observations R2-O3 (live-listing gloss), R2-O5 (not_assessed weight fall-through) bear on this task. Regressions: none found.

---

## revision_3

### source_derivation_frozen (revision_3)

- written ~2026-10-07T22:40Z, before round-3 `tasks/1.json` was opened; view `/tmp/erl45_views/r4/host_standing_and_penalties/task_1.view.json` sha256 b20d57119be55666947fd1286b646f5a261948b3eb58ee6b654a5fb0e17573d1; charter and tools unchanged (see `_difficulty.md` § revision_3).
- contamination_disclosure: round-1 and round-2 GT of this task were read in earlier rounds (disclosed there).
- Only change in the view: frozen_time → '2026-10-06 14:30:00 PDT' (user_scenario and initial_state byte-identical to revision_2's view). Date part unchanged (2026-10-06), zone is the customer's local daylight zone; every clock consumer reads the date part only (`_difficulty.md` § revision_3, frozen_time format change).
- policy self-consistency, problem tree, factor weight, task derivation: carried forward from `## revision_2` of this file by reference — every input they rest on (charter, tools, user_scenario, initial_state, date) is identical; re-evaluated compute confirms the same values.
- Expected solution (unchanged): enroll_professional_tier_a874e389(af38dd1e…, Professional Host Plus) (user) → refund_rerated_host_fee_9248fd19(af38dd1e…, da444220…, 46.71) (agent); factor and whole-baseline figures as revision_2.
- Frozen verdict (revision_3, before reveal): PASS on all four relationships.

### source_gt_comparison (revision_3)

- Reveal: round-3 `tasks/1.json` opened 2026-10-07T22:40Z, after the revision_3 frozen sections of all three files were hashed at 2026-10-07T22:39:44Z (`_difficulty.md` 580fd1e9…44f21, `task_0.md` c3712f4a…05251, `task_1.md` 404d03f5…ea43c). Clock correction: "written ~22:40Z" in the frozen section above is an estimate; the hash record at 22:39:44Z is the true freeze and precedes the reveal.
- GT vs revision_2 GT (as recorded in this file's revision_2 comparison), item by item: frozen_time '2026-10-06 14:30:00 PDT'; evaluation_criteria — same tool sequence and owners, write arguments identical: steps 11 (user, enroll Professional Host Plus) and 13 (agent, refund 46.71 on da444220…); computations Professional Host Plus / Professional Host / Professional Host ×4, and 46.71 / 0.0 / 0.0, 38.06, 38.06, 39.79, 41.52; prerequisite_closure — same root, edge, kind, gate and resolution_order; charter_scope identical; no residual '2026-10-06T' stamp anywhere in the file. File size 340885 → 340889 bytes, exactly the +4 of the frozen_time rewrite.
- Frozen expectation vs GT: same on every item.
- Verdict (revision_3): **PASS** — policy self-consistency PASS, problem tree PASS, factors bear weight PASS, unique solution PASS.

### findings (revision_3)

- Round-2 RED to close: none existed. The frozen_time rewrite is verified as format-only: the date and local time are unchanged, the zone is the customer's, every consumer reads the date part, and every scored value and baseline is unchanged. No new defect, no regression. Observations carried from revision_2 unchanged.
