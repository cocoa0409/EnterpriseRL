# Policy-task audit — private_homeflood_rating_billing / charter-global

## charter_global_frozen
- Auditor: erl-task-policy-audit subagent (independent of the instantiating agent), round 1.
- Freeze time: 2026-10-15T22:25Z (written before any task's GT was opened).
- Frozen inputs (sha256 prefixes, re-computed and equal to the coordinator snapshot):
  `homeflood.extended.yaml` 69d970f2d921ff11, `task_tools.py` 964637328d0c292e,
  masked views `0.json` ceadfcfa78d50a47, `1.json` 6ac29b686db94d31.
- Read: `blueprint/{blueprint.yaml,db_schema.json,share_tools.py,products/homeflood.yaml}`, `products/{dwelling,excess}.yaml`
  (only to check the seeded cross-category rows), the extended charter, `task_tools.py`, the two masked views, the gate snapshot.
- Masked / not read before this file was written: `tasks/private_homeflood_rating_billing/tasks/*.json` (all GT fields),
  the difficulty `worklog.md`, any prior audit. No recursive search touched `tasks/*/tasks/`.
- Entry conditions (Step 0): gate snapshot supplied verbatim (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY /
  COMPUTE / GROUNDING / SCOPE all OK; traceability misses are only the unlock tool-name provenance of
  `pay_installment_4d782e9d`; validate INVALID only for `documents: 0`, pre-render). Masked views with hashes supplied. Complete.
- Base copy: lines 1–1341 of the extended file are byte-identical to `blueprint/products/homeflood.yaml` (diff shows only the
  trailing blank line before `extended_policies:`).

### policy_conflict_scan
Six extended policies:

| id | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| P1 `homeflood_ext_certificate_rerate` | `apply_certificate_review_8d563756` (agent) | revised_term_premium | [] |
| P2 `homeflood_ext_rerate_credit` | `book_rerate_credit_70dc8da2` (agent) | credit_amount | P1 (value_input) |
| P3 `homeflood_ext_renewal_booking` | `book_renewal_term_27983a73` (agent) | renewal_term_premium | P1 (value_input), P2 (state_gate) |
| P4 `homeflood_ext_installment_payment` | `pay_installment_4d782e9d` (user) | amount | P3 (value_input), P2 (value_input) |
| P5 `homeflood_ext_sale_cancellation` | `process_cancellation_request_bf9010ee` (agent) | credit_amount | [] |
| P6 `homeflood_ext_closing_payment` | `pay_closing_balance_b53536cf` (user) | amount | P5 (value_input) |

- Overlapping subjects: P2 and P5 both post a credit of the TERM_PREMIUM item, but with distinct charge bases (RERATE vs
  CANCELLATION), distinct triggers (applied certificate vs signed cancellation request) and distinct tools — no overlap.
  P4 and P6 both record a `homeflood_premium_payment`, but P4 is on a live policy's next installment and P6 on a cancelled
  policy's closing balance — disjoint triggers and tools. P1 and P3 both read the certificate entry's re-rated premium; P3 only
  reads what P1 writes — consistent. P2 and P5: P5's term net deducts "RERATE credits already given on the term", which is
  what P2 posts — consistent.
- P5 and P6 both supersede the same base sentence ("The policy fee and installment fees are fully earned when
  policy_fee_refundable is false."); P5 keeps installment fees earned "save that the closing payment rule may waive the fee
  of an overdue installment on a sold home", P6 waives it only in the closing payment and states "the cancellation credit
  itself keeps installment fees earned". The two replacements are compatible; merged semantics unique.
- Time anchors, eligibility and terminal states: no contradiction between extended policies. Cross-category reads (dwelling,
  excess) are read-only. Scope: the six policies split into two connected components {P1,P2,P3,P4} and {P5,P6}; with M=2
  the expected claims are task 0 = first component (root P4), task 1 = second (root P6); jointly complete and disjoint
  if `charter_scope` agrees (checked per task after reveal).

### rule_compute_equivalence
Mechanical check (whitespace-normalised): every `compute_basis` sentence of all six policies is a verbatim substring of its
own `rule`; every `overwrite.superseded_clause` is verbatim in the named base rule; every `replaced_by` is verbatim in the
extended rule; every `baseline.rule` is verbatim in the rule; every prerequisite `policy_source` is verbatim in the blocked
policy's own rule. Every factor ladder tier appears as a rule sentence and as a branch of its `decides` binding (checked
by reading each binding against its ladder). Rounding sentences match RND placement in all six (single rounding at the end;
P1/P3 floor at minimum_premium after rounding, P4/P5/P6 floor at zero after rounding).

Sentence-level mismatches found (all members of each class listed):
1. **P5 paid-claim share scope (F1, demonstrable — see findings).** Rule: "The paid-claim share of the cancellation credit is
   nothing when …, claim_light_share percent when …, and the whole credit when they total zero." and "Every share and percent
   this rule states applies to the part of the return it names". The share names the cancellation credit (whose parts the rule
   itself calls "The policy-fee return of the cancellation credit" and "The exit fee taken from the cancellation credit").
   `result` applies `claim_pct` only to the two premium parts: `(term_net - lou_part) * earning_frac * claim_pct / 100 +
   lou_part * earning_frac * lou_pct / 100 * claim_pct / 100 + fee_return - exit_fee`. The rule leaves open (non-commuting
   order) whether the share is taken before or after the policy-fee return is added and the exit fee taken off.
2. First-match reads with no decoy guard (observations; no task world exercises them): P1 `nfip_id`, `nfip_orig`, `nf_primary`,
   `nf_reason`, `nf_cxl_eff`, `nf_number` (CFIELD dwelling by `property_address`, no status/recency rule) and `xs_eff`,
   `xs_status`, `xs_closed`, `xs_limit` (CFIELD excess by address — an old cancelled Excess row at the address would race the
   live one); P3 `nf_orig` (by address) and `other_orig`/`other_addr` (`CFIELD(..., status='in_force')` takes the first
   in-force NFIP policy and only then tests its address — a customer with an in-force NFIP policy at the HomeFlood address and
   another elsewhere can be read as having none; the rule says "in force at another address"; also `renewal_grace` is not
   addressed by "in force"); P4 `xs_status`/`xs_balance` (by address); P6 `nh_eff`/`nh_addr` (`CFIELD('dwelling', ...)` with
   no filter at all, while the rule says "the customer holds a Tidemark NFIP Dwelling Form policy at a different address" —
   neither "holds" (live status) nor "different address" is applied before the pick).
3. "first" vs latest: P3 `deposit_date` takes the LATEST payment posted to the coming term while the rule says "the first payment
   of the coming term" (observation; one coming-term payment in task 0).
