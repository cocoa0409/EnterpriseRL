# Worklog — flood_coverage_and_mortgagee_billing (M=2)

## Step 0 — draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[4, 6, 5]
- task 1: prerequisite_problems=2, factor_counts=[4, 6, 5]

## Claimed space
- task 0 (renewal paid by the insured after a missed renewal notice): offer (6 factors) -> renewal record (5) -> insured's renewal payment (4, owner=user, root).
  Tools: record_flood_renewal_offer_81f1ff73, renew_flood_policy_8cc307a9, pay_flood_renewal_premium_ad8d78a5.
- task 1 (house sold, refund of unused premium): additional premium for an unbilled limit increase (6) -> signed cancellation with credit (5, owner=user) -> refund (4, root).
  Tools: bill_flood_increase_premium_f099355d, sign_flood_cancellation_83daa4cf, issue_flood_refund_b526defb.
- Headroom: task 0 claims the renewal side (renewal_offered / policy_renewed / payment_received); task 1 claims the midterm-increase billing / cancellation / refund side. Disjoint policies and tools.

## Task 0 — closed (per-task gates)
- Values (gate evaluator, handling-time worlds): offer 453.57 (baseline 868.80), renewal term 253.43 (baseline 290.17), payment 298.19 (baseline 303.43).
- Edge sensitivity: skip renewal -> payment formula -5.16; skip offer -> renewal recompute raises on empty indicated premium.
- Fix: helper `_customer_of` was a top-level def and check_extended counted it as a task tool -> rewritten as a module-level lambda.
- check_extended --task 0 red only on task-1 tools not yet named by a policy (expected until task 1 lands); other per-task gates green.

## Task 1 — policies written
- flood_ext_increase_premium (6 factors: earned-share method, increase companion [cross home, multi], layer share, anti-selection load, insurance-to-value credit, mitigation credit [multi]); state_due.
- flood_ext_cancellation_credit (5: unearned day count [method, cross home, multi], increase premium return [method, multi], window claim deduction, sale fee return [multi], backdating retention); on_request; user tool.
- flood_ext_cancellation_refund (4: credit offset order [method, cross home, multi], interest rate, interest anchor [method, cross home], payment-method charge); on_request; root.
- Edges: credit -> increase premium (value_input, gate addl_billed, affirmative "only after"); refund -> credit (value_input, gate credits_posted, negated "No refund ... until").
- check_extended --task 0 now green (all six tools named).

## Task 1 — closed
- Values (gate evaluator, handling-time worlds): increase charge 92.81 (baseline 110.94 = the endorsement's stale request-time quote), credit 294.33 (baseline 593.60), refund 151.49 (baseline 201.52).
- Edge sensitivity: skip increase charge -> credit 203.37; skip signed cancellation -> refund recompute raises (no cancellation date) and the account stays 92.81 in debit.
- Per-task gates (--task 1) all green; task 0 per-task gates re-run green after the helper fix.

## Final difficulty-level gates (no --task)
- EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 45.00, steps mean 15.50, history_rows_max 28, branches_max 46), GROUNDING OK, CACHE-DIFF INFO (diagnostic only), SCOPE OK.
- check_traceability skipped: the published KB does not exist yet (run after erl-kb-doc-render).
- Coverage: 6 extended policies, 3 per task, disjoint; 6 task tools, 3 per task, disjoint; each task has one owner=user tool.

## Round 2 — response to audits/policy_task/flood_coverage_and_mortgagee_billing (_difficulty.md, 0.md, 1.md)

