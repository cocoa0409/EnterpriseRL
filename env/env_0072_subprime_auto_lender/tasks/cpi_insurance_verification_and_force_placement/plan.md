# plan.md — cpi_insurance_verification_and_force_placement (env_0072), M=2

## Draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2 (3 problems), factor_counts=[4,4,6]
- task 1: prerequisite_problems=1 (2 problems), factor_counts=[4,6]
- 5 extended policies total; pairwise disjoint scopes.

## Status
- [x] read references + blueprint (cpi.yaml, schema, share_tools)
- [x] design trees (below), trigger list
- [x] task 0 extended+tools+json, gates
- [x] task 1 extended+tools+json, gates
- [x] final gates, worklog tail line

## Scratch: /tmp/cpi_insurance_verification_and_force_placement_0072/

## Feasibility finding (base thinness, routed around)
- Trigger rule: cpi_premium_charged(added_to_contract_balance)->contract and cpi_premium_refunded(credited_to_contract_balance /
  credited_to_deficiency_balance)->contract/deficiency are cross-category => my tools may only write refunds with
  refund_disposition mailed_to_borrower, and never capitalised charges. Mailed refunds exist only once the contract left
  servicing (paid_off) => every tree lives on a CLOSED record of a paid-off contract.
- Every problem must carry a computation; the only scored values my events carry are refund amount_usd and the proof
  review outcome proof_result (string result, check_compute compares str). Proof attributes are only in records after a
  review, so a review problem is a RE-REVIEW of a proof already on file (earlier automated first-pass rejection).
- Base forbids review on a closed record -> scoped overwrite: re-review of a proof already rejected on the record, whose
  coverage began before the closing date, solely to fix refunds; never changes status/policy on file/notices.

## Trees (design)
- T0 (3 problems, [4,4,6]): record closed by payoff on the last day of a billing period; earlier proof (insurer channel)
  rejected; re-review accepts; refunds: charge in which proven coverage began (partial, root, USER, 6 factors) and the
  later charge wholly inside proven coverage (full + interest, agent, 4); re-review (agent, 4).
  edges: start_refund -> re-review (value_input: proof start date), start_refund -> covered_refund (state_gate),
         covered_refund -> re-review (value_input).
- T1 (2 problems, [4,6]): record closed by payoff inside a billing period, proof start inside that period; earlier
  upload proof rejected; re-review of upload (agent, 4) -> closing-period refund (USER, 6), value_input.
- Refund amounts include contract interest the capitalised premium accrued (interest_on_capitalized_premium) from its
  capitalisation (contract_ancillary_charge txn) to the payoff — declared overwrite of cpi_cancellation_refund.

## Trigger list (events my tools write)
- cpi_proof_verified (row): triggers cpi_policy_on_file_updated / cpi_notice_sent — both cpi (in-category). OK.
- cpi_premium_refunded with refund_disposition=mailed_to_borrower fixed in tool: triggers only fire for
  credited_to_contract_balance / credited_to_deficiency_balance -> none fire. OK.
- Never written: cpi_premium_charged (added_to_contract_balance), contract/deficiency/recovery/gap/dealer events.

## Progress log
- Policies drafted in scratch (/tmp/cpi_insurance_verification_and_force_placement_0072/pol_t0.py, pol_t1.py):
  T0: cpi_ext_feed_proof_rereview(4), cpi_ext_upload_proof_rereview(4), cpi_ext_closing_month_refund(6, root, user)
  T1: cpi_ext_fax_proof_rereview(4), cpi_ext_closing_period_refund(6, root, user)
- Next: builder (extended yaml + task_tools + task json) in scratch gen.py, then gates per task.

## Round 2 redesign (audit policy_task r1: CW-1..CW-7 + task REDs)
Refund = unearned premium + finance charge accrued on the capitalised premium (contract interest method:
simple interest at the contract rate, actual/365, from the date the premium reached the contract balance to
payoff). No delay interest, no credits (CW-7). One acceptance schedule shared by all three re-review rules
(CW-4.3); one refund schedule shared by both refund rules (CW-4.1/4.2).
- Re-review factors (all three, identical ladders): lienholder route (closed -> waived / open & insurer+policy
  number on file -> on-file policy / own flag); comprehensive ceiling (value+model year); collision ceiling
  (credit tier, better tiers more lenient); coverage reach (closed -> effective on/before closed date / open &
  repossessed -> expiry >= repossession date / expiry >= review + min days). Absent proof -> not_applicable
  with sentinel reads (no crash). Binder clause retired with a self-naming tail.
- Refund factors (both refunds, identical schedules): proof days (expiry inside period -> bounded / on-file
  policy reinstated -> from day after on-file expiry / latest effective date); gap grace (compliance months);
  lienholder share; deductible share; finance factor (rate cap -> lower of apr and cap / capitalised -> apr /
  never capitalised -> none). CM only: binder credit (same-insurer bridge / other-insurer capped). CP only:
  post-closing days (wire/certified -> from closed date / ACH-check-card -> after funds-final date / base).
- Seeds: contracts inside tier limits (T0 Tier 5 54 months, LTV <= 115 %; T1 Tier 4 60 months, LTV <= 120 %).
- Personas: correction lines removed.

## Round 2 probe table (scratch copies of both worlds; check_compute DSL evaluator)
| probe | policy | result | expected by rule |
| --- | --- | --- | --- |
| T0 as seeded (proof present) | feed_proof_rereview | accepted | accepted |
| T0 same-day tie, second entry recorded later (deductible 5000) | feed_proof_rereview | accepted | first recorded wins -> accepted |
| T0 later decoy entry of same channel (deductible 5000) | feed_proof_rereview | rejected_deductible_too_high | latest entry read -> rejected_deductible_too_high |
| T0 record reopened (open, contract paid_off) | feed_proof_rereview | rejected_no_lienholder | lienholder by own flag -> rejected_no_lienholder |
| T0 contract model year empty | feed_proof_rereview | accepted | model year 0 -> comp ceiling tier applies, no crash |
| T1 as seeded (proof present) | feed_proof_rereview | not_applicable | not_applicable (absent) / accepted |
| T1 same-day tie, second entry recorded later (deductible 5000) | feed_proof_rereview | not_applicable | first recorded wins -> accepted |
| T1 later decoy entry of same channel (deductible 5000) | feed_proof_rereview | not_applicable | latest entry read -> rejected_deductible_too_high |
| T1 record reopened (open, contract paid_off) | feed_proof_rereview | not_applicable | lienholder by own flag -> rejected_no_lienholder |
| T1 contract model year empty | feed_proof_rereview | not_applicable | model year 0 -> comp ceiling tier applies, no crash |
| T0 as seeded (proof present) | upload_proof_rereview | accepted | accepted |
| T0 same-day tie, second entry recorded later (deductible 5000) | upload_proof_rereview | accepted | first recorded wins -> accepted |
| T0 later decoy entry of same channel (deductible 5000) | upload_proof_rereview | rejected_deductible_too_high | latest entry read -> rejected_deductible_too_high |
| T0 record reopened (open, contract paid_off) | upload_proof_rereview | rejected_no_lienholder | lienholder by own flag -> rejected_no_lienholder |
| T0 contract model year empty | upload_proof_rereview | accepted | model year 0 -> comp ceiling tier applies, no crash |
| T1 as seeded (absent record) | upload_proof_rereview | not_applicable | not_applicable (absent) / accepted |
| T0 as seeded (absent record) | fax_proof_rereview | not_applicable | not_applicable (absent) / accepted |
| T1 as seeded (proof present) | fax_proof_rereview | accepted | accepted |
| T1 same-day tie, second entry recorded later (deductible 5000) | fax_proof_rereview | accepted | first recorded wins -> accepted |
| T1 later decoy entry of same channel (deductible 5000) | fax_proof_rereview | rejected_deductible_too_high | latest entry read -> rejected_deductible_too_high |
| T1 record reopened (open, contract paid_off) | fax_proof_rereview | rejected_no_lienholder | lienholder by own flag -> rejected_no_lienholder |
| T1 contract model year empty | fax_proof_rereview | accepted | model year 0 -> comp ceiling tier applies, no crash |
| T0 gold handling world | closing_month_refund | 26.51 | gold |
| T0 no accepted proof (opening world) | closing_month_refund | 0.0 | expired original proof gives no proof days; no crash |
| T0 decoy refund already booked against the charge | closing_month_refund | 26.51 | compute unchanged (dedup gate is the base eligibility) |
| T0 decoy accepted agent-call proof from the period start | closing_month_refund | 26.51 | standard proof days move only if it is the latest effective; tiers read their channel |
| T0 latest charge held (never capitalised) | closing_month_refund | 31.63 | previous capitalised charge read; no crash |
| T0 ancillary posting absent | closing_month_refund | 26.02 | finance factor 0 |
| T0 rate cap in force (apr below original) | closing_month_refund | 26.13 | finance at lower of apr and cap |
| T0 lapse_date empty | closing_month_refund | 21.25 | gap allowance 0 |
| T1 gold handling world | closing_period_refund | 61.18 | gold |
| T1 no accepted proof (opening world) | closing_period_refund | 41.72 | expired original proof gives no proof days; no crash |
| T1 decoy refund already booked against the charge | closing_period_refund | 61.18 | compute unchanged (dedup gate is the base eligibility) |
| T1 decoy accepted agent-call proof from the period start | closing_period_refund | 61.18 | standard proof days move only if it is the latest effective; tiers read their channel |
| T1 latest charge held (never capitalised) | closing_period_refund | 23.8 | previous capitalised charge read; no crash |
| T1 ancillary posting absent | closing_period_refund | 60.54 | finance factor 0 |
| T1 rate cap in force (apr below original) | closing_period_refund | 60.69 | finance at lower of apr and cap |
| T1 lapse_date empty | closing_period_refund | 54.23 | gap allowance 0 |
Edges: gap of zero days (binder expiry the day before the policy start) -> MX(0, DAYS-1) = 0; negative overlap (binder after policy start) -> binder days MX(0, ...) = 0; date difference 0 (one-day proof) -> 1 proof day; month-end periods use DAYS on ISO dates (31-, 30-, 28-day periods handled by DAYS); no accepted proof -> proof days 0, never a crash; charge period ending exactly on the closed date -> post-closing days 0 (closing-month scope). Same-day ties: every LATEST read states that the entry recorded first wins; the refund rules read proofs by policy_effective_date, so two re-reviews written at the frozen clock never tie unless their coverage starts on the same day.