4. Per-term vs pooled: P4 `closed_credit = MX(0, cur_balance - all_balance)` nets every earlier term together while the rule
   speaks of "A credit balance left on an earlier term … when below zero" (observation; task 0 has one earlier term).
5. Overdue installment pick: P6 `od_num` is the latest INSTALLMENT_FEE booked, and the installment is treated as not overdue if
   that one was paid, while the rule says "the latest installment of the term whose installment fee was booked and for which no
   payment with that installment number was received" (observation; in task 1 the latest one is the unpaid one).
6. Acceptance vs credit: P1 states a certificate "is accepted for rating only when … its survey date falls fewer than
   ec_max_age_years times 12 whole calendar months before" receipt, but `vent_credit` is granted from an over-age certificate
   too (no `cert_months` test) (observation; the task-0 certificate is 0 months old).
7. Undefined date anchors (F2, demonstrable for one member): "the re-rating date" (P1, loss-history windows and tenure),
   "the booking date" (P3, notice window, loyalty, household), "the processing date" (P5, claim windows), "the payment date"
   (P4/P6). Compute pins each to NOW. Only "the re-rating date" has a competing anchor that changes a scored value in this
   difficulty's worlds (task 0); see findings.

### action_binding_and_uuids
- Each `(target_tool, computes)` pair is claimed by exactly one policy; no two policies share a target tool.
- Tool bodies: none checks status, prerequisite, eligibility or amount; each only finds the row, writes the given values and
  returns a receipt (`not_found` only for a missing id). Docstrings name no other tool, carry no ordering word about other
  actions and carry no example values (no gold leak). `book_rerate_credit_70dc8da2` and `process_cancellation_request_bf9010ee`
  post to "the term the policy currently shows", which is what makes P3's state gate on the RERATE credit order-bearing.
- uuid8s: 8d563756, 70dc8da2, 27983a73, 4d782e9d, bf9010ee, b53536cf — pairwise unrelated, no shared prefix/suffix, no
  sequence; none appears in `share_tools.py`.

### prerequisite_graph
- `prerequisite` filled on all six (P1, P5 `[]`). Edges: P2→P1, P3→P1, P3→P2, P4→P3, P4→P2, P6→P5. Every `problem` is an
  extended policy of this file, none self, none base. Acyclic (topological order P1, P2, P3, P4; P5, P6).
- All six edges `form: state`, no `fallback_reason` (correct). `gate` names exist: `new_premium` (P2), `cert_prem` (P3),
  `homeflood_billing.charge_basis` (P3 state_gate), `term_item` and `closed_credit` (P4), `acct_balance` (P6).
- `resolved_by` is in each case the depended-on policy's `target_tool`, and its body makes the state hold (P1 tool writes the
  entry's `revised_term_premium`; P2 tool posts a RERATE credit referenced to the entry; P3 tool posts the TERM_PREMIUM item to
  the new term; P5 tool posts the CANCELLATION credit referenced to the request).