### RED items
- F-G1 / R-0-1 (cap_claim_window is a parameter): CLOSED. The factor is removed. It is replaced by `cap_tenure_start`, a genuine anchor-family method: the tenure clock runs from the household's HomeGuard start date when that is earlier and the lookback is claim-free; from the most recent flood claim payment when one lies within 120 months; otherwise from the original effective date. renewal_term now has 4 parameter factors and 1 honest method factor. Task 0 world: the clock restarts 2021-04-14, giving 65 months, the tenured cap (12%) and a term premium of 262.82. The anchor baseline gives 120 months, the loyal cap and 253.43.
- F-G2 / R-0-2 (earlier_balance_treatment: two tiers, one method): CLOSED. The factor is removed. The earlier balance enters through the baseline paragraph (a balance owed is added and a credit deducted; a credit paid by anyone else is left for refund). `late_renewal_charge` is now the method factor: per-day accrual (1.25 per day) above 15 days, one flat charge for 1–15 days, none otherwise. A fourth factor, `electronic_payment_credit` (parameter, multi-source; near-miss: the 2023 EFT payment just outside 36 months), takes the freed slot. Task 0 payment is now 306.87 (baseline 300.32).
- R-0-3 (false 492.007414 intermediate): CLOSED. The line now reads RND(493.007414 × 0.92 = 453.566821) = 453.57.
- R-1-1 (two readings of "the date the signed cancellation request was received"): CLOSED. Every occurrence in the credit rule (unsigned-sale day count, backdating) and in the refund rule (interest anchor) now reads "the date the cancellation request was received, as recorded on the request whether or not it had been signed by then". The only receipt date is created_at 2026-09-22, so the refund is uniquely 151.49. The tracing quotes the new wording.
- R-1-2 (false "consumed" assertion): CLOSED. The [Seed] card now states the terminal residue: the flood account keeps a 50.03 credit and the HomeGuard still owes 46.18. Re-applying the refund rule gives about 3.75, below the 5.00 minimum. The refund rule now says the amount is "held back … staying on this premium account for that balance".

### Observations
- O-G1: closed. The indication overwrite quotes only "At renewal the indicated premium is rated on … the renewal offer date". The renewal-term overwrite quotes only "the renewal term premium is the smaller of … rounded half-up to the cent."
- O-G2: kept. The draw allows 6 policies in 2 trees of 3. The mortgagee-side events (invoice, mortgagee change) remain governed by base flood_billing_and_mortgagee. Neither tree could carry them as a load-bearing computed write without dropping a problem that already carries weight.
- O-G3a: closed (the RC>0 guard is removed). O-G3b: closed (every HomeGuard read in the indication now filters property_address). O-G3c: kept on purpose. The factor gate requires disjoint bindings per factor, so a factor that reads the same count carries its own evidence binding. O-G3d: closed ("before the date the renewal is recorded"). O-G3e: closed (scheduled minus removed entries; the rule says "lists, and has not since removed"). O-G3f: kept, inert (only building increases exist in the worlds). O-G3g: closed (the window is anchored "before the date the charge is posted"). O-G3h: closed (in force on the request date = bound on or before it and not cancelled or expired by it; the compute checks bound_date and status). O-G3i: kept, inert (the base clamp is inherited and does not bind on task 1). O-G3j: kept, inert (one increase).
- O-G4: framework contract; no action.
- O-G5: kept. The customer paying by card on the call is her own write, and the skill requires one owner=user problem per task. The blueprint's "payments … are agent actions" describes recording received payments.
- O-G6a: closed (the condition no longer adds the fee). O-G6b: closed (the condition equals the sentence's state). O-G6c: closed (the sentence and the condition both read "every limit increase recorded on the policy with additional premium due").
- O-G7 / O-0-2 / O-1-3: kept as observations. The discount, dividend, electronic credit and late charge settle inside the payment figure, and no flood event or fee code exists to post them. The refund's held-back amount belongs to the HomeGuard line, which no write of this difficulty touches. Neither creates a second scored write: the residual credits fall below any rule's action (task 1 re-refund is about 3.75, under the 5.00 minimum).
- O-G8a: kept (borderline label, accepted by the audit). O-G8b and O-G8c: kept (tier parameters make those ladders collapse only on tiers where the zone or credit is unavailable). O-G8d: closed (the cap ladder is now the tier cap less 7 / less 3, never above the tier default). O-G8e: kept (retention and card charge are published rules with ladders). O-G8f: cap_claim_window is gone; the refund interest-anchor fall-through remains, not a straw man.
- O-0-1: closed. Edge renewal ← offer is re-declared `state_gate` (gate flood_policies.indicated_renewal_premium); the closure texts no longer claim a value dependency. The value_input floor is met by payment ← renewal.
- O-0-3: addressed. The payment computation now has a record-level near-miss: the 2023-08-22 EFT payment, 37 months back, just outside the electronic window.
- O-1-1: kept. The unposted increase charge is the posting backlog this task resolves, and the rationale states it.
- O-1-2: closed. The persona reacts only to "how the amount was worked out" and no longer anticipates retention or the offset.
- O-1-4: closed. Four home_billing rows (2310.00 billed, 2310.00 paid, 158.40 additional, 112.22 short-rate return) explain the 46.18 owed. They are read by a new find_home_billing step (evaluation step 8; later steps shift by one).

### Values after round 2
- Task 0: offer 453.57, renewal term 262.82 (was 253.43), payment 306.87 (was 298.19).
- Task 1: unchanged at 92.81, 294.33 and 151.49.

## Round 3 — response to the revision_2 re-audit (_difficulty.md, 0.md, 1.md § revision_2)

### RED items
- N-G1 (payment ← renewal edge `effect`/`condition` vs compute): CLOSED.
  - The charter `condition` now reads: the policy's effective_date is the start of the new term (the expiring term's expiration date) and a flood_premium_billed entry exists for that date. It notes that before the renewal the only matching charge is the expiring term's own.
  - The `effect` now says the binding reads the expiring term's own charge before the renewal (252.32 on task 0), and the renewal moves effective_date and posts the new-term charge.
  - Task 0's closure `condition` and `why_false` are copied to match.
