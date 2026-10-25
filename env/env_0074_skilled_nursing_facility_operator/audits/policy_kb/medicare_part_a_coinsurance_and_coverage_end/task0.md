# Policy-KB bijection audit — medicare_part_a_coinsurance_and_coverage_end / task 0

## revision_1

Scope: policies on task0's path — `medicare_ext_resident_block_share` (target `post_coinsurance_charge_97c12690`) and `medicare_ext_card_payment_share` (target `pay_coinsurance_by_card_ebeca5a6`), their base refs (`medicare_evt_coinsurance`, `medicare_evt_secondary_and_qmb`, `medicare_evt_payment_posting`, `medicare_coverage_tier_change`, `medicare_evt_day_counting`), the variant figures they read, and the two tool contracts. Corpus `docs/medicare` 56 files, tree sha256 `ece4e204…`; source `medicare.extended.yaml` `203ecd58…`, `task_tools.py` `91fc2fae…`. Method: sentence-level verbatim location of every `rule` sentence of both policies and of every base-policy rule (script `/tmp/erl0074_kbaudit_mpa/scripts/sentcheck.py`), then manual entailment reading of every non-verbatim sentence, every factor ladder and every variant figure.

## source_to_kb

### medicare_ext_resident_block_share
- Rule sentences (17): all located verbatim. Hub: `original_coinsurance_charge_posting` (subject, state_due "falls due once that block stands booked", tool contract). Computation doc `resident_coinsurance_charge_computation`: latest-block selection, record test, overwrite replaced_by, baseline (217.00, earlier share 100, covered days, days-before rule, shares, sum/100 half-up once), supplemental-date reading, "Each kind of day named below…", LOA clause (rule clause, not a declared factor), block-before definition.
- baseline.rule: carried complete; params rate_2026 = 217.00, share_none = 100 rendered; nothing added.
- Factors (each in its own doc, full ladder, result named, nothing referencing another document):
  - f_year_rate -> `resident_charge_rate_year`: 2025 -> 209.50; 2024 -> 204.00; otherwise 217.00. Exact. Read from the booked-days entry's last service date.
  - f_carried_split -> `resident_charge_earlier_share`: 50 / 25 (within half a percentage point) / 0 (secondary charge, no resident charge) / 100 otherwise; block before and "not a rebill" definition carried. Exact.
  - f_held_nights -> `resident_charge_bed_hold_nights`: all / from first to day before / none / no leave -> none; names "Bed-Hold and Leave Reservations records" (official product name) and the record kind (held days booked for the same service month). Exact.
  - f_hospital_reversal -> `resident_charge_hospital_day_reversals`: three tiers exact.
  - f_uncertified_days -> `resident_charge_uncertified_days`: both compound tiers with "less the held nights and the hospital-day and leave-of-absence days inside" carried; otherwise none. Exact.
- prerequisite: [] — no document attributes a wait to the charge posting. Correct.
- Retired surface (overwrite on `medicare_evt_coinsurance`): superseded clause carried in `coinsurance_block_pricing` under "Retired clause — no longer in force", with "The rest of this rule remains in force"; the other clauses of `medicare_evt_coinsurance` (year-of-service rate, block total, split, rounding, days 1-20 never charged, once per party) carried as in force. replaced_by carried verbatim in all five computation documents. No undeclared retirement found.
- Variant figures read: resident share by tier (100/100/50/25/0/0) `cost_sharing_split_by_tier`; rates 2025 209.50 / 2026 217.00 `daily_coinsurance_rate_schedule`; half-up per row; bands 1-20 / 21-100 `benefit_period_day_bands`. Exact.
- Tool contract: parameters, formats, error cases and return fields in `original_coinsurance_charge_posting` match `post_coinsurance_charge_97c12690` docstring and body (agent-owned). Exact.