- `condition` texts match their sentences in strength (closed sets named by kind: "every … entry received after the renewal
  offer", "every Elevation Certificate applied to it/an earlier term"). No authoring-viewpoint phrasing.

### prerequisite_sentences
| edge | sentence (verbatim, own rule) | connective | waited-on state | single writer |
| --- | --- | --- | --- | --- |
| P2←P1 | "The re-rate credit is worked out only once the certificate entry carries its re-rated term premium in place of 0.00." | only once | entry's re-rated premium ≠ 0.00 | P1 rule: "the figure produced is the re-rated term premium recorded on the certificate entry" |
| P3←P1 | "The renewal term premium is not fixed until every Elevation Certificate entry received after the renewal offer carries its re-rated term premium in place of 0.00." | not … until | same field, entries after the offer | P1 only |
| P3←P2 | "The coming term is booked only after the expiring term carries a RERATE credit for every Elevation Certificate applied to it." | only after | RERATE credit on the expiring term | P2 rule ("credited to that term as one RERATE credit of the TERM_PREMIUM item") only |
| P4←P3 | "An installment after the first is not fixed until the term it belongs to carries its booked term premium item." | not … until | TERM_PREMIUM item on the installment's term | P3 rule ("with a TERM_PREMIUM item for the renewal term premium") only |
| P4←P2 | "The installment due is fixed only after the account carries a RERATE credit for every Elevation Certificate applied to an earlier term." | only after | RERATE credit on an earlier term | P2 only |
| P6←P5 | "The closing payment is fixed only after the account carries the CANCELLATION credit for the signed cancellation request on file." | only after | CANCELLATION credit referenced to the request | P5 rule ("books the return of premium as one CANCELLATION credit … referenced to the request") only |

Four-point test passes for all six: ordering connective present; waited-on thing is a record-visible state in table words;
no tool name, policy id, snake_case token or row id (RERATE / CANCELLATION are ledger values, not identifiers); strength equals
`condition`. The depended-on rules do not restate the sentences. Derivation sentence + records + depended-on rule → resolving
action has one reading in each case (written per task).
Observations (not grounds for rework): P2's opening sentence ("When a certificate review has re-rated the policy's current term
lower than the full-term premium in force, …") and P6's opening sentence ("When a cancelled HomeFlood policy still shows an
amount owed, …") are trigger/scope sentences that also describe a state the depended-on write brings about — a second wording
of the same declared edge, leading to the same write, no second order. P5's replaced_by/rule mentions "the closing payment rule"
in business words (no order, no id).
No base rule sentence states a cross-problem order that a task tree rests on.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (findings only):
- P1 ← `homeflood_premium_rating`: factor sentence and elevation sentence superseded and declared; credit-reduction, LOU,
  rounding, minimum sentences followed (restated in the replaced_by). Occupancy and NFIP-transfer multipliers are new factors,
  admitted by the declared "multiplied by every factor this rule states". ← `homeflood_ec_rating`: acceptance sentence declared
  (10 calendar years "no more than" → "fewer than 120 whole months"); difference/rounding-down, "re-rates the current term",
  "applied from the date it is received", status gate followed. ← `homeflood_credits`: mitigation and claims-free sentences
  declared; "added together, never multiplied … capped at max_combined_credit_pct" followed. ← `homeflood_agg_property_combination`:
  package-credit sentence declared. No undeclared override found.
- P2 ← `homeflood_ec_rating`: RERATE amount sentence declared. ← endorsements / cancellation_refund / insurer_notices: not touched.
- P3 ← `homeflood_premium_rating`: only the final sentence ("The term premium is that reduced amount plus loss_of_use_premium …")
  is quoted as superseded, while the replaced_by replaces "the base way of fixing the term premium" for a renewal booked under
  the rule (the whole schedule chain). ← `homeflood_renewal`: "booked when the first payment … is received on or before term_end"
  followed; ← `homeflood_credits`: "decided … at each renewal" — the start figure may be the expiring term's certificate
  re-rating, whose credits were decided as of the expiring term; no second number is produced because the declared tail
  ("this replaces the base way of fixing the term premium") covers it. Observation (declaration narrower than the replaced chain).
- P4 ← `homeflood_payment_plans`: fee sentence declared; the "equal shares 3, 6 and 9 calendar months after term_start" sentence
  is not quoted, but the declared tail "this replaces the base way of working out an installment" covers it. Base rating's
  "installment fees are booked as each installment falls due" (installment_fee) is not superseded while P4 sets this
  installment's fee to fee_autopay/fee_partial — no effect on the scored payment; observation.
- P5 ← `homeflood_cancellation_refund`: refund-method, fee-earned and paid-claim-bar sentences declared; signed request, status,
  reason→effective-date, lender release, offset-then-refund sentences followed.
- P6 ← `homeflood_cancellation_refund`: fee-earned sentence declared for the closing payment; ← `homeflood_payment_plans`:
  "A payment received on or after the cancellation date … is applied to any earned premium still owed" followed.
No anonymous intermediate factor, 0/1 multiplier or dropped branch found.

### factor_ladders
| policy | factors (effect) | decides | tiers | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| P1 | elev_survey_age (method), vent_openings (param), loss_history (param), excess_layer (param), occupancy_use (param), nfip_transfer (param) | elev_factor, vent_credit, loss_credit, layer_credit, occupancy_factor, transfer_factor | 4,3,3,3,3,3 | elev (zone + certificate), vent (openings + elevation), loss (HF claims + NFIP claims + tenure), layer (HF term start + Excess row), transfer (HF replaced number + NFIP row) | loss/occupancy/transfer → dwelling; layer → excess |
| P2 | credit_start_anchor (method), fall_measure_source (method), review_delay (param), first_elevation_survey (param) | credit_start, prior_premium, delay_pct, first_pct | 3 each | credit_start tier 2, fall_measure tiers 1–2 | none |
| P3 | start_figure_source (method), early_renewal, payment_history, tenure_loyalty, household_policy, autopay_history (param) | start_premium, early_pct, notice_pct, loyalty_pct, household_pct, autopay_pct | 3 each | start figure (offer + cert/endorsement), autopay (count + method), household (status + address + date) | loyalty, household → dwelling |
| P4 | deposit_spread (method), earlier_term_credit (method), autopay_fee, pay_ahead, booking_delay, excess_paid_up (param) | deposit_part, credit_part, fee, pay_ahead_pct, booking_pct, excess_pct | 3 each | earlier_term_credit (plan + count), autopay_fee, excess_paid_up (status + balance) | excess_paid_up → excess |
| P5 | earning_basis (method), lou_return, claim_share, policy_fee_return, exit_fee (param) | earning_frac, lou_pct, claim_pct, fee_return, exit_fee | 3 each | earning_basis (date + reason + document) | none |
| P6 | late_charge (method), overdue_fee_waiver, prompt_settlement, new_home_courtesy, payment_record (param) | late_charge, fee_waiver, prompt_pct, newhome, record_courtesy | 3 each | overdue_fee_waiver (reason + document + installment timing), payment_record (notices + tenure) | new_home_courtesy → dwelling |

- Counts per policy: 4–6 factors, ≥2 parameter, ≥1 method in every policy. Bindings pairwise disjoint; no `decides` is
  `result`; every fall-through equals the factor's `baseline`; no two tiers of a ladder share a value or method.
- Factor independence: no factor's tiers read another factor's binding or output; shared inputs are plain bindings
  (`hf_cert_count` feeds both P2 credit_start_anchor and first_elevation_survey — their tiers are correlated, never chained;
  `od_due`/`od_paid` feed both P6 late_charge and overdue_fee_waiver the same way). No result assembled inside a factor binding.
- Labels: method factors either switch the algorithm (P4 spread/apply/none, P5 flat/pro-rata/short-rate, P6 percent/flat/none,
  P1 table/table-less-one-foot/constant) or select which record supplies the measuring date or base premium (P2 both, P3
  start figure). The latter are source-selection methods; acceptable, noted as observation.
- Realism (each condition and outcome judged against US flood/P&C practice or a carrier's filed schedule): flat/pro-rata/
  short-rate cancellation, exit fee, policy-fee return window, claims-based return reduction, LOU return after a LOU payment,
  early-renewal, payment-history surcharge, tenure, multi-policy, EFT credits and installment-fee waivers, late charge, fee
  waiver on sale, collection courtesies, loss-free credits, excess-layer package credit, NFIP-transfer credit, vent credit split
  by elevation, delayed-review addition (interest-like) — all within what carriers file. Doubtful but not demonstrably
  unpublishable (observations): P2 first_elevation_survey (a 5–10 % bonus on a re-rate credit for a policy's first certificate);
  P1 occupancy_use reading occupancy only from the customer's NFIP record, even a cancelled one, with factor 1 for every
  HomeFlood customer without NFIP history; P1 "less one foot" for a 5-to-10-year-old survey; P4 booking_delay (installment
  credit because Tidemark booked the term late) and pay_ahead.

### findings
- **F1 — SOURCE-POLICY RED (P5 `homeflood_ext_sale_cancellation`, rule ↔ compute; bears on task 1).** Symptom: the rule makes the
  paid-claim share a share "of the cancellation credit" whose full-value tier is "the whole credit", and says each share applies
  "to the part of the return it names"; the parts it names include "The policy-fee return of the cancellation credit" and "The
  exit fee taken from the cancellation credit". Compute applies `claim_pct` to the premium parts only and adds `fee_return - exit_fee`
  after it. Root cause: the order of the claim share against the fee return and the exit fee is not fixed in the rule, and the
  compute picks one order the rule does not state. Consequence: demonstrated in task 1's file (two credits, 289.23 vs 280.48).
  Affected: P5 rule sentence on the paid-claim share and the assembly sentence; `compute.result`.
- **F2 — undefined "re-rating date" (P1; SOURCE-TASK RED on task 0).** Symptom: P1's loss-history credit counts windows and tenure
  "to the re-rating date"; the charter never defines it, while P1 applies the re-rated premium "from the date it was received" and
  the base credit rule anchors the claims-free lookback on "the term_start being rated". Compute uses NOW. Consequence and the
  second reading's numbers are in task 0's file. Other members of the class (no demonstrated consequence here): "the booking date"
  (P3), "the processing date" (P5), "the payment date" (P4, P6).
- Observations O1–O7 (no demonstrated consequence in this difficulty's worlds): O1 first-match class (§rule_compute_equivalence
  item 2, all members listed); O2 P3 "first payment" vs LATEST; O3 P4 pooled earlier-term credit; O4 P6 overdue-installment pick;
  O5 P1 vent credit from an over-age certificate; O6 overwrite declarations narrower than the replaced computation (P3 rating
  chain, P4 equal-shares sentence and base installment-fee booking); O7 realism doubts listed under factor_ladders.

## post_reveal_charter_additions
Written after both task derivations were frozen (mtimes `0.md` 22:27:27Z, `1.md` 22:28:01Z; reveal 22:28:05Z). Both items
below are derived from the charter text and the opening DBs, not from GT values; they were missed in the pre-reveal
§prerequisite_graph, which stated that every `condition` matches its sentence — that statement is corrected here, the
pre-reveal text above is left unchanged. The "Freeze time: 2026-10-15T22:25Z" label above is an estimate; the file mtime
22:26:27Z is authoritative.
- **F3 — SOURCE-POLICY RED (check 7, P4 `homeflood_ext_installment_payment` edge to P3).** Sentence: "An installment after the
  first is not fixed until the term it belongs to carries its booked term premium item." Declared `condition`: "The policy's
  current term (its term_start) carries a homeflood_premium_charged TERM_PREMIUM entry." Declared `effect`: "term_item changes from
  0.00 to the booked renewal term premium". The condition names a different object (the term the policy currently shows) from the
  sentence (the term the installment belongs to); for a renewal-chain world the policy's current term always carries its own
  TERM_PREMIUM item, so the condition is true before and after the depended-on write, and `term_item` (SUM TERM_PREMIUM on the
  policy's term_start) is never 0.00 there. Demonstrated on task 0 (`0.md` T0-C2: condition true at the opening via
  `homeflood_billing.da1124c8…`; term_item 2244.01 → 1256.86).
- **F4 — SOURCE-CHAIN class (sentences P3←P2 and P4←P2).** "The coming term is booked only after the expiring term carries a RERATE
  credit for every Elevation Certificate applied to it." / "The installment due is fixed only after the account carries a RERATE
  credit for every Elevation Certificate applied to an earlier term." Both quantify over certificates already applied; when the
  application is itself a write of the same tree (P1), both are vacuously satisfied on the opening DB. Demonstrated on task 0
  (`0.md` T0-C1).
- Cross-task seed class (per-task REDs, listed together so one rework closes them): seeded HomeFlood `homeflood_claim_paid` rows
  whose amounts the base settlement rule cannot produce while `seed_consistency` says they are consistent — task 0
  `homeflood_claims.576e3389…` (2150.00; ACV basis and the 2,000 deductible of that era give 4420.00), task 1
  `homeflood_claims.bad5f32b…` (3850.00; ACV basis gives 3400.00). No other claim_paid rows are seeded in this difficulty.

## per_task_verdicts
| task | policy self-consistency | problem tree | factors | unique solution | GT match (frozen reading A) |
| --- | --- | --- | --- | --- | --- |
| 0 | RED (F3) | RED (T0-C1, T0-C2) | PASS | RED (T0-T1 = F2; T0-T2 proof text/seed) | all 4 writes identical |
| 1 | RED (F1) | PASS | PASS | RED (T1-T1 seed/proof text; F1 second value) | both writes identical |

## closing_checklist
Not closed: the difficulty does not pass the source-layer audit (REDs F1–F4 and the per-task items above). Items that do hold:
two task files plus this file, one per task; scopes disjoint and jointly complete (`charter_scope` task 0 = P1–P4 with their four
tools, task 1 = P5–P6 with their two tools); every tree has 1–3 prerequisite problems, ≥ max(n−1,1) value_input edges, an
owner=user root write, no cycle, and the difficulty graph is a DAG; every computation declares 4–6 factors with ≥2 parameter and
≥1 method, every task has multi-source and cross-difficulty factors on seeded rows, every factor bears weight against an honest
baseline and every whole baseline differs from gold; uuid8s independent. Instantiation-stage gates were not re-run by this audit
(not part of a failing close-out).

task0=SOURCE-POLICY+SOURCE-CHAIN+SOURCE-TASK RED task1=SOURCE-POLICY+SOURCE-TASK RED
charter=F1,F2,F3,F4

## revision_2
### charter_global_frozen (round 2)
- Re-audit after REWORK round 2 (worklog tail "REWORK round 2: gates 8/8 green" checked first). Gate snapshot round 2 run by this
  auditor via `/tmp/erl0065_coord/snapshot.sh private_homeflood_rating_billing 2`: EXTENDED / TASK TOOL CONTRACT / REPLAY /
  SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; traceability misses only the unlock tool-name provenance; validate INVALID only
  for `documents: 0` (pre-render).
- Hashes: `homeflood.extended.yaml` 2cc39491d17d295f (changed from 69d970f2d921ff11 → every charter-global section re-derived);
  `task_tools.py` 964637328d0c292e (unchanged → §action_binding_and_uuids carried forward by reference); masked views
  `0.json` 18b4c9d13106de9c, `1.json` e1fbdedaff8f3c44 (changed: seeded claim rows; personas byte-for-byte as round 1).
- Base copy still identical to `blueprint/products/homeflood.yaml`. This section was written before either round-2 task file was opened.

### charter re-derivation (round 2)
- Mechanical: every compute_basis sentence verbatim in its rule (sentence-level sweep, all six policies); compute_basis keys = compute
  bindings; every superseded_clause verbatim in its base rule, every replaced_by and policy_source verbatim in the extended rule;
  every baseline.rule in the rule.
- **F1 closed (genuinely, not reworded).** P5 now states "The paid-claim share of the premium return — the term-premium part and the
  loss-of-use part of the return, before any policy-fee return or exit fee — …" and "The cancellation credit is put together in this
  order: every share and percent this rule states is first applied to the part of the premium return it names, every amount this rule
  states is then added to or taken from that result …". Compute (unchanged) is now the only reading; reading B (share on the fee
  return) is excluded by the text. Class A2/A3 sweep: P1 (factors multiply, credits summed and capped, once), P2 (additions of the
  unrounded pro rata), P3 (one net percent), P4 (percents of the share, amounts added), P6 (percents of their named base, amounts
  added) — all order-explicit or purely additive. Closed class-wide.
- **F2 closed.** Definitions now in the rules: P1 "The re-rating date is the day the certificate review is completed and recorded; it
  is neither the date Tidemark received the certificate nor the term start …"; P3 booking date; P4 and P6 payment date; P5 processing
  date — each = the day of the write, which is what the compute's NOW reads. Class B11 closed. (P6's "after the policy was closed"
  still leans on closed_date; the tool writes the processing date and both candidate dates give the same tier in task 1 — observation.)
- **F3 closed.** P4 defines "the term that installment belongs to is the term of the latest first payment (installment 1) received on
  the policy"; new plain binding `inst_term` feeds term_item, paid_count, deposit, cur_balance, since_prev, booked_on, booking_lag;
  declared condition "The term_start of the latest homeflood_premium_payment with installment_number 1 on the policy carries a …
  TERM_PREMIUM entry with that term_start" now names the sentence's object; effect "term_item … changes from 0.00" is now true.
  Booking-delay guard ("nothing when … no term premium item is booked for that term") is stated in the rule and implemented
  (`DAYS(inst_term, booked_on) if booked_on else 0`).
- **F4 closed.** P3: "The coming term is booked only after every Elevation Certificate entry received during the expiring term carries a
  RERATE credit, save one kept on file for the next term with its re-rated term premium recorded." P4: "… every Elevation Certificate
  entry received during an earlier term carries a RERATE credit, save one kept on file …". Conditions restate the same scope
  (recorded_date within the term; excluding ec_applied false with revised_term_premium above 0.00). An unreviewed entry (0.00) now
  falls inside the quantifier, so the state is not vacuous before the in-task review. Single writer of a RERATE credit: P2. (Where a
  review re-rates higher, P1's own write moves the entry into the "kept on file" exception — the hop is still determined by the records
  after P1; observation.) Class C13 sweep: all six conditions re-checked against their sentences — equal scope.
- Observations carried: O1 first-match reads — P6 `nh_eff`/`nh_addr` now filtered `status='in_force'`; remaining members unchanged and
  still unguarded against a second record: P1 `nfip_id`, `nfip_orig`, `nf_primary`, `nf_reason`, `nf_cxl_eff`, `nf_number`, `xs_eff`,
  `xs_status`, `xs_closed`, `xs_limit`; P3 `nf_orig`, `other_orig`/`other_addr`; P4 `xs_status`/`xs_balance`; P6 `nh_eff`/`nh_addr`
  (first in-force record, then address test). No task world has a second record; observation. O2 closed (P3 `deposit_date` filters
  installment_number=1, rule says "(its installment 1)"). O3 closed (rule now "earlier terms taken together"). O4 closed (rule wording
  = compute). O5 closed (`vent_flag` is False unless the survey is fewer than ec_max_age_years×12 months before receipt; rule and
  ladder say "accepted for rating"). O6, O7 unchanged (observations).
- New-defect scan: no factor reads another factor's binding (P1 `vent_flag` recomputes the age test from plain `cert_survey`/
  `cert_received`, it does not read `cert_months`); `inst_term` is a plain binding; no new cross-problem order; ladders unchanged in
  tier count and values; tool module unchanged. Nothing regressed.