## Round 3 (coordinator ruling: only rules a real CPI program uses)
Feasibility check of the suggested held-premium route: cpi_evt_premium_billing holds a premium only "while
borrower-submitted proof received within the last proof_review_hold_days days is still unreviewed"; no table
records a received-but-unreviewed proof (cpi_proof_verified rows exist only once reviewed), so a held charge
cannot be evidenced from records; a held release is always "for its full amount". Route not adopted.
Decision: strike every company-chosen schedule (lienholder/deductible shares, binder cap, tenure grace, finance
part, lienholder waiver tiers, post-closing offset). What remains is real: refund = unearned premium only;
refund factors = coverage counted from an accepted binder bridging into the policy proof, and coverage ending
at the policy proof's expiration inside the period; re-review factors = deductible ceilings and coverage-reach
anchor; lienholder test back to the base own-flag rule (seeded proofs list the company and were first rejected
for the deductible). The drawn factor counts (4..6) cannot be reached with real rules on this charter; the
shortfall is reported as the actual gate count rather than filled with invented schedules.

## Round 3 probe table
| probe | policy | result | expected by rule |
| --- | --- | --- | --- |
| T0 as seeded (2 entries of the channel) | feed_proof_rereview | accepted | accepted if latest entry rejected for deductible/expiry, else not_applicable |
| T0 same-day tie, later-recorded twin with 5000 deductible | feed_proof_rereview | accepted | first recorded wins |
| T0 later decoy entry without lienholder listing | feed_proof_rereview | rejected_no_lienholder | latest entry read; rejected_no_lienholder if it is a deductible/expiry rejection, else not_applicable |
| T0 record open (not closed) | feed_proof_rereview | rejected_expiring | reach by expiry 15 days after review |
| T1 as seeded (1 entries of the channel) | feed_proof_rereview | not_applicable | accepted if latest entry rejected for deductible/expiry, else not_applicable |
| T1 same-day tie, later-recorded twin with 5000 deductible | feed_proof_rereview | not_applicable | first recorded wins |
| T1 later decoy entry without lienholder listing | feed_proof_rereview | not_applicable | latest entry read; rejected_no_lienholder if it is a deductible/expiry rejection, else not_applicable |
| T1 record open (not closed) | feed_proof_rereview | not_applicable | reach by expiry 15 days after review |
| T0 as seeded (1 entries of the channel) | upload_proof_rereview | accepted | accepted if latest entry rejected for deductible/expiry, else not_applicable |
| T0 same-day tie, later-recorded twin with 5000 deductible | upload_proof_rereview | accepted | first recorded wins |
| T0 later decoy entry without lienholder listing | upload_proof_rereview | rejected_no_lienholder | latest entry read; rejected_no_lienholder if it is a deductible/expiry rejection, else not_applicable |
| T0 record open (not closed) | upload_proof_rereview | rejected_expiring | reach by expiry 15 days after review |
| T1 as seeded (0 entries of the channel) | upload_proof_rereview | not_applicable | accepted if latest entry rejected for deductible/expiry, else not_applicable |
| T0 as seeded (0 entries of the channel) | fax_proof_rereview | not_applicable | accepted if latest entry rejected for deductible/expiry, else not_applicable |
| T1 as seeded (1 entries of the channel) | fax_proof_rereview | accepted | accepted if latest entry rejected for deductible/expiry, else not_applicable |
| T1 same-day tie, later-recorded twin with 5000 deductible | fax_proof_rereview | accepted | first recorded wins |
| T1 later decoy entry without lienholder listing | fax_proof_rereview | rejected_no_lienholder | latest entry read; rejected_no_lienholder if it is a deductible/expiry rejection, else not_applicable |
| T1 record open (not closed) | fax_proof_rereview | rejected_expiring | reach by expiry 15 days after review |
| T0 gold handling world | closing_month_refund | 56.67 | gold |
| T0 opening world (no accepted proof reaching the period) | closing_month_refund | 0.0 | no proof days; base closure days only (CP) / 0 (CM) |
| T0 decoy held charge for the same period | closing_month_refund | 56.67 | held charge excluded from the premium sum |
| T0 decoy accepted agent-call proof from the period start | closing_month_refund | 56.67 | outside the rule scope (agent-call proof); standard read may move |
| T0 accepted proofs one day long (date difference 0) | closing_month_refund | 5.15 | one covered day each |
| T1 gold handling world | closing_period_refund | 65.36 | gold |
| T1 opening world (no accepted proof reaching the period) | closing_period_refund | 37.84 | no proof days; base closure days only (CP) / 0 (CM) |
| T1 decoy held charge for the same period | closing_period_refund | 65.36 | held charge excluded from the premium sum |
| T1 decoy accepted agent-call proof from the period start | closing_period_refund | 65.36 | outside the rule scope (agent-call proof); standard read may move |
| T1 accepted proofs one day long (date difference 0) | closing_period_refund | 41.28 | one covered day each |

## Round 4 design (coordinator: counts fixed, gates 7/7, real lender/vendor schedules allowed)
Placement of draws: T0 [4,4,6] -> feed re-review 6, upload (binder) re-review 4, closing-month refund 4;
T1 [4,6] -> fax re-review 6, closing-period refund 4.
- Re-review schedule (identical in all three rules; one record dimension per factor):
  comprehensive allowance by model year (param), comprehensive allowance by loan-to-value at signing (param),
  collision allowance by vehicle value on the record (param), collision allowance by credit tier (param);
  for policies (feed, fax) also: expiry buffer by contract state (param) and the date the buffer is
  measured from by record status (method: closed -> first review date; open & repossessed -> repossession
  date; otherwise the re-review date). Uploaded binders are held to the base binder-period test and a
  closed-record start test instead (binders are temporary by nature), so the upload rule carries 4 factors.
- Refund schedule (identical in both refund rules): coverage-span counting (method: two accepted proofs ->
  union of bounded spans; one proof ending inside the period -> its bounded span; otherwise base days from
  the latest effective date), lapse tolerance per uncovered stretch by plan (param), closing-day adjustment
  by payoff funds finality (param), period-day basis by contract state filing (param). Unearned premium
  only; no shares, credits, tenure grading, insurer-identity caps or interest.

## Round 4 probe table
| probe | policy | result | expected by rule |
| --- | --- | --- | --- |
| T0 as seeded (2 entries of the channel) | feed_proof_rereview | accepted | accepted when the latest entry is a deductible/expiry rejection the schedule clears; not_applicable when none or already accepted |
| T0 same-day twin recorded later (5000 deductible) | feed_proof_rereview | accepted | entry recorded first wins |
| T0 later decoy entry without listing | feed_proof_rereview | rejected_no_lienholder | latest entry read |
| T0 record open | feed_proof_rereview | rejected_expiring | reach date = re-review date |
| T0 contract model year empty | feed_proof_rereview | rejected_deductible_too_high | no model-year allowance; no crash |
| T1 as seeded (1 entries of the channel) | feed_proof_rereview | not_applicable | accepted when the latest entry is a deductible/expiry rejection the schedule clears; not_applicable when none or already accepted |
| T1 same-day twin recorded later (5000 deductible) | feed_proof_rereview | not_applicable | entry recorded first wins |
| T1 later decoy entry without listing | feed_proof_rereview | not_applicable | latest entry read |
| T1 record open | feed_proof_rereview | not_applicable | reach date = re-review date |
| T1 contract model year empty | feed_proof_rereview | not_applicable | no model-year allowance; no crash |
| T0 as seeded (1 entries of the channel) | upload_proof_rereview | accepted | accepted when the latest entry is a deductible/expiry rejection the schedule clears; not_applicable when none or already accepted |
| T0 same-day twin recorded later (5000 deductible) | upload_proof_rereview | accepted | entry recorded first wins |
| T0 later decoy entry without listing | upload_proof_rereview | rejected_no_lienholder | latest entry read |
| T0 record open | upload_proof_rereview | rejected_expiring | reach date = re-review date |
| T0 contract model year empty | upload_proof_rereview | rejected_deductible_too_high | no model-year allowance; no crash |
| T1 as seeded (0 entries of the channel) | upload_proof_rereview | not_applicable | accepted when the latest entry is a deductible/expiry rejection the schedule clears; not_applicable when none or already accepted |
| T0 as seeded (0 entries of the channel) | fax_proof_rereview | not_applicable | accepted when the latest entry is a deductible/expiry rejection the schedule clears; not_applicable when none or already accepted |
| T1 as seeded (1 entries of the channel) | fax_proof_rereview | accepted | accepted when the latest entry is a deductible/expiry rejection the schedule clears; not_applicable when none or already accepted |
| T1 same-day twin recorded later (5000 deductible) | fax_proof_rereview | accepted | entry recorded first wins |
| T1 later decoy entry without listing | fax_proof_rereview | rejected_no_lienholder | latest entry read |
| T1 record open | fax_proof_rereview | rejected_expiring | reach date = re-review date |
| T1 contract model year empty | fax_proof_rereview | rejected_deductible_too_high | no model-year allowance; no crash |
| T0 gold handling world | closing_month_refund | 69.2 | gold |
| T0 opening world | closing_month_refund | 2.66 | no accepted proof reaching the period; no crash |
| T0 decoy held charge for the same period | closing_month_refund | 69.2 | held charge excluded |
| T0 payoff by ACH instead of wire | closing_month_refund | 66.54 | closed date not refunded; one post-closing day earned |
| T0 payoff by moneygram | closing_month_refund | 66.54 | no closing-day adjustment |
| T0 contract state outside the filing schedule | closing_month_refund | 66.97 | actual period days |
| T0 Tier 6 contract | closing_month_refund | 58.56 | no lapse tolerance: uncovered stretches stay earned |
| T1 gold handling world | closing_period_refund | 81.43 | gold |
| T1 opening world | closing_period_refund | 40.71 | no accepted proof reaching the period; no crash |
| T1 decoy held charge for the same period | closing_period_refund | 81.43 | held charge excluded |
| T1 payoff by ACH instead of wire | closing_period_refund | 74.64 | closed date not refunded; one post-closing day earned |
| T1 payoff by moneygram | closing_period_refund | 78.04 | no closing-day adjustment |
| T1 contract state outside the filing schedule | closing_period_refund | 82.56 | actual period days |
| T1 Tier 6 contract | closing_period_refund | 74.64 | no lapse tolerance: uncovered stretches stay earned |
Edges: zero-day uncovered stretch -> 0; overlapping spans counted once; one-day proof -> 1 day; month-end periods by DAYS on ISO dates; a refund below refund_min_check_usd is not mailed (base, kept in force).

