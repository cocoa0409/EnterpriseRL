# KB audit verdict — resident_trust_fund_accounts (product trust)

## revision_1

Per-task files: `audits/runtime_context/resident_trust_fund_accounts/{0,1}.md` (blind_answer frozen before reveal, sha256 6df9b58b… / 36640342…; gt_comparison appended), `audits/policy_kb/resident_trust_fund_accounts/{0,1}.md`.
Closing gate re-run (kb_snapshot 2026-10-23T10:39:53, docs unchanged, tree 600f4bac909bd07b): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; [check_docs] DOCS OK; [check_traceability] TRACEABILITY OK (0 misses).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (67.11, 56.11 reproduced blind) | PASS | RED E2 |
| 1 | PASS (486.50, 3280.75, 1837.92, 4595.64 reproduced blind) | RED K1 | RED E1 |

## KB findings (documents)
- **K1** (KB-BIJECTION, P4) bed_hold_night_rate_schedule_f6f4d2fa, row "before 2025-07-01 | the schedule in effect on the date the charge was billed": the source tier's value "(the charge's own daily rate for a charge billed before 2025-07-01)" is missing from the factor document; it appears only in bed_hold_return_computation ("For a charge billed before 2025-07-01 neither schedule below is in effect, no room tier can be priced, and the charge's own daily rate is the nightly rate due"). Judgement call on the memo side is sound (entailed by the compute baseline, same outcome, makes the fall-back definite); the factor ladder is not carried in full in its own document. No effect on task 1's numbers.
- **E1** (KB-EXPLICIT, task 1) block_supplemental_share_3a2d2feb §Hypothetical illustration "Eight owed days … at $209.50 a day: Plan K, no QMB | $838.00" reproduces task 1's coinsurance-owed step and equals seeded Medicare row 5ec43403 (838.00).
- **E2** (KB-EXPLICIT, task 0) run_day_coinsurance_rate_5dbdd3aa §Basis Q&A "The episode's most recent coinsurance charge was priced at $209.50, and the run days fall in 2026. → $217.00" states task 0's evidence configuration (charge 9531985d at 209.50; 2026 run days) and contrasts the default reading with the tier's answer.
- **X1** (example world not producible) payer_covered_return_computation worked example: oxygen concentrator "$58.40 billing 14 days" — the Ancillary corpus prices it at 185.00/month prorated (83.55–92.50 for 14 days) or 0.00; no entailment affected. Partial example coincidences (not red) are listed in the task files.
- Checked and clean: unlock schemas (no example values); scored values appear in no document; every prerequisite sentence verbatim, state form, blocked side only; no tool name/route/chain beyond them; titles general; no factor document names another factor, each names the result it modifies; every factor reachable from record words; every fall-back definite and different (P1 120.00, P2 0.00, P3 1389.70, P4 3186.00, P5 217.00, P6 3831.17/6450.04); no retired surface (no overwrite).

## Source-side list (policy / seed; not KB verdicts)
- **S1** (P4 vs the published Bed-Hold corpus, task 1): the trust "amount due" prices held nights at 100 % of the private rate with no dietary credit, but the Bed-Hold corpus prices this very charge type (single-entry Private Pay Hospital Leave hospital stay charge: hs_base, hs_ext 95 % for 15–30 days, hs_diet 14.10/day for leaves ≥ 4 days) at 13 × 385.85 = 5016.05, not 5473.00. The P4 rule's own premise ("the charge billed more than the hold's own rules let it bill") points a reader to that corpus, whose figure gives excess 4139.95 and return 3687.71 instead of 3280.75. Cross-product contradiction outside the trust KB's single-homed text; the trust memo itself is explicit and unique. (Same divergence would hit the held-night reserves of P2/P6 for leaves ≥ 4 days; not triggered in these worlds.)
- **S2** (P5 baseline, task 1): the compute's baseline filters the booking-error day against the record's last covered date (baseline_result 0.00) although the baseline rule says "every day the charge priced runs to the covered end"; the KB memo, rendering the rule text, gives 217.00. Both differ from 1837.92; no scoring effect.
- **S3** (seed, task 0): Medicare charge 9531985d prices September 2026 days at 209.50 (corpus: 217.00 → 4340.00). Gold's value does not read the rate, but run_year_rate bears weight in task 0 only because of this row; the Medicare corpus forbids a re-bill, so the undercharge stands.
- **S4** (source hygiene): the P2 and P3 source baselines embed factor ladders (run-year rate, first night allowed; month standing) before their "standard method" override; KB correctly renders only the standard method.
- **S5** (seed, task 1): Medicare payment 9e31fcfd records the trust transfer as method "ach" (other products use trust_transfer; the Medicare method list has none). Not load-bearing.
- **S6** (seed, task 0): reservation e2a3bb8b room_tier_held Semi-Private LTC while the converted private agreement (no room change recorded) is Private LTC; the Bed-Hold corpus does not fix where the held tier comes from; held_room_tier's weight (398 vs 436) rests on it. Plausible (move at Part A start), unrecorded.
- **S7** (owed-write window, task 1): the Medicaid reconciliation (trueups 113.30 × Jul–Oct, not-eligible 1389.70 on June) is due within 30 days of the 10-14 notice and has an agent tool `post_trueup_decrease_6ec57e06`; complete posting leaves all scored reads unchanged, a partial posting moves P3 (July only → 713.10). No other product has an owed-at-once write that could move a scored read (Medicare/Bed-Hold corrections capped at open balance 0.00; Ancillary/Private name no applicable tool).
- **S8** (realism, task 1): the resident funds account held ≈ $10,001 on 2026-07-01 (10,000 family check available 06-26; bed-hold transfer only 07-08) while the CAO granted MA eligibility from 07-01 — above the resource limit on the first day of eligibility; the trust tasks read that eligibility start.