### per_task_verdicts (round 2)
| task | policy self-consistency | problem tree | factors | unique solution | GT match |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | 4/4 writes identical |
| 1 | PASS | PASS | PASS | PASS | 2/2 writes identical |

### closing_checklist (round 2)
- Files: `_difficulty.md`, `0.md`, `1.md`, one per task; round-1 text untouched, revision_2 appended; both comparison sections PASS.
- Coverage/scope: task 0 = P1–P4 with their four tools, task 1 = P5–P6 with their two tools; disjoint, jointly complete; each tool
  uuid8 independent and frozen (tool module unchanged since round 1).
- Trees: task 0 n = 3 (4 value_input edges), task 1 n = 1 (1 value_input edge); each root is an owner=user write; no cycle; the
  difficulty's prerequisite graph is a DAG; every declared condition equals its sentence's scope and is false on its opening DB.
- Factors: P1 6, P2 4, P3 6, P4 6, P5 5, P6 5 (each ≥2 parameter, ≥1 method); multi-source and cross-difficulty factors in both
  tasks on seeded rows; every factor bears weight against an honest baseline; every whole baseline ≠ gold.
- Gates on the final form: round-2 snapshot run by this auditor — all instantiation gates OK; only pre-render traceability/document
  items remain.
- Remaining observations (not grounds for rework): O1 first-match reads without a second-record guard (members listed in revision_2
  charter re-derivation), O6 overwrite declarations narrower than the replaced chain (P3, P4), O7 realism doubts (first-certificate
  addition, occupancy from the NFIP record, one-foot haircut, booking-delay and pay-ahead credits), P6 "closed" anchor.

