# worklog — sr22_financial_responsibility_filings (erl-task-instantiate, M=2)

2026-10-05 START  draw (scripts/draw_counts.py --tasks 2):
  task 0: prerequisite_problems=3, factor_counts=[4, 6, 5, 5]
  task 1: prerequisite_problems=2, factor_counts=[4, 4, 6]

## Difficulty pre-check (Step 0)
- Writable tables of this category: sr22_filings (holding), sr22_ledger (events). The only numeric field in
  either is sr22_ledger.fee_amount, so every scored computation of this difficulty is a filing charge booked
  on an sr22_fee_assessed row. Known tension with the frozen blueprint: sr22_fee_assessed declares an
  unconditional trigger to billing:billing_fee_charged (the charge is later billed). No sr22 numeric field
  exists outside that event, so the tools book the sr22 ledger row only and never write billing; the billing
  posting stays with the billing difficulty's own process. sr22_request (new filing) is not used at all
  (it creates a holding and triggers auto:auto_filing_flag_update).
- Record-visible problems available: corrected refiling (rejected filing), reinstatement filing
  (cancel_notified filing on a reinstated policy), amendments by certified fact (vehicle / address /
  policy number / name), release at the end of the requirement. Name change and release are only knowable
  from the customer -> they are the two roots; the five record-visible problems are prerequisites.
- Status exclusivity on one filing: rejected (refile) vs cancel_notified (restore) vs accepted (release).
  Partition: task 0 = release root + restore + vehicle amendment + address amendment (one Out-of-State
  SR-22 Owner Certificate, IL order); task 1 = name-amendment root + corrected refiling + policy-number
  amendment (one Out-of-State SR-22 Owner-Operator Certificate, TN order). Each task's tree is a chain.
- Tools (uuid8 generated one by one with uuid.uuid4().hex[:8]):
  restore_certificate_19610618 (agent), amend_certificate_vehicles_869f2144 (agent),
  amend_certificate_address_1c393d15 (agent), request_filing_release_10a5eab7 (user)  -> task 0
  submit_filing_correction_4a6499e2 (user), amend_certificate_policy_9772f7fb (agent),
  amend_certificate_name_9daa06e9 (agent)  -> task 1

## Task 0 (closed)
- Root sr22_ext_release_notice_charge (user tool) <- address amendment <- vehicle amendment <- reinstatement filing
  (chain, all edges value_input, all state form). Filing: Out-of-State SR-22 Owner Certificate, IL order, Denise Tomczak.
- Factor counts: reinstatement 6, vehicle 5, address 5, release 4 (= draw [4,6,5,5]).
- Expected: 33.85 / 33.75 / 21.00 / 10.25; baselines 25.00 / 15.00 / 15.00 / 0.00.
- Prerequisite skips: vehicle 42.35, address 36.00, release 8.75.
- Revision: check_extended failed (helper `_filing` counted as an unnamed task tool, and the substring occurred in
  rule words like release_filing_fee) -> helper inlined into each tool -> EXTENDED OK.
- Gates --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.

## Task 1 (closed)
- Snapshot: task 0 occupies reinstatement / vehicle / address / release policies and their 4 tools. Task 1 claims the
  remaining three: corrected refiling (user tool), policy-number amendment, name amendment (root, on_request).
- Root sr22_ext_name_amendment_charge <- policy-number amendment <- corrected refiling (chain, both value_input, state form).
  Filing: Out-of-State SR-22 Owner-Operator Certificate, TN order, Brianna Vance/Tolliver.
- Factor counts: corrected refiling 4, policy-number 6, name 4 (= draw [4,4,6]).
- Expected: 32.50 / 19.25 / 9.25; baselines 0.00 / 15.00 / 15.00. Prerequisite skips: policy-number 27.85, name 14.25.
- Revision: 'is not None' is outside the restricted grammar -> '!= None'. Release policy (task 0) and corrected
  refiling policy both declare an overwrite of the base clause "a fee of 0.00 is not assessed" (their baselines are 0.00;
  a zero sum is still booked at 0.00 on the transmission) - task 0 regated after the edit.
- Gates --task 1: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK.

## Difficulty-level closing
- Coverage: 7 extended policies, task 0 {reinstatement, vehicle, address, release}, task 1 {corrected refiling,
  policy-number, name}; tools pairwise disjoint; every policy fires on its gold call.
- Prerequisite sentences: 5 edges, 3 negated-direction (address, release, name), 2 affirmative (vehicle, policy-number).
- Known gaps owned by the frozen blueprint (not patched here): sr22_fee_assessed rows declare an unconditional billing
  trigger; the auto financial-responsibility indicator is switched only by the auto charter's own event (task 0's
  release and task 1's move of the certificate to the replacement policy leave it to that event).
- Final gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (branches mean
  53.50, steps mean 18.00, history_rows_max 9, branches_max 67); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK.
  check_traceability not run (KB not yet published).

## Round 2 — rework against audits/policy_task/sr22_financial_responsibility_filings/ (revision 1)
- G1 (rate ladders inverted for in-state certificates): restoration_rate tiers = reinstatement_filing_fee
  + bounce_restore_surcharge 10.00 / + repeat_restore_surcharge 5.00 / alone (monotone on every certificate);
  vehicle, policy-number and name amendment rates now use flat schedules (new params standard_change_rate,
  standard_policy_change_rate, standard_name_rate = 15.00 as the standard rate and fall-through; baseline.rule and
  baseline.params updated; base "The amendment carries amended_filing_fee" stays superseded by the declared overwrite).
- G2 (address_reprint paper conjunct universal): ladder now by certificate age only — >= 36 months full_reprint_charge
  4.00, 12-35 months partial_reissue_charge 2.00, else none (params paper_reprint_charge/electronic_reissue_charge
  replaced by full_reprint_charge/partial_age_months/partial_reissue_charge).
- G3 (correction_rate customer-code conjunct universal, fall-through unreachable): ladder now by rejections on record
  and the rejected version — >= 2 rejections -> repeat 20.00; one rejection of the original certificate -> first 10.00;
  one rejection of a later transmission (amendment etc.) -> refiling_fee_after_rejection. Binding latest_response_code
  replaced by rejected_version_kind (latest transmission type). All tiers reachable by the customer's correction.
- G4 (latent "a fee of 0.00 is not assessed" for vehicle/policy/name amendments): with the flat schedules the sums are
  bounded below (vehicle >= 5.00, policy-number >= 4.00, name >= 2.00), so no booked zero can arise; release and
  corrected refiling keep their declared overwrite.
- O3: all five prerequisite conditions restate their sentences exactly (added conjuncts dropped, address edge scope added).
- O4: release prerequisite sentence reworded to name one address amendment entered no earlier than the recording date
  of the latest garaging change (policy_source in charter and task 0 updated).
- O6: restore_certificate_19610618 renamed restore_certificate_8ba85022 (fresh uuid4) in charter, tools and task 0.
- O1/O2 (billing posting, auto filing indicator), O5 (base amendment status gate), O7 (fraction+rounding methods),
  O8/O9 (realism notes): blueprint-owned or no consequence; no change.
- Scored values unchanged: task 0 33.85/33.75/21.00/10.25, task 1 32.50/19.25/9.25; factor sensitivities and
  baselines identical. Task JSON proof texts (factor_trace, tier_taken, tracing, prerequisite_closure, rationale [13])
  updated to the new ladders.