## Round 5 design (audit r3: R3-A..R3-D; coordinator route)
- Dropped: day basis (premium earned by actual days, base), minimum policy terms, the closing-day adjustment. A
  closing-coverage-end factor by payoff funds finality was considered and dropped: the contract charter's clearance
  is in business days excluding federal holidays, which the compute cannot reproduce exactly per payment method, and
  the recorded funds_final_date alone gives one tier, not a ladder.
- Re-reviews: shared ladders comprehensive allowance by model year, collision allowances by contract book value
  and credit tier, reach date by record status (method). Issued policies (feed, fax) also carry the expiry
  buffer by contract state and a loan-to-value-at-signing comprehensive allowance (binders take none).
  The upload rule re-reviews only binders: its pick is the most recent upload, and when that upload shows a period
  longer than binder_max_days the outcome is not_applicable (compute enforces it). Every tail restates that such
  uploads, like first reviews and agent-call proofs, are reviewed only on open records (R3-C2).
- Refunds (one schedule in both rules): coverage counting (method: union of two reaching spans / one span expiring
  inside the period / latest effective date through the closed date), replacement grace by CPI plan (first days of
  a gap between two reaching spans), renewal grace by contract state (first days after the last reaching span
  before the closed date), refund basis (method: full_no_lapse when a counting proof took effect by the placement
  date; pro_rata_from_proof_effective when a counting proof reaches the covered stretch; standard
  pro_rata_from_closure). Reads: only the named insurer channel and declarations_page_upload. "Counts" = expires on
  or after the period start; "reaches" = counts and took effect on or before the closed date (stated in rule).
  The refund tools now take refund_basis as an argument.
- Worlds: T0 feed month-to-month policy 06-08..07-08 (reviewed 06-26) and binder 07-14..07-27 (reviewed 07-16);
  T1 fax month-to-month policy 08-14..09-14 (reviewed 09-08), binder 09-19..09-25 rejected 09-21 and accepted at
  a re-review on 10-06; contracts unchanged (inside tier limits).