VERDICT revision_2: task0=PASS task1=PASS
charter=CLEAN

## revision_3
### charter_global_frozen (round 3)
- GATE FIRST: worklog tail "REWORK round 3: gates 8/8 green". Snapshot `/tmp/erl0065_coord/snapshot.sh private_homeflood_rating_billing 3`
  run by this auditor (2026-10-16T14:29:58Z): all instantiation gates OK; traceability only the unlock tool-name provenance; validate
  INVALID only on the render side (documents 36).
- Hashes: charter 7415673b3508cba0 (changed → charter-global checks re-derived); `task_tools.py` 964637328d0c292e (unchanged →
  §action_binding_and_uuids carried forward); masked views 18b4c9d13106de9c / e1fbdedaff8f3c44 (identical to round 2). Base copy
  still identical to the blueprint. Scope of this round: my round-1/2 verdicts plus the renderer source scan
  `audits/render_source/private_homeflood_rating_billing/render_r1.md` (M1–M6, wording, ties, placement), and XF_recipe classes.
- Mechanical (scratch script): every compute_basis sentence verbatim in its rule; basis keys = compute bindings; superseded clauses
  verbatim in base; replaced_by / policy_source / baseline.rule verbatim in the extended rule; no factor binding reads a binding
  owned by another factor (transitive token scan over all six policies).

### renderer items
- **M1 closed.** `claim_pct = 0 if (claim_net > 0 and claim_net >= 25 % × (building_coverage + contents_coverage)) …`; rule and ladder
  say "total more than zero and at least claim_heavy_pct percent of the policy's dwelling limit and personal property limit taken
  together". A Renters policy (dwelling 0) with no claim → 100. Rule = compute = ladder.