- R2-0-1 (stale 1873.17 in task 0's [Business-object card]): CLOSED. It now reads "charges 1882.56 incl. the new term's 262.82 premium and 50.00 fee".

### Observations
- O-G3b: closed. The LandlordGuard read in the indication now filters `property_address`.
- O-0-3: closed.
  - Seed change: the 2023-08-22 payment is now a check and the 2024-08-16 payment an EFT.
  - The named insured's in-window payments (2024 EFT, 2025 card) are all electronic, so the credit is 1.5%. The check 37 months back is a near-miss that moves the tier: counting it gives the mixed 0.5%.
  - Task 0 payment 306.87 → 304.24. Baseline 300.32 is unchanged; the factor figures are 312.12 / 277.99 / 314.75 / 308.18.
  - Nothing else in task 0 reads the payment method. Prompt pay reads dates and returns; the payer is still the insured.
- N-G2: kept, inert. The inherited base S4 clamp ("the date the signed request is received") does not bind on task 1: 11 days on the recorded receipt date, 13 on the signing date, both ≤ 30 and after the term's effective date. The extended rules state their own receipt anchor explicitly. Re-legislating the base clamp would need a date-shifting operation the compute primitives cannot express.
- N-G3: closed. The sentence now reads "the late daily charge multiplied by every calendar day from the new term's start date to the payment date", and the ladder text matches.
- N-G4: kept. It is a framework constraint: extended policies carry no eligibility block, so a state_gate points at the record field.
- N-G5: closed. The electronic credit counts only the named insured's own payments (`payer='insured'` in compute; "the named insured's own premium payments" in the rule), so a lender's escrow check is outside it.
- N-G6: closed. The increase companion counts a HomeGuard in pending_cancellation or pending_nonrenewal as in force on the request date. Inert on task 1.
- N-1-1: closed. Task 1's [Problem-tree card] and the increase-charge step's necessity quote the current sentence ("… with additional premium due"). No pre-rework quotation remains.
- Still kept: O-G2, O-G3c, O-G3f, O-G3i, O-G3j, O-G4, O-G5, O-G7 (payment adjustments and the refund card charge are recorded by no entry; neither creates a scored write), O-G8a/b/c/e/f, O-1-1.

### Values after round 3
- Task 0: 453.57 / 262.82 / 304.24.
- Task 1: 92.81 / 294.33 / 151.49 (unchanged).