## Round 5 probe table (scratch copies of both worlds; check_compute DSL evaluator)
| world / change | rule | result | expected |
| --- | --- | --- | --- |
| T0 as seeded | feed_proof_rereview | accepted | accepted |
| T0 record open, contract not repossessed | feed_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T0 record open, contract repossessed on the first-review date | feed_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T0 model year 2022 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | feed_proof_rereview | not_applicable | not_applicable |
| T0 LTV 125 percent (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T0 contract state MS (fall-through) | feed_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T0 sibling state of the same buffer tier | feed_proof_rereview | accepted | as seeded |
| T0 as seeded | upload_proof_rereview | accepted | accepted |
| T0 record open, contract not repossessed | upload_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T0 record open, contract repossessed on the first-review date | upload_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T0 model year 2022 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | upload_proof_rereview | not_applicable | not_applicable |
| T0 later upload is a 6-month declarations page | upload_proof_rereview | not_applicable | most recent upload not a binder -> not_applicable (R3-D1) |
| T0 the upload shows 38 days | upload_proof_rereview | not_applicable | not a binder -> not_applicable |
| T1 as seeded | fax_proof_rereview | accepted | accepted |
| T1 record open, contract not repossessed | fax_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T1 record open, contract repossessed on the first-review date | fax_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T1 model year 2022 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T1 book value 19000 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T1 Tier 6 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T1 first rejection not re-reviewed | fax_proof_rereview | not_applicable | not_applicable |
| T1 LTV 125 percent (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T1 contract state MS (fall-through) | fax_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T1 sibling state of the same buffer tier | fax_proof_rereview | accepted | as seeded |
| T0 after re-reviews | closing_month_refund | 64.4 | pro rata; union + both graces |
| T0 after re-reviews: basis | closing_month_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T0 only the insurer_edi_feed proof reaches | closing_month_refund | 20.61 | one proof expiring inside: its span + renewal grace |
| T0 only the insurer_edi_feed proof, running past the period | closing_month_refund | 79.85 | fall-through: latest effective through closed date |
| T0 binder entry reinstates the policy on file without a gap | closing_month_refund | 79.85 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T0 insurer_edi_feed proof took effect on the placement date | closing_month_refund | 79.85 | full_no_lapse: whole charge |
| T0 insurer_edi_feed proof took effect on the placement date: basis | closing_month_refund | full_no_lapse | full_no_lapse |
| T0 only an upload taking effect after the closed date counts | closing_month_refund | 0.0 | pro_rata_from_closure: post-closing days only (CM: none) |
| T0 only an upload taking effect after the closed date: basis | closing_month_refund | pro_rata_from_closure | pro_rata_from_closure |
| T0 plan A | closing_month_refund | 64.4 | replacement grace grace_ab |
| T0 plan D | closing_month_refund | 61.82 | replacement grace grace_cd |
| T0 plan E | closing_month_refund | 56.67 | replacement grace 0 (fall-through) |
| T0 contract state LA | closing_month_refund | 64.4 | renewal grace grace_gulf |
| T0 contract state AR | closing_month_refund | 59.24 | renewal grace grace_plains |
| T0 contract state NM | closing_month_refund | 51.52 | renewal grace 0 (fall-through) |
| T0 extra accepted agent-call proof covering the period | closing_month_refund | 64.4 | not read (named channels only): as after re-reviews |
| T0 extra accepted proof of the other insurer channel | closing_month_refund | 64.4 | not read: as after re-reviews |
| T0 the accepted upload is a long declarations page | closing_month_refund | 74.7 | read like any accepted upload: span to the closed date |
| T1 after re-reviews | closing_period_refund | 89.44 | pro rata; union + both graces |
| T1 after re-reviews: basis | closing_period_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T1 only the insurer_fax proof reaches | closing_period_refund | 58.48 | one proof expiring inside: its span + renewal grace |
| T1 only the insurer_fax proof, running past the period | closing_period_refund | 103.2 | fall-through: latest effective through closed date |
| T1 binder entry reinstates the policy on file without a gap | closing_period_refund | 103.2 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T1 insurer_fax proof took effect on the placement date | closing_period_refund | 103.2 | full_no_lapse: whole charge |
| T1 insurer_fax proof took effect on the placement date: basis | closing_period_refund | full_no_lapse | full_no_lapse |
| T1 only an upload taking effect after the closed date counts | closing_period_refund | 37.84 | pro_rata_from_closure: post-closing days only (CM: none) |
| T1 only an upload taking effect after the closed date: basis | closing_period_refund | pro_rata_from_closure | pro_rata_from_closure |
| T1 plan A | closing_period_refund | 92.88 | replacement grace grace_ab |
| T1 plan D | closing_period_refund | 89.44 | replacement grace grace_cd |
| T1 plan E | closing_period_refund | 82.56 | replacement grace 0 (fall-through) |
| T1 contract state LA | closing_period_refund | 96.32 | renewal grace grace_gulf |
| T1 contract state AR | closing_period_refund | 89.44 | renewal grace grace_plains |
| T1 contract state NM | closing_period_refund | 79.12 | renewal grace 0 (fall-through) |
| T1 extra accepted agent-call proof covering the period | closing_period_refund | 89.44 | not read (named channels only): as after re-reviews |
| T1 extra accepted proof of the other insurer channel | closing_period_refund | 89.44 | not read: as after re-reviews |
| T1 the accepted upload is a long declarations page | closing_period_refund | 96.32 | read like any accepted upload: span to the closed date |

## Round 6 design (audit r4: R4-A, R4-B, R4-C; coordinator route)
- Refund-basis method struck as a factor: with the base proof basis as the standard, its other tiers (full_no_lapse,
  closure) would replace the covered-day count and silence the other factors. The basis is now a plain branch
  (full_no_lapse when a counting proof took effect by the placement date; pro_rata_from_closure when no counting
  proof reaches; otherwise pro_rata_from_proof_effective). The tool keeps the refund_basis argument.
- Standard method = base pro rata from the proof's effective date by actual days: covered days from the latest
  reaching proof's effective date through the closed date, plus the post-closing days, no grace (never 0.00 in scope).
- Refund factors: coverage counting (method: union / one span expiring inside / standard); replacement-gap grace
  as the sum of three allowances (like the deductible ceilings): CPI plan, contract state, vehicle model year.
  The renewal-stretch grace is dropped (no stretch exists once proofs start inside the charged period).
- R4-C: proofs re-seeded to start inside the refunded charge's period, so no other charge is reached by any
  accepted proof under the kept base rule. T0: binder 07-06..07-11 (reviewed 07-08), feed month-to-month policy
  07-18..08-18 (reviewed 08-04). T1: payoff moved to 2026-10-08 (contract ledger re-simulated, wire), binder
  09-12..09-16 (rejected 09-14, accepted re-review 10-10), fax month-to-month policy 09-21..10-21 (reviewed 10-07).

## Round 6 probe table (scratch copies of both worlds; check_compute DSL evaluator)
| world / change | rule | result | expected |
| --- | --- | --- | --- |
| T0 as seeded | feed_proof_rereview | accepted | accepted |
| T0 record open, contract not repossessed | feed_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T0 record open, contract repossessed on the first-review date | feed_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T0 model year 2022 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | feed_proof_rereview | not_applicable | not_applicable |
| T0 LTV 125 percent (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T0 contract state MS (fall-through) | feed_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T0 sibling state of the same buffer tier | feed_proof_rereview | accepted | as seeded |
| T0 as seeded | upload_proof_rereview | accepted | accepted |
| T0 record open, contract not repossessed | upload_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T0 record open, contract repossessed on the first-review date | upload_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T0 model year 2022 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | upload_proof_rereview | not_applicable | not_applicable |
| T0 later upload is a 6-month declarations page | upload_proof_rereview | not_applicable | most recent upload not a binder -> not_applicable (R3-D1) |
| T0 the upload shows 38 days | upload_proof_rereview | not_applicable | not a binder -> not_applicable |
| T1 as seeded | fax_proof_rereview | accepted | accepted |
| T1 record open, contract not repossessed | fax_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T1 record open, contract repossessed on the first-review date | fax_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T1 model year 2022 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T1 book value 19000 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T1 Tier 6 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T1 first rejection not re-reviewed | fax_proof_rereview | not_applicable | not_applicable |
| T1 LTV 125 percent (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T1 contract state MS (fall-through) | fax_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T1 sibling state of the same buffer tier | fax_proof_rereview | accepted | as seeded |
| T0 after re-reviews | closing_month_refund | 77.27 | pro rata; union + gap allowances |
| T0 after re-reviews: basis | closing_month_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T0 only the uploaded binder reaches (expires inside the period) | closing_month_refund | 15.45 | one proof expiring inside: its span only |
| T0 only the insurer_edi_feed proof, running past the period | closing_month_refund | 48.94 | fall-through: latest effective through closed date |
| T0 binder entry reinstates the policy on file without a gap | closing_month_refund | 79.85 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T0 insurer_edi_feed proof took effect on the placement date | closing_month_refund | 79.85 | full_no_lapse: whole charge |
| T0 insurer_edi_feed proof took effect on the placement date: basis | closing_month_refund | full_no_lapse | full_no_lapse |
| T0 only an upload taking effect after the closed date counts | closing_month_refund | 0.0 | pro_rata_from_closure: post-closing days only (CM: none) |
| T0 only an upload taking effect after the closed date: basis | closing_month_refund | pro_rata_from_closure | pro_rata_from_closure |
| T0 plan A | closing_month_refund | 77.27 | plan allowance grace_plan_ab |
| T0 plan D | closing_month_refund | 74.7 | plan allowance grace_plan_cd |
| T0 plan E | closing_month_refund | 72.12 | plan allowance 0 (fall-through) |
| T0 contract state LA | closing_month_refund | 77.27 | state allowance grace_gulf |
| T0 contract state AR | closing_month_refund | 74.7 | state allowance grace_plains |
| T0 contract state NM | closing_month_refund | 72.12 | state allowance 0 (fall-through) |
| T0 model year 2016 | closing_month_refund | 79.85 | model-year allowance grace_year_old |
| T0 model year 2020 | closing_month_refund | 77.27 | model-year allowance grace_year_mid |
| T0 model year 2023 | closing_month_refund | 74.7 | model-year allowance 0 (fall-through) |
| T0 after re-reviews: every factor at its standard | closing_month_refund | 48.94 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T0 after re-reviews: only cm_cover_rule at its standard | closing_month_refund | 61.82 | moves the result on its own |
| T0 after re-reviews: only cm_plan_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_state_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_year_grace at its standard | closing_month_refund | 74.7 | moves the result on its own |
| T0 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T0 extra accepted agent-call proof covering the period | closing_month_refund | 77.27 | not read (named channels only): as after re-reviews |
| T0 extra accepted proof of the other insurer channel | closing_month_refund | 77.27 | not read: as after re-reviews |
| T0 the accepted upload is a long declarations page | closing_month_refund | 79.85 | read like any accepted upload: span to the closed date |
| T1 after re-reviews | closing_period_refund | 99.76 | pro rata; union + gap allowances |
| T1 after re-reviews: basis | closing_period_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T1 only the uploaded binder reaches (expires inside the period) | closing_period_refund | 27.52 | one proof expiring inside: its span only |
| T1 only the insurer_fax proof, running past the period | closing_period_refund | 72.24 | fall-through: latest effective through closed date |
| T1 binder entry reinstates the policy on file without a gap | closing_period_refund | 103.2 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T1 insurer_fax proof took effect on the placement date | closing_period_refund | 103.2 | full_no_lapse: whole charge |
| T1 insurer_fax proof took effect on the placement date: basis | closing_period_refund | full_no_lapse | full_no_lapse |
| T1 only an upload taking effect after the closed date counts | closing_period_refund | 10.32 | pro_rata_from_closure: post-closing days only (CM: none) |
| T1 only an upload taking effect after the closed date: basis | closing_period_refund | pro_rata_from_closure | pro_rata_from_closure |
| T1 plan A | closing_period_refund | 103.2 | plan allowance grace_plan_ab |
| T1 plan D | closing_period_refund | 99.76 | plan allowance grace_plan_cd |
| T1 plan E | closing_period_refund | 96.32 | plan allowance 0 (fall-through) |
| T1 contract state LA | closing_period_refund | 103.2 | state allowance grace_gulf |
| T1 contract state AR | closing_period_refund | 99.76 | state allowance grace_plains |
| T1 contract state NM | closing_period_refund | 96.32 | state allowance 0 (fall-through) |
| T1 model year 2016 | closing_period_refund | 103.2 | model-year allowance grace_year_old |
| T1 model year 2020 | closing_period_refund | 99.76 | model-year allowance grace_year_mid |
| T1 model year 2023 | closing_period_refund | 96.32 | model-year allowance 0 (fall-through) |
| T1 after re-reviews: every factor at its standard | closing_period_refund | 72.24 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T1 after re-reviews: only cp_cover_rule at its standard | closing_period_refund | 82.56 | moves the result on its own |
| T1 after re-reviews: only cp_plan_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_state_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_year_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T1 extra accepted agent-call proof covering the period | closing_period_refund | 99.76 | not read (named channels only): as after re-reviews |
| T1 extra accepted proof of the other insurer channel | closing_period_refund | 99.76 | not read: as after re-reviews |
| T1 the accepted upload is a long declarations page | closing_period_refund | 103.2 | read like any accepted upload: span to the closed date |

## Round 7 design (render_source r1: R1-R7 + trigger note)
- R1: replacement gap is a plain binding stated in the standard method; the first grace allowance is keyed on the
  contract's vehicle book value (CFIELD) instead of the CPI plan (same bands, same values in both worlds), so its
  factor owns only its key and value.
- R2: span day counts and overlap move into the coverage-counting factor's bindings.
- R3: standard covered-days sentence no longer defers to the retired base clause.
- R4: re-review overwrite states the outcome on every record: an accepted re-review is recorded as an entry only
  (no status change, no policy-detail update, no cancellation, no notice), matching the tools; the base status-return
  clause is retired for re-reviews and restated in the outside-this-rule tail for first reviews.
- R5 (+ class): the upload rule names no sibling factor quantity (loan-to-value allowance, expiry buffer).
- R6: the outside-this-rule tail restates binder_accepted.
- R7: charge picked by the latest billing_period_start (stated).
- Note: closing-period refund trigger set to on_request (the tool is the borrower's own request).

## Round 7 probe table (scratch copies of both worlds; check_compute DSL evaluator)
| world / change | rule | result | expected |
| --- | --- | --- | --- |
| T0 as seeded | feed_proof_rereview | accepted | accepted |
| T0 record open, contract not repossessed | feed_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T0 record open, contract repossessed on the first-review date | feed_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T0 model year 2022 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | feed_proof_rereview | not_applicable | not_applicable |
| T0 LTV 125 percent (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T0 contract state MS (fall-through) | feed_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T0 sibling state of the same buffer tier | feed_proof_rereview | accepted | as seeded |
| T0 as seeded | upload_proof_rereview | accepted | accepted |
| T0 record open, contract not repossessed | upload_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T0 record open, contract repossessed on the first-review date | upload_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T0 model year 2022 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | upload_proof_rereview | not_applicable | not_applicable |
| T0 later upload is a 6-month declarations page | upload_proof_rereview | not_applicable | most recent upload not a binder -> not_applicable (R3-D1) |
| T0 the upload shows 38 days | upload_proof_rereview | not_applicable | not a binder -> not_applicable |
| T1 as seeded | fax_proof_rereview | accepted | accepted |
| T1 record open, contract not repossessed | fax_proof_rereview | rejected_expiring | reach date = re-review date -> rejected_expiring |
| T1 record open, contract repossessed on the first-review date | fax_proof_rereview | accepted | reach date = repossession date -> as seeded |
| T1 model year 2022 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T1 book value 19000 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T1 Tier 6 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T1 first rejection not re-reviewed | fax_proof_rereview | not_applicable | not_applicable |
| T1 LTV 125 percent (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T1 contract state MS (fall-through) | fax_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T1 sibling state of the same buffer tier | fax_proof_rereview | accepted | as seeded |
| T0 after re-reviews | closing_month_refund | 77.27 | pro rata; union + gap allowances |
| T0 after re-reviews: basis | closing_month_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T0 only the uploaded binder reaches (expires inside the period) | closing_month_refund | 15.45 | one proof expiring inside: its span only |
| T0 only the insurer_edi_feed proof, running past the period | closing_month_refund | 48.94 | fall-through: latest effective through closed date |
| T0 binder entry reinstates the policy on file without a gap | closing_month_refund | 79.85 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T0 insurer_edi_feed proof took effect on the placement date | closing_month_refund | 79.85 | full_no_lapse: whole charge |
| T0 insurer_edi_feed proof took effect on the placement date: basis | closing_month_refund | full_no_lapse | full_no_lapse |
| T0 only an upload taking effect after the closed date counts | closing_month_refund | 0.0 | pro_rata_from_closure: post-closing days only (CM: none) |
| T0 only an upload taking effect after the closed date: basis | closing_month_refund | pro_rata_from_closure | pro_rata_from_closure |
| T0 contract book value 9000.0 | closing_month_refund | 77.27 | value allowance grace_value_low |
| T0 contract book value 16000.0 | closing_month_refund | 74.7 | value allowance grace_value_mid |
| T0 contract book value 21000.0 | closing_month_refund | 72.12 | value allowance 0 (fall-through) |
| T0 record open (out of scope): no failing read | closing_month_refund | 77.27 | a figure, no crash |
| T0 contract state LA | closing_month_refund | 77.27 | state allowance grace_gulf |
| T0 contract state AR | closing_month_refund | 74.7 | state allowance grace_plains |
| T0 contract state NM | closing_month_refund | 72.12 | state allowance 0 (fall-through) |
| T0 model year 2016 | closing_month_refund | 79.85 | model-year allowance grace_year_old |
| T0 model year 2020 | closing_month_refund | 77.27 | model-year allowance grace_year_mid |
| T0 model year 2023 | closing_month_refund | 74.7 | model-year allowance 0 (fall-through) |
| T0 after re-reviews: every factor at its standard | closing_month_refund | 48.94 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T0 after re-reviews: only cm_cover_rule at its standard | closing_month_refund | 61.82 | moves the result on its own |
| T0 after re-reviews: only cm_value_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_state_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_year_grace at its standard | closing_month_refund | 74.7 | moves the result on its own |
| T0 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T0 extra accepted agent-call proof covering the period | closing_month_refund | 77.27 | not read (named channels only): as after re-reviews |
| T0 extra accepted proof of the other insurer channel | closing_month_refund | 77.27 | not read: as after re-reviews |
| T0 the accepted upload is a long declarations page | closing_month_refund | 79.85 | read like any accepted upload: span to the closed date |
| T1 after re-reviews | closing_period_refund | 99.76 | pro rata; union + gap allowances |
| T1 after re-reviews: basis | closing_period_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T1 only the uploaded binder reaches (expires inside the period) | closing_period_refund | 27.52 | one proof expiring inside: its span only |
| T1 only the insurer_fax proof, running past the period | closing_period_refund | 72.24 | fall-through: latest effective through closed date |
| T1 binder entry reinstates the policy on file without a gap | closing_period_refund | 103.2 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T1 insurer_fax proof took effect on the placement date | closing_period_refund | 103.2 | full_no_lapse: whole charge |
| T1 insurer_fax proof took effect on the placement date: basis | closing_period_refund | full_no_lapse | full_no_lapse |
| T1 only an upload taking effect after the closed date counts | closing_period_refund | 10.32 | pro_rata_from_closure: post-closing days only (CM: none) |
| T1 only an upload taking effect after the closed date: basis | closing_period_refund | pro_rata_from_closure | pro_rata_from_closure |
| T1 contract book value 9000.0 | closing_period_refund | 103.2 | value allowance grace_value_low |
| T1 contract book value 16000.0 | closing_period_refund | 99.76 | value allowance grace_value_mid |
| T1 contract book value 21000.0 | closing_period_refund | 96.32 | value allowance 0 (fall-through) |
| T1 record open (out of scope): no failing read | closing_period_refund | 99.76 | a figure, no crash |
| T1 contract state LA | closing_period_refund | 103.2 | state allowance grace_gulf |
| T1 contract state AR | closing_period_refund | 99.76 | state allowance grace_plains |
| T1 contract state NM | closing_period_refund | 96.32 | state allowance 0 (fall-through) |
| T1 model year 2016 | closing_period_refund | 103.2 | model-year allowance grace_year_old |
| T1 model year 2020 | closing_period_refund | 99.76 | model-year allowance grace_year_mid |
| T1 model year 2023 | closing_period_refund | 96.32 | model-year allowance 0 (fall-through) |
| T1 after re-reviews: every factor at its standard | closing_period_refund | 72.24 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T1 after re-reviews: only cp_cover_rule at its standard | closing_period_refund | 82.56 | moves the result on its own |
| T1 after re-reviews: only cp_value_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_state_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_year_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T1 extra accepted agent-call proof covering the period | closing_period_refund | 99.76 | not read (named channels only): as after re-reviews |
| T1 extra accepted proof of the other insurer channel | closing_period_refund | 99.76 | not read: as after re-reviews |
| T1 the accepted upload is a long declarations page | closing_period_refund | 103.2 | read like any accepted upload: span to the closed date |

## Round 8 design (audit r6: R6-A, R6-B, R6-C; coordinator route)
- R6-A: the three re-review rules (and their overwrites) govern closed tracking records only; on a record that is not
  closed the base proof-review rule and lifecycle stay in force (compute returns not_applicable there). Reach-date
  ladder re-keyed on closed-record cases: contract paid off -> first-review date; contract not paid off but
  repossessed -> repossession date; otherwise the re-review date (standard). The status-return retirement is dropped.
- R6-B: one shared hand-off sentence in both refund rules: the latest charge of a payoff-closed record goes to the
  closing-month / closing-period rule only when an accepted proof counts for its period; that charge without one,
  and every other charge, keep the base refund rule, the closure basis restated in force.
- R6-C: refunds read accepted proofs of every arrival channel alike: for each channel the accepted proof with the
  latest effective date (a later accepted proof from a source supersedes an earlier one from that source); covered
  days are the union of the reaching spans (inclusion-exclusion over the four channels), the replacement days are
  the uncovered days between the first and last reaching span. The channel decides only which re-review rule
  reviewed the proof. Figures unchanged on both worlds.

## Round 8 probe table (scratch copies of both worlds; check_compute DSL evaluator)
| world / change | rule | result | expected |
| --- | --- | --- | --- |
| T0 as seeded | feed_proof_rereview | accepted | accepted |
| T0 record open (not closed) | feed_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T0 closed record, contract liquidated after a repossession on the first-review date | feed_proof_rereview | accepted | reach date = repossession date -> accepted |
| T0 closed record, contract charged off, never repossessed | feed_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T0 model year 2022 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | feed_proof_rereview | not_applicable | not_applicable |
| T0 LTV 125 percent (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T0 contract state MS (fall-through) | feed_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T0 sibling state of the same buffer tier | feed_proof_rereview | accepted | as seeded |
| T0 as seeded | upload_proof_rereview | accepted | accepted |
| T0 record open (not closed) | upload_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T0 closed record, contract liquidated after a repossession on the first-review date | upload_proof_rereview | accepted | reach date = repossession date -> accepted |
| T0 closed record, contract charged off, never repossessed | upload_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T0 model year 2022 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | upload_proof_rereview | not_applicable | not_applicable |
| T0 later upload is a 6-month declarations page | upload_proof_rereview | not_applicable | most recent upload not a binder -> not_applicable (R3-D1) |
| T0 the upload shows 38 days | upload_proof_rereview | not_applicable | not a binder -> not_applicable |
| T1 as seeded | fax_proof_rereview | accepted | accepted |
| T1 record open (not closed) | fax_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T1 closed record, contract liquidated after a repossession on the first-review date | fax_proof_rereview | accepted | reach date = repossession date -> accepted |
| T1 closed record, contract charged off, never repossessed | fax_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T1 model year 2022 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T1 book value 19000 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T1 Tier 6 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T1 first rejection not re-reviewed | fax_proof_rereview | not_applicable | not_applicable |
| T1 LTV 125 percent (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T1 contract state MS (fall-through) | fax_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T1 sibling state of the same buffer tier | fax_proof_rereview | accepted | as seeded |
| T0 after re-reviews | closing_month_refund | 77.27 | pro rata; union + gap allowances |
| T0 after re-reviews: basis | closing_month_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T0 only the uploaded binder reaches (expires inside the period) | closing_month_refund | 15.45 | one proof expiring inside: its span only |
| T0 only the insurer_edi_feed proof, running past the period | closing_month_refund | 48.94 | fall-through: latest effective through closed date |
| T0 binder entry reinstates the policy on file without a gap | closing_month_refund | 79.85 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T0 insurer_edi_feed proof took effect on the placement date | closing_month_refund | 79.85 | full_no_lapse: whole charge |
| T0 insurer_edi_feed proof took effect on the placement date: basis | closing_month_refund | full_no_lapse | full_no_lapse |
| T0 only an upload taking effect after the closed date counts | closing_month_refund | 0.0 | pro_rata_from_closure: post-closing days only (CM: none) |
| T0 only an upload taking effect after the closed date: basis | closing_month_refund | pro_rata_from_closure | pro_rata_from_closure |
| T0 contract book value 9000.0 | closing_month_refund | 77.27 | value allowance grace_value_low |
| T0 contract book value 16000.0 | closing_month_refund | 74.7 | value allowance grace_value_mid |
| T0 contract book value 21000.0 | closing_month_refund | 72.12 | value allowance 0 (fall-through) |
| T0 record open (out of scope): no failing read | closing_month_refund | 77.27 | a figure, no crash |
| T0 contract state LA | closing_month_refund | 77.27 | state allowance grace_gulf |
| T0 contract state AR | closing_month_refund | 74.7 | state allowance grace_plains |
| T0 contract state NM | closing_month_refund | 72.12 | state allowance 0 (fall-through) |
| T0 model year 2016 | closing_month_refund | 79.85 | model-year allowance grace_year_old |
| T0 model year 2020 | closing_month_refund | 77.27 | model-year allowance grace_year_mid |
| T0 model year 2023 | closing_month_refund | 74.7 | model-year allowance 0 (fall-through) |
| T0 after re-reviews: every factor at its standard | closing_month_refund | 48.94 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T0 after re-reviews: only cm_cover_rule at its standard | closing_month_refund | 61.82 | moves the result on its own |
| T0 after re-reviews: only cm_value_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_state_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_year_grace at its standard | closing_month_refund | 74.7 | moves the result on its own |
| T0 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T0 extra accepted agent-call proof covering the period | closing_month_refund | 79.85 | read like any channel: covers the whole period -> full charge |
| T0 extra accepted proof of the other insurer channel | closing_month_refund | 79.85 | read like any channel: covers the whole period -> full charge |
| T0 the accepted policy arrived by insurer_fax instead (R6-C) | closing_month_refund | 77.27 | channel-blind: as after re-reviews |
| T0 the accepted policy arrived by insurance_agent_call instead (R6-C) | closing_month_refund | 77.27 | channel-blind: as after re-reviews |
| T0 no accepted proof counts (R6-B: outside the rule, base closure restated in the tail) | closing_month_refund | 0.0 | compute gives the closure days; the base rule governs |
| T0 the accepted upload is a long declarations page | closing_month_refund | 79.85 | read like any accepted upload: span to the closed date |
| T1 after re-reviews | closing_period_refund | 99.76 | pro rata; union + gap allowances |
| T1 after re-reviews: basis | closing_period_refund | pro_rata_from_proof_effective | pro_rata_from_proof_effective |
| T1 only the uploaded binder reaches (expires inside the period) | closing_period_refund | 27.52 | one proof expiring inside: its span only |
| T1 only the insurer_fax proof, running past the period | closing_period_refund | 72.24 | fall-through: latest effective through closed date |
| T1 binder entry reinstates the policy on file without a gap | closing_period_refund | 103.2 | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T1 insurer_fax proof took effect on the placement date | closing_period_refund | 103.2 | full_no_lapse: whole charge |
| T1 insurer_fax proof took effect on the placement date: basis | closing_period_refund | full_no_lapse | full_no_lapse |
| T1 only an upload taking effect after the closed date counts | closing_period_refund | 10.32 | pro_rata_from_closure: post-closing days only (CM: none) |
| T1 only an upload taking effect after the closed date: basis | closing_period_refund | pro_rata_from_closure | pro_rata_from_closure |
| T1 contract book value 9000.0 | closing_period_refund | 103.2 | value allowance grace_value_low |
| T1 contract book value 16000.0 | closing_period_refund | 99.76 | value allowance grace_value_mid |
| T1 contract book value 21000.0 | closing_period_refund | 96.32 | value allowance 0 (fall-through) |
| T1 record open (out of scope): no failing read | closing_period_refund | 99.76 | a figure, no crash |
| T1 contract state LA | closing_period_refund | 103.2 | state allowance grace_gulf |
| T1 contract state AR | closing_period_refund | 99.76 | state allowance grace_plains |
| T1 contract state NM | closing_period_refund | 96.32 | state allowance 0 (fall-through) |
| T1 model year 2016 | closing_period_refund | 103.2 | model-year allowance grace_year_old |
| T1 model year 2020 | closing_period_refund | 99.76 | model-year allowance grace_year_mid |
| T1 model year 2023 | closing_period_refund | 96.32 | model-year allowance 0 (fall-through) |
| T1 after re-reviews: every factor at its standard | closing_period_refund | 72.24 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T1 after re-reviews: only cp_cover_rule at its standard | closing_period_refund | 82.56 | moves the result on its own |
| T1 after re-reviews: only cp_value_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_state_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_year_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T1 extra accepted agent-call proof covering the period | closing_period_refund | 103.2 | read like any channel: covers the whole period -> full charge |
| T1 extra accepted proof of the other insurer channel | closing_period_refund | 103.2 | read like any channel: covers the whole period -> full charge |
| T1 the accepted policy arrived by insurer_edi_feed instead (R6-C) | closing_period_refund | 99.76 | channel-blind: as after re-reviews |
| T1 the accepted policy arrived by insurance_agent_call instead (R6-C) | closing_period_refund | 99.76 | channel-blind: as after re-reviews |
| T1 no accepted proof counts (R6-B: outside the rule, base closure restated in the tail) | closing_period_refund | 10.32 | compute gives the closure days; the base rule governs |
| T1 the accepted upload is a long declarations page | closing_period_refund | 103.2 | read like any accepted upload: span to the closed date |

## Round 9 design (audit r7: R7-A; coordinator route)
- Both refunds are scoped, through their self-naming hand-off, to records on which no arrival channel holds more
  than one accepted proof (exact per-channel COUNT of accepted cpi_proof_verified entries, a record test); on any
  other record the latest charge stays under the base refund rule, restated in the tail and computed as base (the
  proof read is the accepted proof with the latest policy_effective_date).
- T0's original 2025 proof is re-seeded as an insurance agent call (it was verified by the borrower's agent by phone
  at funding), so after the re-reviews each channel holds one accepted proof; T1 already does. Figures unchanged.

## Round 9 probe table (scratch copies of both worlds; check_compute DSL evaluator; [scope] = extended rule or base)
| world / change | rule | result | expected |
| --- | --- | --- | --- |
| T0 as seeded | feed_proof_rereview | accepted | accepted |
| T0 record open (not closed) | feed_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T0 closed record, contract liquidated after a repossession on the first-review date | feed_proof_rereview | accepted | reach date = repossession date -> accepted |
| T0 closed record, contract charged off, never repossessed | feed_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T0 model year 2022 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | feed_proof_rereview | not_applicable | not_applicable |
| T0 LTV 125 percent (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T0 contract state MS (fall-through) | feed_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T0 sibling state of the same buffer tier | feed_proof_rereview | accepted | as seeded |
| T0 as seeded | upload_proof_rereview | accepted | accepted |
| T0 record open (not closed) | upload_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T0 closed record, contract liquidated after a repossession on the first-review date | upload_proof_rereview | accepted | reach date = repossession date -> accepted |
| T0 closed record, contract charged off, never repossessed | upload_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T0 model year 2022 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | upload_proof_rereview | not_applicable | not_applicable |
| T0 later upload is a 6-month declarations page | upload_proof_rereview | not_applicable | most recent upload not a binder -> not_applicable (R3-D1) |
| T0 the upload shows 38 days | upload_proof_rereview | not_applicable | not a binder -> not_applicable |
| T1 as seeded | fax_proof_rereview | accepted | accepted |
| T1 record open (not closed) | fax_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T1 closed record, contract liquidated after a repossession on the first-review date | fax_proof_rereview | accepted | reach date = repossession date -> accepted |
| T1 closed record, contract charged off, never repossessed | fax_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T1 model year 2022 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T1 book value 19000 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T1 Tier 6 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T1 first rejection not re-reviewed | fax_proof_rereview | not_applicable | not_applicable |
| T1 LTV 125 percent (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T1 contract state MS (fall-through) | fax_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T1 sibling state of the same buffer tier | fax_proof_rereview | accepted | as seeded |
| T0 after re-reviews | closing_month_refund | 77.27 [extended] | pro rata; union + gap allowances |
| T0 after re-reviews: basis | closing_month_refund | pro_rata_from_proof_effective [extended] | pro_rata_from_proof_effective |
| T0 only the uploaded binder reaches (expires inside the period) | closing_month_refund | 15.45 [extended] | one proof expiring inside: its span only |
| T0 only the insurer_edi_feed proof, running past the period | closing_month_refund | 48.94 [extended] | fall-through: latest effective through closed date |
| T0 binder entry reinstates the policy on file without a gap | closing_month_refund | 79.85 [extended] | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T0 insurer_edi_feed proof took effect on the placement date | closing_month_refund | 79.85 [extended] | full_no_lapse: whole charge |
| T0 insurer_edi_feed proof took effect on the placement date: basis | closing_month_refund | full_no_lapse [extended] | full_no_lapse |
| T0 only an upload taking effect after the closed date counts | closing_month_refund | 0.0 [extended] | pro_rata_from_closure: post-closing days only (CM: none) |
| T0 only an upload taking effect after the closed date: basis | closing_month_refund | pro_rata_from_closure [extended] | pro_rata_from_closure |
| T0 contract book value 9000.0 | closing_month_refund | 77.27 [extended] | value allowance grace_value_low |
| T0 contract book value 16000.0 | closing_month_refund | 74.7 [extended] | value allowance grace_value_mid |
| T0 contract book value 21000.0 | closing_month_refund | 72.12 [extended] | value allowance 0 (fall-through) |
| T0 record open (out of scope): no failing read | closing_month_refund | 77.27 [extended] | a figure, no crash |
| T0 contract state LA | closing_month_refund | 77.27 [extended] | state allowance grace_gulf |
| T0 contract state AR | closing_month_refund | 74.7 [extended] | state allowance grace_plains |
| T0 contract state NM | closing_month_refund | 72.12 [extended] | state allowance 0 (fall-through) |
| T0 model year 2016 | closing_month_refund | 79.85 [extended] | model-year allowance grace_year_old |
| T0 model year 2020 | closing_month_refund | 77.27 [extended] | model-year allowance grace_year_mid |
| T0 model year 2023 | closing_month_refund | 74.7 [extended] | model-year allowance 0 (fall-through) |
| T0 after re-reviews: every factor at its standard | closing_month_refund | 48.94 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T0 after re-reviews: only cm_cover_rule at its standard | closing_month_refund | 61.82 | moves the result on its own |
| T0 after re-reviews: only cm_value_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_state_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_year_grace at its standard | closing_month_refund | 74.7 | moves the result on its own |
| T0 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T0 extra accepted agent-call proof covering the period | closing_month_refund | 48.94 [base (a channel holds two accepted proofs)] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T0 extra accepted proof of the other insurer channel | closing_month_refund | 79.85 [extended] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T0 binder and policy both accepted through the upload channel (R7-A) | closing_month_refund | 48.94 [base (a channel holds two accepted proofs)] | outside the extended scope: base refund from the latest accepted effective date |
| T0 the accepted policy arrived by insurer_fax instead (R6-C) | closing_month_refund | 77.27 [extended] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T0 the accepted policy arrived by insurance_agent_call instead (R6-C) | closing_month_refund | 48.94 [base (a channel holds two accepted proofs)] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T0 no accepted proof counts (R6-B: outside the rule, base closure restated in the tail) | closing_month_refund | 0.0 [extended] | compute gives the closure days; the base rule governs |
| T0 the accepted upload is a long declarations page | closing_month_refund | 79.85 [extended] | read like any accepted upload: span to the closed date |
| T1 after re-reviews | closing_period_refund | 99.76 [extended] | pro rata; union + gap allowances |
| T1 after re-reviews: basis | closing_period_refund | pro_rata_from_proof_effective [extended] | pro_rata_from_proof_effective |
| T1 only the uploaded binder reaches (expires inside the period) | closing_period_refund | 27.52 [extended] | one proof expiring inside: its span only |
| T1 only the insurer_fax proof, running past the period | closing_period_refund | 72.24 [extended] | fall-through: latest effective through closed date |
| T1 binder entry reinstates the policy on file without a gap | closing_period_refund | 103.2 [extended] | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T1 insurer_fax proof took effect on the placement date | closing_period_refund | 103.2 [extended] | full_no_lapse: whole charge |
| T1 insurer_fax proof took effect on the placement date: basis | closing_period_refund | full_no_lapse [extended] | full_no_lapse |
| T1 only an upload taking effect after the closed date counts | closing_period_refund | 10.32 [extended] | pro_rata_from_closure: post-closing days only (CM: none) |
| T1 only an upload taking effect after the closed date: basis | closing_period_refund | pro_rata_from_closure [extended] | pro_rata_from_closure |
| T1 contract book value 9000.0 | closing_period_refund | 103.2 [extended] | value allowance grace_value_low |
| T1 contract book value 16000.0 | closing_period_refund | 99.76 [extended] | value allowance grace_value_mid |
| T1 contract book value 21000.0 | closing_period_refund | 96.32 [extended] | value allowance 0 (fall-through) |
| T1 record open (out of scope): no failing read | closing_period_refund | 99.76 [extended] | a figure, no crash |
| T1 contract state LA | closing_period_refund | 103.2 [extended] | state allowance grace_gulf |
| T1 contract state AR | closing_period_refund | 99.76 [extended] | state allowance grace_plains |
| T1 contract state NM | closing_period_refund | 96.32 [extended] | state allowance 0 (fall-through) |
| T1 model year 2016 | closing_period_refund | 103.2 [extended] | model-year allowance grace_year_old |
| T1 model year 2020 | closing_period_refund | 99.76 [extended] | model-year allowance grace_year_mid |
| T1 model year 2023 | closing_period_refund | 96.32 [extended] | model-year allowance 0 (fall-through) |
| T1 after re-reviews: every factor at its standard | closing_period_refund | 72.24 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T1 after re-reviews: only cp_cover_rule at its standard | closing_period_refund | 82.56 | moves the result on its own |
| T1 after re-reviews: only cp_value_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_state_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_year_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T1 extra accepted agent-call proof covering the period | closing_period_refund | 103.2 [extended] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T1 extra accepted proof of the other insurer channel | closing_period_refund | 72.24 [base (a channel holds two accepted proofs)] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T1 binder and policy both accepted through the upload channel (R7-A) | closing_period_refund | 72.24 [base (a channel holds two accepted proofs)] | outside the extended scope: base refund from the latest accepted effective date |
| T1 the accepted policy arrived by insurer_edi_feed instead (R6-C) | closing_period_refund | 72.24 [base (a channel holds two accepted proofs)] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T1 the accepted policy arrived by insurance_agent_call instead (R6-C) | closing_period_refund | 99.76 [extended] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T1 no accepted proof counts (R6-B: outside the rule, base closure restated in the tail) | closing_period_refund | 10.32 [extended] | compute gives the closure days; the base rule governs |
| T1 the accepted upload is a long declarations page | closing_period_refund | 103.2 [extended] | read like any accepted upload: span to the closed date |

## Round 10 design (audit r8: R8-A, R8-B; coordinator ruling)
- R8-B: the scope test is stated as a plain record test with no purpose clause: the rule applies only on a tracking
  record on which no verification_source holds more than one accepted cpi_proof_verified entry.
- R8-A: the tail restates the base refund clauses verbatim (refunded only once, full_no_lapse, proof clause,
  closure clause) plus one stated reading (the proof read is the accepted proof with the latest effective date; its
  coverage has no gap when it took effect by the placement date and expires on or after it; when the proof and
  closure clauses both apply the charge is refunded once for every day either gives). The out-of-scope compute is
  that reading exactly, and it is used whenever the hand-off condition fails (record test fails or no accepted
  proof counts). Checked against an independent reading of the text on both worlds (Round 10 probe tables).

## Round 10 probe table A (rule probes; [scope] = extended rule or base)
| world / change | rule | result | expected |
| --- | --- | --- | --- |
| T0 as seeded | feed_proof_rereview | accepted | accepted |
| T0 record open (not closed) | feed_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T0 closed record, contract liquidated after a repossession on the first-review date | feed_proof_rereview | accepted | reach date = repossession date -> accepted |
| T0 closed record, contract charged off, never repossessed | feed_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T0 model year 2022 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | feed_proof_rereview | not_applicable | not_applicable |
| T0 LTV 125 percent (fall-through) | feed_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T0 contract state MS (fall-through) | feed_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T0 sibling state of the same buffer tier | feed_proof_rereview | accepted | as seeded |
| T0 as seeded | upload_proof_rereview | accepted | accepted |
| T0 record open (not closed) | upload_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T0 closed record, contract liquidated after a repossession on the first-review date | upload_proof_rereview | accepted | reach date = repossession date -> accepted |
| T0 closed record, contract charged off, never repossessed | upload_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T0 model year 2022 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T0 book value 19000 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T0 Tier 6 (fall-through) | upload_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T0 first rejection not re-reviewed | upload_proof_rereview | not_applicable | not_applicable |
| T0 later upload is a 6-month declarations page | upload_proof_rereview | not_applicable | most recent upload not a binder -> not_applicable (R3-D1) |
| T0 the upload shows 38 days | upload_proof_rereview | not_applicable | not a binder -> not_applicable |
| T1 as seeded | fax_proof_rereview | accepted | accepted |
| T1 record open (not closed) | fax_proof_rereview | not_applicable | outside the rule (base review governs) -> not_applicable |
| T1 closed record, contract liquidated after a repossession on the first-review date | fax_proof_rereview | accepted | reach date = repossession date -> accepted |
| T1 closed record, contract charged off, never repossessed | fax_proof_rereview | rejected_expiring | reach date = re-review date (fall-through) -> rejected_expiring |
| T1 model year 2022 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no model-year allowance -> rejected_deductible_too_high |
| T1 book value 19000 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no vehicle-value allowance -> rejected_deductible_too_high |
| T1 Tier 6 (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no credit-tier allowance -> rejected_deductible_too_high |
| T1 first rejection not re-reviewed | fax_proof_rereview | not_applicable | not_applicable |
| T1 LTV 125 percent (fall-through) | fax_proof_rereview | rejected_deductible_too_high | no loan-to-value allowance -> rejected_deductible_too_high |
| T1 contract state MS (fall-through) | fax_proof_rereview | rejected_expiring | buffer 15 days -> rejected_expiring |
| T1 sibling state of the same buffer tier | fax_proof_rereview | accepted | as seeded |
| T0 after re-reviews | closing_month_refund | 77.27 [extended] | pro rata; union + gap allowances |
| T0 after re-reviews: basis | closing_month_refund | pro_rata_from_proof_effective [extended] | pro_rata_from_proof_effective |
| T0 only the uploaded binder reaches (expires inside the period) | closing_month_refund | 15.45 [extended] | one proof expiring inside: its span only |
| T0 only the insurer_edi_feed proof, running past the period | closing_month_refund | 48.94 [extended] | fall-through: latest effective through closed date |
| T0 binder entry reinstates the policy on file without a gap | closing_month_refund | 79.85 [extended] | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T0 insurer_edi_feed proof took effect on the placement date | closing_month_refund | 79.85 [extended] | full_no_lapse: whole charge |
| T0 insurer_edi_feed proof took effect on the placement date: basis | closing_month_refund | full_no_lapse [extended] | full_no_lapse |
| T0 only an upload taking effect after the closed date counts | closing_month_refund | 0.0 [extended] | pro_rata_from_closure: post-closing days only (CM: none) |
| T0 only an upload taking effect after the closed date: basis | closing_month_refund | pro_rata_from_closure [extended] | pro_rata_from_closure |
| T0 contract book value 9000.0 | closing_month_refund | 77.27 [extended] | value allowance grace_value_low |
| T0 contract book value 16000.0 | closing_month_refund | 74.7 [extended] | value allowance grace_value_mid |
| T0 contract book value 21000.0 | closing_month_refund | 72.12 [extended] | value allowance 0 (fall-through) |
| T0 record open (out of scope): no failing read | closing_month_refund | 77.27 [extended] | a figure, no crash |
| T0 contract state LA | closing_month_refund | 77.27 [extended] | state allowance grace_gulf |
| T0 contract state AR | closing_month_refund | 74.7 [extended] | state allowance grace_plains |
| T0 contract state NM | closing_month_refund | 72.12 [extended] | state allowance 0 (fall-through) |
| T0 model year 2016 | closing_month_refund | 79.85 [extended] | model-year allowance grace_year_old |
| T0 model year 2020 | closing_month_refund | 77.27 [extended] | model-year allowance grace_year_mid |
| T0 model year 2023 | closing_month_refund | 74.7 [extended] | model-year allowance 0 (fall-through) |
| T0 after re-reviews: every factor at its standard | closing_month_refund | 48.94 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T0 after re-reviews: only cm_cover_rule at its standard | closing_month_refund | 61.82 | moves the result on its own |
| T0 after re-reviews: only cm_value_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_state_grace at its standard | closing_month_refund | 72.12 | moves the result on its own |
| T0 after re-reviews: only cm_year_grace at its standard | closing_month_refund | 74.7 | moves the result on its own |
| T0 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T0 extra accepted agent-call proof covering the period | closing_month_refund | 48.94 [base (outside the record test or no counting proof)] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T0 extra accepted proof of the other insurer channel | closing_month_refund | 79.85 [extended] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T0 binder and policy both accepted through the upload channel (R7-A) | closing_month_refund | 48.94 [base (outside the record test or no counting proof)] | outside the extended scope: base refund from the latest accepted effective date |
| T0 the accepted policy arrived by insurer_fax instead (R6-C) | closing_month_refund | 77.27 [extended] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T0 the accepted policy arrived by insurance_agent_call instead (R6-C) | closing_month_refund | 48.94 [base (outside the record test or no counting proof)] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T0 no accepted proof counts (R6-B: outside the rule, base closure restated in the tail) | closing_month_refund | 0.0 [base (outside the record test or no counting proof)] | compute gives the closure days; the base rule governs |
| T0 the accepted upload is a long declarations page | closing_month_refund | 79.85 [extended] | read like any accepted upload: span to the closed date |
| T1 after re-reviews | closing_period_refund | 99.76 [extended] | pro rata; union + gap allowances |
| T1 after re-reviews: basis | closing_period_refund | pro_rata_from_proof_effective [extended] | pro_rata_from_proof_effective |
| T1 only the uploaded binder reaches (expires inside the period) | closing_period_refund | 27.52 [extended] | one proof expiring inside: its span only |
| T1 only the insurer_fax proof, running past the period | closing_period_refund | 72.24 [extended] | fall-through: latest effective through closed date |
| T1 binder entry reinstates the policy on file without a gap | closing_period_refund | 103.2 [extended] | full_no_lapse (the reinstatement took effect before the placement date): whole charge |
| T1 insurer_fax proof took effect on the placement date | closing_period_refund | 103.2 [extended] | full_no_lapse: whole charge |
| T1 insurer_fax proof took effect on the placement date: basis | closing_period_refund | full_no_lapse [extended] | full_no_lapse |
| T1 only an upload taking effect after the closed date counts | closing_period_refund | 10.32 [extended] | pro_rata_from_closure: post-closing days only (CM: none) |
| T1 only an upload taking effect after the closed date: basis | closing_period_refund | pro_rata_from_closure [extended] | pro_rata_from_closure |
| T1 contract book value 9000.0 | closing_period_refund | 103.2 [extended] | value allowance grace_value_low |
| T1 contract book value 16000.0 | closing_period_refund | 99.76 [extended] | value allowance grace_value_mid |
| T1 contract book value 21000.0 | closing_period_refund | 96.32 [extended] | value allowance 0 (fall-through) |
| T1 record open (out of scope): no failing read | closing_period_refund | 99.76 [extended] | a figure, no crash |
| T1 contract state LA | closing_period_refund | 103.2 [extended] | state allowance grace_gulf |
| T1 contract state AR | closing_period_refund | 99.76 [extended] | state allowance grace_plains |
| T1 contract state NM | closing_period_refund | 96.32 [extended] | state allowance 0 (fall-through) |
| T1 model year 2016 | closing_period_refund | 103.2 [extended] | model-year allowance grace_year_old |
| T1 model year 2020 | closing_period_refund | 99.76 [extended] | model-year allowance grace_year_mid |
| T1 model year 2023 | closing_period_refund | 96.32 [extended] | model-year allowance 0 (fall-through) |
| T1 after re-reviews: every factor at its standard | closing_period_refund | 72.24 | base proof basis: latest reaching effective date through the period end, no grace (not 0.00) |
| T1 after re-reviews: only cp_cover_rule at its standard | closing_period_refund | 82.56 | moves the result on its own |
| T1 after re-reviews: only cp_value_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_state_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 after re-reviews: only cp_year_grace at its standard | closing_period_refund | 96.32 | moves the result on its own |
| T1 earlier charges reached by an accepted proof after the re-reviews | base cancellation refund | [] | [] (only the latest charge is refundable) |
| T1 extra accepted agent-call proof covering the period | closing_period_refund | 103.2 [extended] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T1 extra accepted proof of the other insurer channel | closing_period_refund | 72.24 [base (outside the record test or no counting proof)] | read like any channel when it is that channel's only accepted proof (full charge); base when the channel already holds one |
| T1 binder and policy both accepted through the upload channel (R7-A) | closing_period_refund | 72.24 [base (outside the record test or no counting proof)] | outside the extended scope: base refund from the latest accepted effective date |
| T1 the accepted policy arrived by insurer_edi_feed instead (R6-C) | closing_period_refund | 72.24 [base (outside the record test or no counting proof)] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T1 the accepted policy arrived by insurance_agent_call instead (R6-C) | closing_period_refund | 99.76 [extended] | channel-blind: as after re-reviews when the channel holds no other accepted proof; base otherwise |
| T1 no accepted proof counts (R6-B: outside the rule, base closure restated in the tail) | closing_period_refund | 10.32 [base (outside the record test or no counting proof)] | compute gives the closure days; the base rule governs |
| T1 the accepted upload is a long declarations page | closing_period_refund | 103.2 [extended] | read like any accepted upload: span to the closed date |

## Round 10 probe table B (out-of-scope compute vs an independent reading of the restated base text)
| world / case | rule | compute (amount / basis) | text reading | verdict |
| --- | --- | --- | --- | --- |
| T0 two accepted feed proofs, the latest expired before the period (auditor case) | closing_month_refund | 79.85 / pro_rata_from_proof_effective [base] | base text reading 79.85 / pro_rata_from_proof_effective | AGREE |
| T0 two accepted fax proofs, both before the placement with a gap | closing_month_refund | 0.0 / pro_rata_from_closure [base] | base text reading 0.0 / pro_rata_from_closure | AGREE |
| T0 two accepted fax proofs, the latest effective before the placement and running past it | closing_month_refund | 79.85 / full_no_lapse [base] | base text reading 79.85 / full_no_lapse | AGREE |
| T0 a second accepted upload taking effect at or after the closed date | closing_month_refund | 2.58 / pro_rata_from_proof_effective [base] | base text reading 2.58 / pro_rata_from_proof_effective | AGREE |
| T0 binder and policy both accepted through the upload channel | closing_month_refund | 48.94 / pro_rata_from_proof_effective [base] | base text reading 48.94 / pro_rata_from_proof_effective | AGREE |
| T0 no accepted proof at all | closing_month_refund | 0.0 / pro_rata_from_closure [base] | base text reading 0.0 / pro_rata_from_closure | AGREE |
| T0 one accepted proof per channel, none counting (expired before the period) | closing_month_refund | 79.85 / pro_rata_from_proof_effective [base] | base text reading 79.85 / pro_rata_from_proof_effective | AGREE |
| T1 two accepted feed proofs, the latest expired before the period (auditor case) | closing_period_refund | 103.2 / pro_rata_from_proof_effective [base] | base text reading 103.2 / pro_rata_from_proof_effective | AGREE |
| T1 two accepted fax proofs, both before the placement with a gap | closing_period_refund | 10.32 / pro_rata_from_closure [base] | base text reading 10.32 / pro_rata_from_closure | AGREE |
| T1 two accepted fax proofs, the latest effective before the placement and running past it | closing_period_refund | 103.2 / full_no_lapse [base] | base text reading 103.2 / full_no_lapse | AGREE |
| T1 a second accepted upload taking effect at or after the closed date | closing_period_refund | 10.32 / pro_rata_from_proof_effective [base] | base text reading 10.32 / pro_rata_from_proof_effective | AGREE |
| T1 binder and policy both accepted through the upload channel | closing_period_refund | 72.24 / pro_rata_from_proof_effective [base] | base text reading 72.24 / pro_rata_from_proof_effective | AGREE |
| T1 no accepted proof at all | closing_period_refund | 10.32 / pro_rata_from_closure [base] | base text reading 10.32 / pro_rata_from_closure | AGREE |
| T1 one accepted proof per channel, none counting (expired before the period) | closing_period_refund | 103.2 / pro_rata_from_proof_effective [base] | base text reading 103.2 / pro_rata_from_proof_effective | AGREE |

## Round 11 (audit r9: R9-A)
- Tail reading of both refunds now states the tie rule the compute implements: where two accepted proofs share the
  latest policy_effective_date, the one recorded first counts (LATEST keeps the first-recorded row; the effective
  and expiration reads use the same pick). Probe: two accepted feed proofs effective 2026-01-01, one expiring before
  the placement, recorded in either order -> the first-recorded one decides, as stated. No figure change.
- Tie sweep: re-review picks state "by review date (where two entries share that date, the one recorded first
  counts)"; the charge pick sums every capitalised charge of the latest billing period; within the refund scope each
  channel holds at most one accepted proof; the other "latest/earliest" phrases are dates, not record picks.