- **M2 closed for the cancellation's own scope** (each replaced_by now restates the base content for out-of-scope cancellations:
  base pro-rata refund, base paid-claim bar, base "fully earned" sentence) and the closing payment's tail now covers the policy-fee
  half ("save it and the policy-fee return of a cancellation credit worked out under the cancellation rule, the policy fee and
  installment fees are fully earned …"). **Remaining member — R3-1 (RED), see findings:** the sibling exceptions no longer match.
- **M3 closed for the two named reads:** P3 household credit is now existence-tiered (`EXISTS('dwelling', status='in_force',
  primary_residence=False)`, `EXISTS('excess', status='active', property_address=…)`), rule identical; P6 new-home courtesy reads the
  in-force primary-residence NFIP policy (unique by the primary-residence designation) and then tests the address. **Remaining members
  of the same class (first-match pick where the rule's object can be more than one record) — R3-3 (RED), see findings.**
- **M4 closed.** Waiver tiers now state the negative-gap case ("in full when that installment fell due after the request's effective
  date, whatever the reason") and the on-or-before condition for the sale/replacement tiers; compute `waiver_gap < 0` first, REPLACED
  tier `waiver_gap >= 0`; "no installment overdue" → nothing (9999 sentinel). Due date defined: "An installment's due date is the
  posted date of its installment fee, which is booked on the day the installment falls due under the plan" (ties the late charge's
  `od_due` to the plan schedule).
- **M5 closed** for the review-delay figure: "The review counts as completed on the day this re-rate credit is booked." = `DAYS(cert_received,
  NOW)`. Observation O-R3-a: P1 defines its re-rating date as "the day the certificate review is completed and recorded", while P2
  deems the review completed on the credit's booking day; the two days coincide in every task (both writes in one session) and each
  rule fixes its own figure, so no second value arises — wording collision only.
- **M6 closed.** The pay-ahead count is stated as computed ("the whole calendar months from the term's start to the payment date less the
  months after the start at which that previous installment fell due (0 for the first payment, 3 or 6 on QUARTERLY)"), absent first
  payment → nothing (`since_prev` 99).
- Wording (deposit difference) closed: "less the sum of policy_fee and the plan's down share". Ties closed: every rule now states "among
  records of the same date the one recorded first counts" (= LATEST's first-row behaviour); "another, earlier" → "another" in rule,
  ladder and traces. Rounding: every rule states nearest cent, exact halves to the even cent (= Python `round` used by RND); no scored
  value sits on a tie. Placement: single-factor definitions now sit in their factors (P1 `nfip_id` and the re-rating date in
  loss_history; P2 `cert_survey` in credit_start_anchor; P4 `prev_due_months` in pay_ahead; P5 `req_reason`/`req_doc` in
  earning_basis; P3 NFIP-record definition in the loyalty sentence / `nf_orig` in tenure_loyalty); shared definitions (P6 `od_*`,
  `req_*`; P3 booking date; P1 NFIP record, `nfip_orig`) stay plain, as XF A4 requires.

### own round-1/2 verdicts — regression
- F1–F4 remain closed (P5 share scoped and ordered; date anchors defined; P4 installment term and its condition; RERATE gates scoped to
  certificates received during the term). Six declared conditions re-checked against their sentences: equal scope, all false on the
  opening DBs. Observation O-R3-b (realism): the P3 household long tier now requires an active Excess at the HomeFlood address, and the
  certificate re-rate the renewal starts from already carries the 3 % layer credit for that same Excess policy — the companion policy is
  rewarded twice in one renewal premium; not demonstrably unpublished (multi-line and package credits do stack at some carriers).

### findings (round 3)
- **R3-1 — SOURCE-POLICY RED (sibling overwrites of "The policy fee and installment fees are fully earned when policy_fee_refundable is
  false."; remaining member of renderer class M2 / XF D14).** P5 replaced_by: "… installment fees stay fully earned; this policy-fee
  return applies only to a cancellation credit worked out under this rule, and save it and the overdue-installment fee the closing
  payment rule gives back on a sold or replaced home, the policy fee and installment fees are fully earned when policy_fee_refundable
  is false." P6 replaced_by: "The overdue-fee waiver of the closing payment gives back the overdue installment's installment_fee in full
  when that installment fell due after the request's effective date, whatever the reason, …". Same situation: a cancellation for
  INSURED_REQUEST (or NO_LONGER_REQUIRED) effective 2026-09-01, installment fee posted 2026-09-05 and unpaid, closing payment. P5's
  sentence: the only installment-fee exception is the closing-payment give-back on a sold or replaced home → this fee is fully earned.
  P6: the fee is given back in full. Root cause: M4 widened P6's first waiver tier to every reason, while P5's exception still names
  only sold or replaced homes. Affected: P5 replaced_by and rule (fee-earned sentence), P6 waiver tier 1; no task world exercises it
  (task 1 is PROPERTY_SOLD with the installment due before the effective date).
- **R3-3 — SOURCE-POLICY RED (first-match pick where the rule's object can be more than one record; remaining members of renderer class M3 /
  XF C12).** Previously recorded by me as observation O1; RED this round under the coordinator's rule that a remaining member of a
  renderer class is RED. Members, one list:
  1. P1 "The customer's NFIP record for the address is the customer's Tidemark NFIP Dwelling Form policy whose property address is the
     HomeFlood property address." → `nfip_id`, `nfip_orig`, `nf_primary`, `nf_reason`, `nf_cxl_eff`, `nf_number` = `CFIELD('dwelling', …,
     property_address=…)`. The dwelling charter writes contents-only policies, and the base property-combination rule bars HomeFlood
     only over a live NFIP *building* policy, so a replaced building record and a later NFIP contents policy can share the address; the
     rule names no choice and the compute takes whichever row comes first (occupancy, transfer and loss-history tiers then differ by row
     order).
  2. P1 layer credit "follows the customer's Tidemark Excess Flood policy at the same property address, which counts as in force on the
     term start when …" → `xs_eff`, `xs_status`, `xs_closed`, `xs_limit` = `CFIELD('excess', …, property_address=…)`: an expired or
     cancelled earlier Excess row at the address can be picked instead of the one in force on the term start.
  3. P3 loyalty "the customer's NFIP record for the address (the customer's Tidemark NFIP Dwelling Form policy whose property address is
     the HomeFlood property address)" → `nf_orig` = `CFIELD('dwelling', 'original_effective_date', property_address=…)`.
  4. P4 Excess paid-up "the customer's Tidemark Excess Flood policy at the same address is active … nothing when there is no active
     Excess Flood policy at the address" → `xs_status`, `xs_balance` = `CFIELD('excess', …, property_address=…)`: with an expired
     earlier row first, the compute returns 0 while the rule (an active one exists) grants the credit.
  No task world holds a second record at these addresses; the defect is charter-level.
- Per-task (cited from the task files): task 1 T1-R3-1 stale proof text after M1 (SOURCE-TASK RED); task 0 none.

### per_task_verdicts (round 3)
| task | policy self-consistency | problem tree | factors | unique solution | GT match |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS on its world (R3-1/R3-3 not exercised) | PASS | PASS | PASS | 4/4 writes identical |
| 1 | PASS on its world (R3-1 not exercised) | PASS | PASS | RED (T1-R3-1 proof text) | 2/2 writes identical |

### closing_checklist (round 3)
Not closed: charter REDs R3-1, R3-3 and task 1's T1-R3-1 remain. Everything else in the round-2 checklist still holds (coverage, disjoint
scopes, trees, factor counts and weight, gates green on the final form).

VERDICT revision_3: task0=PASS task1=SOURCE-TASK RED
charter=R3-1,R3-3

## revision_4
### charter_global_frozen (round 4)
- GATE FIRST: worklog tail "REWORK round 4: gates 8/8 green". Snapshot round 4 run by this auditor: all instantiation gates OK;
  traceability only unlock tool-name provenance; validate INVALID only render-side. Hashes: charter af170c240b40ea9f (changed →
  re-derived); tools 964637328d0c292e and both masked views unchanged. Base copy identical to the blueprint.
- Mechanical (scratch script, all six policies): compute_basis sentences verbatim in rule; basis keys = bindings; superseded/replaced_by/
  policy_source/baseline verbatim; no factor binding reads another factor's binding; every rule carries the same-day tie-break and the
  half-to-even rounding sentence; factor counts 6/4/6/6/5/5 as before.

### round-3 REDs
- **R3-1 closed.** P5's fee-earned exception now enumerates the closing payment's give-back in the closing payment's own tier words (full:
  due after the effective date whatever the reason, or PROPERTY_SOLD with statement on/before and within waiver_window_days; half:
  REPLACED_COVERAGE with declarations, same timing); P6's tail still names P5's policy-fee return. Same situation as round 3
  (INSURED_REQUEST, fee due after the effective date): both texts now give the fee back. Sibling exclusions match (XF D14).
- **R3-3 closed, whole class.** Every record read is now scoped to a unique record the rule names:
  P1 NFIP record (`nfip_id`, `nfip_orig`, `nf_primary`, `nf_reason`, `nf_cxl_eff`) and P3 `nf_orig` read `policy_number =
  replaced_nfip_policy_number`, rule: "the Tidemark NFIP Dwelling Form policy this HomeFlood policy replaced … a HomeFlood policy that
  replaced no NFIP policy has no NFIP record" (`nf_number` and the number re-test dropped, consistent); P1 `xs_eff`/`xs_limit` and P4
  `xs_status`/`xs_balance` read the Excess policy in status active at the address, rule states it and cites the Excess charter's
  one-live-policy rule; P3 household uses EXISTS; P6 new-home reads the in-force primary-residence NFIP policy. Remaining CFIELD/EXISTS
  reads in the charter: none unscoped. Class C12 sweep also covers requests (P5/P6 "the latest received, when more than one is signed;
  a withdrawn or unsigned request never counts" = LATEST SIGNED by created_at), P4 deposit ("the payments received for the term as its
  installment 1" = SUM installment 1) and P3 early-renewal ("the latest payment received for the coming term as its installment 1").
- T1-R3-1 closed (see `1.md` revision_4).

### render_r1 items — still closed
M1 (`claim_pct` requires > 0, threshold on dwelling + personal property), M2 (all replaced_by tails restate in-force base content; sibling
fee-earned texts agree), M3 (household EXISTS, new-home unique primary in-force read), M4 (negative gap, on-or-before tiers, due date =
fee posting date), M5 ("The review counts as completed on the day this re-rate credit is booked." = `DAYS(cert_received, NOW)`), M6 (pay-ahead
count stated as computed, absent first payment → nothing), deposit-difference wording, ties, rounding, placement — all unchanged and closed.

### observations (round 4, not grounds for rework)
- O-R4-a (realism): the P1 layer credit now requires the Excess policy to be active on the re-rating day (the closed-after-term-start branch
  was removed), so an Excess in force on the term start but closed before the review loses the credit for the whole re-rated term; stated
  consistently in rule, ladder and compute, and plausible as a company rule.
- O-R4-b: the NFIP record is now only the replaced NFIP policy; NFIP losses at the address under an unreplaced (lapsed) NFIP policy no longer
  enter the loss-history credit — declared by the overwrite of the claims-free sentence, consistent.
- Carried: O-R3-a (P1 "completed and recorded" vs P2 "counts as completed" wording), O-R3-b (Excess rewarded in both the start figure's
  layer credit and the household long tier), O6, O7.

### per_task_verdicts (round 4)
| task | policy self-consistency | problem tree | factors | unique solution | GT match |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | 4/4 writes identical |
| 1 | PASS | PASS | PASS | PASS | 2/2 writes identical |

### closing_checklist (round 4)
Closed: per-task files and this file one-to-one, revisions appended, both comparisons PASS; scopes disjoint and complete; uuid8s independent;
trees 1–3 prerequisites with ≥ max(n−1,1) value_input edges, owner=user roots, conditions equal to their sentences and false at the opening,
DAG; every computation 4–6 factors (≥2 parameter, ≥1 method), multi-source and cross-difficulty factors on seeded rows in both tasks, every
factor bears weight against an honest baseline, whole baselines ≠ gold; instantiation gates re-run on the final form (round-4 snapshot) — green.

VERDICT revision_4: task0=PASS task1=PASS
charter=CLEAN

## revision_5
### charter_global_frozen (round 5)
- GATE FIRST: worklog tail "REWORK round 5: gates 8/8 green". Snapshot round 5 run by this auditor (2026-10-16T17:16:39Z): all gates OK,
  TRACEABILITY OK (0 misses); validate INVALID render-side only. Charter de95085c34a950aa (changed → re-derived); tools and masked views
  unchanged. Base copy identical to the blueprint.
- Mechanical (all six policies): compute_basis sentences verbatim; basis keys = bindings; superseded/replaced_by/policy_source/baseline
  verbatim; no factor reads another factor's binding; factor counts 6/4/6/6/5/5 with ≥2 parameter and ≥1 method each; tie-break and
  half-to-even sentences present in every rule; no authoring vocabulary ("charter", "binding", "tier", "ladder") in any rule.

### KB-audit source items S1–S5
- **S1 closed.** P1 declares the overwrite of "The total credit percent from the credit rule then reduces the result.", replaced by the
  re-rate's single credit assembly whose tail restates both base steps for every other rating; baseline adds "the credit percent recorded
  on the policy for the term is not carried into the re-rating".
- **S2 closed.** "Excess Flood program" in P1 and P4; no authoring vocabulary left.
- **S3 closed.** Acceptance for the re-rate rests on survey age at receipt (recorded fields); form, seal and no-alteration are stated as the
  condition for recording an entry at all; base acceptance restated for every other use.
- **S4 closed.** P3 and P4 middle tiers say "one to three of them and every one was made by ACH" (= `pay_total == pay_ach and pay_ach > 0`);
  zero payments fall through (P4 "installment_fee otherwise"; P3 states no credit for that case, and the ladder's fall-through says so).
- **S5 closed.** P5's fee sentence states only its own case ("installment fees stay fully earned in the cancellation credit … in every other
  cancellation credit the policy fee and installment fees are fully earned"); P6 keeps its ladder and names P5's policy-fee return. The two
  replacements of the same base clause cover disjoint contexts (cancellation credits / closing payment); merged semantics unique.

### P2 re-keying (coordinator principle: no incidental counts, rule = compute on every record set)
- credit_start_anchor: tiers on receipt vs term start (≤ early_receipt_days 30 → term start; later and survey after term start → survey
  date; else receipt) — rule = compute (`DAYS(term_start, cert_received) <= 30` covers receipt before the term start). Count-keyed tiers gone.
- vent_survey_addition replaces the first-certificate addition: openings + survey < fresh_vent_months (3) before receipt → 10, openings
  older → 5, none → 0 — rule = compute = ladder; realism doubt carried with O7.
- Cap "never more than the net premium booked for the term" = `MN(term_net_booked, RND(...))`, applied after rounding as stated.
- **fall_measure_source — R5-1 (RED), see findings.**

### round-4 status
No round-4 RED existed. render_r1 M1–M6 and lower items, F1–F4, R3-1, R3-3 re-checked in the round-5 text: all remain closed.

### findings (round 5)
- **R5-1 — SOURCE-POLICY RED (P2 `fall_measure_source`, rule ↔ compute; new in round 5).** Rule: "The premium the re-rate credit is
  measured from is the revised full-term premium of the latest endorsement entry on the policy when that entry was recorded within the
  term …; when it was not, it is the premium on the renewal offer for the term when the term began as a renewal; …". Compute:
  `prior_premium = end_prem if (end_date != None and DAYS(F('term_start'), end_date) >= 0) else (…)` — only the lower bound of "within
  the term"; the round-4 upper bound (on or before receipt) was removed and term_end was not put in its place. Same situation, task-0
  type world (renewal unbooked, the policy still showing 2025-09-01 → 2026-09-01) plus a MORTGAGEE_CHANGE endorsement recorded
  2026-10-05 carrying the in-force 2033.47: rule — latest endorsement not within the term → offer 2244.01 → (2244.01 − 1373.62) × 55/365
  × 1.14 = 149.52; compute — 2033.47 → 113.35. Single member of the class (no other "within the term" condition with a compute
  counterpart in the charter). Not exercised by either task world.
- Task-level: task 0 T0-R5-1 stale `tier_taken` (SOURCE-TASK RED, `0.md`); task 1 none.
- Observations: carried O-R3-a, O-R3-b, O-R4-a, O-R4-b, O6, O7 (the new mitigation-survey addition joins the O7 realism doubt).

### per_task_verdicts (round 5)
| task | policy self-consistency | problem tree | factors | unique solution | GT match |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS on its world (R5-1 not exercised) | PASS | PASS | RED (T0-R5-1 proof text) | 4/4 writes identical |
| 1 | PASS | PASS | PASS | PASS | 2/2 writes identical |

### closing_checklist (round 5)
Not closed: R5-1 and T0-R5-1 remain; all other round-4 checklist items still hold, gates green on the final form.

VERDICT revision_5: task0=SOURCE-TASK RED task1=PASS
charter=R5-1

## revision_6
### charter_global_frozen (round 6)
- GATE FIRST: worklog tail "REWORK round 6: gates 8/8 green". Snapshot round 6 run by this auditor (2026-10-17T13:14:38Z): all gates OK,
  TRACEABILITY OK; validate INVALID render-side only. Charter 02907f91786ff496 (changed → re-checked); tools and masked views unchanged;
  base copy identical to the blueprint.
- Mechanical (all six policies): compute_basis sentences verbatim; keys = bindings; superseded/replaced_by/policy_source/baseline verbatim;
  no factor reads another factor's binding; factor counts 6/4/6/6/5/5; tie-break and half-to-even sentences in every rule; no authoring
  vocabulary; every CFIELD/EXISTS read scoped (replaced NFIP number, active Excess, in-force primary/non-primary NFIP).

### round-5 REDs
- **R5-1 closed.** Rule and ladder: "recorded within the term (on or after term_start and before term_end)"; compute `DAYS(F('term_start'),
  end_date) >= 0 and DAYS(end_date, F('term_end')) > 0`. Round-5 counter-world (MORTGAGEE_CHANGE recorded 2026-10-05 on the policy still
  showing 2025-09-01 → 2026-09-01): rule and compute now both fall to the offer → 149.52. No other "within the term" condition with a compute
  counterpart exists in the charter (class closed).
- T0-R5-1 closed (see `0.md` revision_6).
- Regression: F1–F4, R3-1, R3-3, render_r1 M1–M6 and lower items, KB S1–S5 re-checked by their compute signatures and sentences — all still
  closed. Observations carried unchanged (O-R3-a, O-R3-b, O-R4-a, O-R4-b, O6, O7).

### per_task_verdicts (round 6)
| task | policy self-consistency | problem tree | factors | unique solution | GT match |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | 4/4 writes identical |
| 1 | PASS | PASS | PASS | PASS | 2/2 writes identical |

### closing_checklist (round 6)
Closed: files one-to-one, revisions appended, both comparisons PASS; scopes disjoint and complete; uuid8s independent; trees valid (n = 3 and
1, value_input floors met, owner=user roots, conditions equal to their sentences and false at the opening, DAG); every computation 4–6 factors
with ≥2 parameter and ≥1 method, multi-source and cross-difficulty factors on seeded rows, every factor bears weight against an honest baseline,
whole baselines ≠ gold; instantiation gates green on the final form (round-6 snapshot).

VERDICT revision_6: task0=PASS task1=PASS
charter=CLEAN

## revision_7
### charter_global_frozen (round 7, seed-only)
- GATE FIRST: worklog tail "REWORK round 7: gates 8/8 green". Snapshot round 7 run by this auditor: all gates OK, TRACEABILITY OK,
  validate_scenario **VALID** (documents 353).
- Seed-only constraint: full sha256 of `homeflood.extended.yaml` (02907f91786ff496cbf4…) and `task_tools.py` (964637328d0c292e…) equal the
  coordinator's `/tmp/erl0065_coord/seedonly_freeze.sha256`; every charter-global section of revision_6 is carried forward by reference.
- KB S6/S7 (`audits/policy_kb/private_homeflood_rating_billing/kb_audit_report.md` §revision_3): closed in task 0's world (see `0.md`
  revision_7). Re-seeded rows checked against the owning charters (blueprint `excess.yaml` 500K tier: rate 1.55/1,000, AE 1.0, loss-of-use
  110, minimum 650, standard wait 30 days; `dwelling.yaml` Residential Condominium Unit: icc_available false, standard wait 30 days) and the
  published Excess rating document (`docs/excess/premium_rating_f7f0684a.json`, `rate_tables_e85f95cd.json`) — producible.
- No scored value moved in either task; no read changes tier. Observation: task 1's file bytes changed with no material difference.

### per_task_verdicts (round 7)
| task | policy self-consistency | problem tree | factors | unique solution | GT match |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | 4/4 writes identical |
| 1 | PASS | PASS | PASS | PASS | 2/2 writes identical |

### closing_checklist (round 7)
Closed — round-6 checklist carried (charter and tools frozen); seeded cross-category rows now producible; gates green and scenario VALID.

VERDICT revision_7: task0=PASS task1=PASS
charter=CLEAN