Cross-product rows checked (every row read by gold; details in task files): Medicare 3a65968a, b053bc47, 5acd9803, 3cf18784, 6513270e, d23f0824, 9531985d (S3), 36f675cc, f09ca1dc, 4ab5db22, c642cc84 (by premise, reversed), 8de9416f (by premise), 1b124f1c, 9e31fcfd (S5), 06cd724f, 5b54dd85, 5ec43403; Bed-Hold e2a3bb8b (S6), f11a3537, 9b0a02c2, 80b51476, 709b75b1, b39cc7a7, 270a15c3, d5af2fdf, f0840981 (by premise), 49354ce0 (by premise; S1), a5933d19, a39345fe, 5227974d, 7ce51efd, d1110207; Ancillary 1e5f526d, 82ef6a02, c4fbcc95, 703a846d, edae3fb5, 55df5022, f6197e8a, 7cba4544, 4d106878, 1e5a41d1 (by premise, repaired by §2 credit), 36c7a8ef, dfc17ed4, 6b0d549b, 359082c2, 8680b9fe, f24ada98, e94156fb, d547f1e1, 614dc436, 99a49eb7, 0eee9576, 1c9057b2, ea78a37a, 1ab23b36; Medicaid 0fe56a94 and its June–October charges, payments, past-due notice, accruals/settlements (June accrual over-count not read); Private 8648f1bd, c2db95d9 (fall-back reads only). Accepted residue applied: rows no gold step reads (June accrual, private June re-bill, a possible June cable partial) are not counted as findings.

Realism under 42 CFR 483.10(f)(10): thresholds $50/$100 interest-bearing ((f)(10)(ii)), quarterly statements ((f)(10)(iii)), $200-below-SSI notice at $1,800 ((f)(10)(iv)), 30-day conveyance with final accounting ((f)(10)(v)), no deposit as admission condition, no management fee, payer-covered items never charged and optional items only on request ((f)(11)) — all consistent. The spare-amount holdbacks (PNA, coming patient pay, ancillary/recurring/bed-hold bills) and the authorization reserves define the answer to an open-ended "what can it spare / cover" request and do not restrict the resident's access to her funds; acceptable. Surety-bond assurance ((f)(10)(vi)) is not in the charter (no defect). Only S8 is a realism flag.

KB VERDICT revision_1: task0=RED:E2 task1=RED:K1,E1 kb=K1,E1,E2,X1 src=S1,S2,S3,S4,S5,S6,S7,S8

## revision_2

Readiness: `RENDER round 3: DOCS OK` (RENDER.log tail). kb_snapshot 2026-10-23T11:13:30: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; DOCS OK; TRACEABILITY OK (0 misses). Source trust.extended.yaml cddc8af0…d31e; docs/trust tree 911bd01fb870b7bc; other products' corpora unchanged; runtime views unchanged.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Gold (re-derived from docs + records) |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | 67.11, 56.11 (unchanged) |
| 1 | PASS | PASS | PASS | 486.50, 3709.22 (was 3280.75), 1837.92, 5084.99 (was 4595.64) |

Round-1 items: K1 closed (factor tier carried whole); E1 closed (example re-drawn, no task value); E2 closed (document removed, rate now baseline); X1 closed (producible example); S1 closed (agreement-priced charges have no excess; task 1's charge priced identically by both corpora, 4992.00); S2 closed (covered end in baseline, baselines agree at 217.00); S3 closed (9531985d at 217.00/4340.00); S5 closed (ACH posting declared, paid-part factor); S6 closed as explained by the private corpus's converted-agreement rule (seeds unchanged); S7 closed (credits read from the approval, posting-invariant); S8 closed (10,000.00 posted after eligibility start). S4 placement note: partly gone (P2), P3 baseline still embeds the month-standing ladder (not routed).
Regressions: none found — every hub sentence, factor ladder, tool contract, cross-product row read by gold and owed-at-once path re-checked (details in the task files).
New source-side item: **N2** — P2's baseline defines the run as the episode's days "not yet booked" yet starts it on the coverage start date (booked days 09-09..09-30 in task 0); a literal reader can reach the run_start_day tier from the computation memo alone, so that factor's weight depends on reading past "not yet booked"; gold and fall-back unaffected. Accepted residue noted: private June re-bill 1d50d0ae (6315.00) vs the 5760.00 accrual moved to private — no gold step reads it.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=N2

## revision_3

Readiness: `RENDER round 4: DOCS OK`. kb_snapshot 2026-10-23T11:25:41: all gates OK; DOCS OK; TRACEABILITY OK (0 misses). Source c58f2f8f…3115; docs/trust 016b357d57180877; seeds, GT, runtime views and other corpora unchanged.

- N2 closed in source and KB: the run is now every day of the episode from the coverage start date under the standard method; "not yet booked" survives only as the run_start_day factor's reason; the P2 fall-back is a single definite 0.00 (GT baseline 0.0) ≠ 56.11, and run_start_day keeps its weight.
- P4 source re-wording ("schedule applying to that night"; baseline parenthetical for charges billed before 2025-07-01) already carried by the KB — no change needed.
- No regression (three P2 documents changed, all checked; everything else byte-identical). Accepted residue unchanged (private June re-bill not read by gold).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=none