### medicare_ext_card_payment_share
- Rule sentences (20): all verbatim. Hub `coinsurance_card_payments`: prerequisite sentence, certified-funds sentence, tool contract (user-owned, "the agent unlocks it and hands it over"). Computation `card_payment_amount_computation`: clauses (a)-(i) = baseline + supplemental-date reading + LOA clause + open-balance clause; card maximum 5000.00 rendered.
- Factors: f_year_rate `card_payment_rate_year`; f_carried_split `card_payment_earlier_share`; f_held_nights `card_payment_bed_hold_nights`; f_hospital_reversal `card_payment_hospital_day_reversals`; f_uncertified_days `card_payment_uncertified_days` — every tier exact, as for the resident charge.
- prerequisite (1): policy_source "A card payment toward a coinsurance block is taken only after the records carry a resident coinsurance charge for the coverage's latest booked coinsurance block, whenever that block's covered days take a resident share above nothing under the split in effect on them." — verbatim in `coinsurance_card_payments` (the blocked policy's hub), form state, connective "only after", conditional "whenever…" intact; appears in no other document. Resolution basis: depended-on hub `original_coinsurance_charge_posting` describes the write in the sentence's own words ("the resident's own original charge for the coverage's latest booked coinsurance block … adds one charge entry … names the booked-days entry it prices and the party billed"); records: ledger has `medicare_coinsurance_charge` rows with `liable_party`, `days_entry_id`. Same strength. `condition` / `resolved_by` / `effect` appear nowhere.
- Base `medicare_evt_payment_posting`: all sentences carried in `payment_posting_and_returned_payments` (the "medigap_remittance / medicaid_crossover_remittance" sentence rendered as "a Medigap remittance or a Medicaid crossover remittance" — equivalent); figures (methods, 5000.00, 2 in 12 months, certified check, day 5, 30 days) in `statements_and_payment_terms`.
- Tool contract: `pay_coinsurance_by_card_ebeca5a6` doc table and return match the source (user-owned). Exact.

## kb_to_source

- Every normative sentence of the 16 path documents traced to a rule sentence, baseline, factor ladder, variant figure, trigger/subject, or tool docstring. Restatements checked for entailment: hub summaries ("the card payment is the amount that settles the resident's share of that block not yet paid"), Q&A and tables of the factor docs, the census truth table — all equivalent.
- Cross-problem operational guidance ("if unmet, first call …"): none. Each tool name appears only in its own hub (`post_coinsurance_charge_97c12690` only in `original_coinsurance_charge_posting`, `pay_coinsurance_by_card_ebeca5a6` only in `coinsurance_card_payments`).
- Opening world state written as policy fact: none (no document states that a December block lacks a resident charge, or that a coverage switched K -> L).
- Added steps / confirmations / reviews: none found.
- Observation (not a defect): a factor-doc example and a computation example reuse seed-like numbers that are not scored: `reversed_day_reduction_computation` example 3 days x 209.50 = 628.50 equals this world's November resident charge `df1b6673` (628.50). No scored value of this task (1885.50, 26, 209.50 as the rate of this block) is stated as a world fact; 209.50 appears only as the published 2025 rate.

## bijection_verdict

**PASS** (KB-BIJECTION). Both policies' complete domains, every tier of all ten factor ladders, the retired surface and both tool contracts correspond losslessly. No previous revision.

## dependency_form

- Prerequisite sentence: verbatim, state form, only in the blocked hub. No action-form restatement, no tool or policy named beside it. Hop P0 -> P1 was state-derived in the blind answer.
- No route, checklist, dependency table or aggregated chain in any document. Titles are general subjects ("Card Payments toward Resident Coinsurance", "Original Coinsurance Charges on a Coverage Episode", factor docs named by the kind of day / figure); none mirrors task0's situation.
- Factor docs: none says which tier customers fall on; each names the figure it modifies; none points at the computation document or at another factor document. The uncertified-day docs subtract held nights and hospital-day/LOA days inside the span — this is the source ladder's own wording (record kinds, not a reference to another factor document).
- Computation docs: their "Record test" paragraph names the block before's 100/50/25-percent billing, the bed-hold leave, the hospital-day/LOA/uncertified reversals and the "2024 or later" floor, and the replaced_by sentence enumerates the five figures of this difficulty. Both are verbatim source rule text (`rule` / `overwrite.replaced_by`) that the KB must carry; recorded as source-side items S1 and S3 in `_kb_verdict.md`, not as KB-EXPLICIT.
- Example scan for task0 mirrors: `card_payment_amount_computation` example 1 uses the Plan L tier (25 percent) with 9 days, no supplemental date, 488.25 — tier coincides with this world but no date, day count or value does; not a mirror. No example contains 1885.50, 26 days, 16 December or a K -> L switch.

**PASS** (KB-EXPLICIT) for task0's path. (Corpus-level finding E1 sits on task1's path; see task1.)

## revision_2

Corpus `21f7544f…` (round-3 render); source unchanged (`203ecd58…`, `91fc2fae…`). Snapshot 2026-10-22T19:39:06 all green (DOCS OK, TRACEABILITY OK 0 misses).

### source_to_kb / kb_to_source
- Diff against revision_1: only hypothetical examples and illustrations changed; every rule sentence, schedule table, factor ladder, prerequisite sentence, tool table and title is unchanged. Sentence-level location re-run: 90/91 extended rule sentences verbatim (the one bank-draft clamp sentence rendered equivalently, as in revision_1); base-rule non-verbatim count unchanged (16, all enum-to-words renderings).
- Every changed example on this task's path re-worked and consistent with its rule: `resident_coinsurance_charge_computation` (QMB tier, 18th-28th, LOA 21st, date 24th: 10 covered days, 5 before at 100 percent -> 1085.00); `card_payment_amount_computation` (Plan A or B, 8 days -> 1736.00 less 236.00 -> 1500.00; example 2 open balance 1414.00 -> not taken); factor examples for held nights (22nd-24th), hospital days (17th-19th), uncertified days (20th-25th, hospital 22nd), earlier share (1519.00 / 14 x 217.00 = 50 percent; 663.00 / 13 x 204.00 = 25 percent), rate-year boundaries (30 April 2025, 28 February 2026; 2024 boundary unchanged); `coinsurance_block_pricing` (QMB, 13 days: 2821.00 to the crossover, zero resident row not posted); schedules' illustrations (census 19th-25th, booking rows 15-23, carrier date 23rd, payment split 815.00). All arithmetic correct; no rule restated or extended.
- Observation (source-borne, see S5 in `_kb_verdict.md`): the two computation examples now place a resident charge (1085.00) and a bank draft (1219.00) on a QMB Medicaid Crossover block with a mid-month supplemental effective date — a faithful application of the extended rules, which carry no balance-billing exclusion, but it sits against the base rule in `secondary_denials_and_qmb_writeoffs` ("the resident is never billed any Medicare cost sharing").

### bijection_verdict
**PASS** — nothing regressed.

### dependency_form
- Mirror/scored-value sweep of all 56 documents for task0 (1885.50, 26 days, Plan L, 16 December, K -> L switch, held 6th-7th, hospital 10th, uncertified 13th-14th, seed figures 628.50 / 3561.50): no example reproduces any; "the 16th" survives only as the "none" boundary of a 17th-19th hospital-day example. The revision_1 Plan L card example is gone.
- Prerequisite sentence, titles, tool-name placement unchanged.

**PASS** (KB-EXPLICIT).

## revision_3

Corpus `77516c68…` (round 4); source `ddc0242f…`; tools `91fc2fae…`. Snapshot 2026-10-23T06:24:59 all green.

### source_to_kb / kb_to_source
- New source atom (S5 rework): each of the five extended `rule`s gains "When the tier on file prohibits balance billing, as the QMB Medicaid Crossover tier does, the <figure> bills the resident nothing for any day on or after the tier's supplemental effective date, those days taking the tier's resident share of nothing, while days before that date keep the earlier split, QMB protection not reaching back before it." It is neither in `baseline.rule` nor a factor. Re-running the sentence location finds it verbatim in each policy's computation document (shares clause: bank draft "Shares", card "(g)", rate-year bullet, resident charge "7.", reduction "7."), and in no other document. Every other rule sentence is still located as in revision_1 (the bank-draft clamp is still rendered equivalently). The base-rule location count is unchanged.
- Rewritten examples, re-worked:
  - Resident charge: tier without supplemental coverage until a QMB determination in April 2026, supplemental effective date 1 May 2026 (consistent with "the first day of the month after the determination month"). April block: 30 booked days, 2 LOA days, all days before the date -> 28 x 217.00 x 100 -> 6076.00. May block 1-19 May: date not after the first service date -> 19 days at 0 -> 0.00. Both correct.
  - Bank draft: Plan A or B -> QMB after a June 2026 determination, date 1 July 2026. June block 1-24 June: 24 days before the date at 100 percent -> 5208.00 less 1208.00 -> 4000.00, open balance 4000.00. Correct.
  - Both examples now agree with the base rule in `secondary_denials_and_qmb_writeoffs`: nothing is billed on QMB-protected days, and the protection starts on the recorded date.
- No added step or claim. Observation only: the new sentence says days before the date "keep the earlier split", while the shares clause next to it says they "take the earlier share". This is source wording and reads consistently: for a passing block the earlier share is read from the block before.

### bijection_verdict
**PASS** — the new atom is carried verbatim, and nothing regressed.

### dependency_form
- Prerequisite sentences, titles and tool placement are unchanged. The new sentence names no other problem, tool or route.
- Sweep for mirrors and scored values (task0: 1885.50, 26, Plan L, the 16th, held 6th-7th, hospital 10th, uncertified 13th-14th; task1: 18.75, 419.00, 104.75, 217.00 on a 2025 block, the 10th, Plan N): none in the new or old examples. The new examples are set in April-July 2026 under the tier without supplemental coverage, Plan A or B and QMB tiers. E1 remains closed.

**PASS** (KB-EXPLICIT).

## revision_4 (cross-product re-judge, 2026-10-23)

- Entry: snapshot 2026-10-23 (`kb_snapshot.sh`): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Source `ddc0242f…`, tools `91fc2fae…` and docs/medicare `77516c68…` are unchanged since revision_3. Other corpora read for this pass: bedhold `24cc3f6d…` (all 50 titles; the 22 non-charge-computation documents in full), private `9c9f001f…` (daily-rate schedule). Also published: medicaid `b89c3e2b…`, trust `600f4bac…`, ancillary `73c2a1c3…`, therapy `d4b962bb…`.
- Other-product holdings: every finder for private, medicaid, trust, ancillary and therapy returns "No … records" for this resident. The only cross-product rows are Bed-Hold and Leave Reservations rows.
- source_to_kb / kb_to_source: medicare corpus and source unchanged since revision_3 -> **PASS** (KB-BIJECTION).
- Cross-product findability: each held-night factor document names "Bed-Hold and Leave Reservations records" and "held days booked for the same service month". The published bedhold corpus uses the same terms ("One held-days entry is booked for each service month and each day payer … its first held day, its last held day and its day count"), so the factor can be reached from the bedhold record words. The bedhold corpus states no Medicare coinsurance rule, so the two products do not contradict each other.
- dependency_form: unchanged -> **PASS** (KB-EXPLICIT).
- Seeded cross-product rows: see `runtime_context/.../task0.md` revision_4. Every row is OK, so there are no new source or seed items.
