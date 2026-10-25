# worklog — sr22_fr44_filings (category fr), M=2

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[6,5] -> fr_ext_refiling_fee 6, fr_ext_lapse_sr26_runoff 5
- task 1: prerequisite_problems=2, factor_counts=[4,6,6]

## Step 0 constraint analysis (why the shapes)
- fr numeric writes: fr_filing_transactions.amount and the SR-26 certificate end date (passed as an
  integer run-off day count, date derived in the tool with a pure ordinal helper). Own-category
  DSL reads are HID-scoped (XSUM/CFIELD on 'fr' rejected by check_extended), so every value_input
  edge writes on the dependent's own HID filing.
- Customer-owned numeric fr writes: only certificate orders (the filed driver orders and accepts the
  fee). Release requests carry no number. Fee reversals are always the fee's full amount (no
  load-bearing factor possible) -> not used.
- Base eligibility evidence contracts read owner AND non-owner fields together (backing_term_open,
  backing_limits, term_coverage_ended, not_before_end, timely) and correlate filer_rated through
  auto_policy_changes.auto_policy_id = action auto_policy_id. Route-arounds: (a) seed the customer's
  real prior owner term (sold car, cancelled at insured request) so owner fields are evidenced;
  (b) scoped overwrites where the base sentence genuinely conflicts with the extended rule
  (lapse reinstatement still gets an SR-26; ending date = lapse_start_date because reinstatement
  clears closed_date; filer of a non-owner refiling is the named insured).

## Task 0 — FL FR-44 Operator, non-owner term cancelled 2026-10-25, reinstated with lapse 2026-10-27
frozen_time 2026-10-28 11:20:00 EDT. Tree: fr_ext_refiling_fee (root, user) <- fr_ext_lapse_sr26_runoff
(agent), value_input on binding `continuity`, state form:
"The refiling fee is fixed only after the replaced certificate carries an SR-26 date and a certificate end date."
Exactly one write in the difficulty gives an Operator certificate on a non-owner term an SR-26 date
(the lapse SR-26; the removal SR-26 is owner-term only).

Capability cards
- transmit_lapse_sr26_2b138773 (agent, write): object = one Operator certificate filing; effect =
  status cancellation_filed, sr26_date today, sr26_reason policy_cancelled, certificate_end_date =
  today + runoff_days; event fr_sr26_transmitted, base triggers [] (stays in fr). Receipt: one line
  with id, status, dates, reason.
- order_refiled_certificate_bf9cb0f2 (user, write): object = new filing replacing the given one;
  effect = new fr_filings row (requested, reinstatement_refiling, prior_fr_filing_id) + one
  fr_filing_fee_assessed row. Events: fr_filing_requested (base trigger fr:fr_filing_fee_assessed,
  same category) and fr_filing_fee_assessed (triggers []). No billing/auto/nonowner write.

Gold: runoff_days 18 (baseline 10); filing_fee 35.50 (baseline 35.00). COMPUTE OK.
Edge sensitivity (skip SR-26): filing_fee 40.50 instead of 35.50.

Probe table (scratch copies, /tmp probe harness on check_compute's evaluator)
| probe | result |
|---|---|
| SR base world | 18 |
| term cancelled, not reinstated, day 3 (window open) | 28 (MX(10, 20-3)=17 counted) |
| term cancelled 25 days ago (window shut) | 21 (std 10) |
| no required_through_date | 16 (FR-44 short tier) |
| returned payment in window | 16 |
| decoy returned payment 13 months old | 18 (excluded) |
| decoy reinstatement fee 13 months old | 18 (excluded) |
| lapse start after SR-26 date (negative lag) | rule + compute: counted as zero days |
| RF opening world (no SR-26) | 40.50 |
| RF after SR-26 | 35.50 |
| RF certificate end date passed | 55.50 (+15 re-certification) |
| RF no fee rows (None) | 57.50 (std basis) |
| RF fee 10 days old | 22.50 (std - standing) |
| RF no lapse recorded | lapse charge 0 |
| decoy notice 13 months old | 40.50 (excluded) |
| third notice in window | 48.00 |
| rejection 400 days old | recheck 0 |
| no required_through_date | requirement 0 |

Method-tier pair table (XF 10)
| factor | tier A | tier B | fall-through | distinguishing input/op |
|---|---|---|---|---|
| runoff_counting | std - MX(0, DAYS(lapse_start, SR-26 date)) | MX(std, window_days - DAYS(closed_date, SR-26 date)) | std | A adds lapse_start + subtraction/floor; B adds window param + closed_date + max |
| refiling_fee_basis | MX(0, std - fees standing) | ceil(std/2) to whole dollar | std | A adds the fee-ledger input + floor; B adds the round-up operation |

Trigger rule: tools write fr_sr26_transmitted (triggers []), fr_filing_requested (-> fr:fr_filing_fee_assessed),
fr_filing_fee_assessed (triggers []). None lands outside fr.

Gates task 0: check_task_tools OK, check_extended OK, replay OK, solvability OK, compute OK,
grounding OK, cross_fire OK.

Revisions
- check_compute: clean_payment factor read billing returns with no matching rows -> reworded to
  count payments received and returned payments (evidence rows exist).
- check_compute: data_recheck read a plain field -> tier now dated (rejected_date within 365 days).
- replay: '' foreign keys flagged dangling -> empty ids set to null; billing invoices unread -> added
  find_billing_invoices read (notices answer different unpaid installments).
- solvability: base contracts need owner fields and action args customer_id / fr_filing_id /
  auto_policy_id / nonowner_policy_id -> refiling tool takes them; prior owner term seeded;
  gate-conflicting SR-26 clauses overwritten (scoped).
- negative lag probe -> rule states zero days when lapse start is later; compute MX(0, DAYS).

## Task 1 — VA owner term CPA-VA-2318406: Hector removed 2026-10-05, his SR-22 fee never posted; Ethan's SR-22 ordered by Gloria
frozen_time 2026-10-07 14:10:00 EDT. Draw [4,6,6]: removal SR-26 4, late-posted fee 6, household fee 6.
Tree: fr_ext_household_fee (root, user) <- fr_ext_removal_sr26_runoff (value_input, household_standing, negated),
fr_ext_household_fee <- fr_ext_unbilled_fee (value_input, joint_credit, affirmative),
fr_ext_unbilled_fee <- fr_ext_removal_sr26_runoff (value_input, standing, negated). Order: SR-26, fee, household.

Capability cards
- transmit_removal_sr26_3c79d8f5 (agent): Owner certificate of a removed/excluded filer -> cancellation_filed,
  sr26_date today, reason filer_excluded_or_removed, end date today + runoff_days. Event fr_sr26_transmitted (triggers []).
- post_unbilled_filing_fee_f14427ed (agent): one fr_filing_fee_assessed row on the given filing (fee_reason = its
  filing_reason), fees_charged_total raised. Event fr_filing_fee_assessed (triggers []).
- order_household_certificate_bb3829bf (user): new fr_filings row (requested, new_requirement, verbatim driver data,
  form/type/state of the read-against certificate) + one fee row. Events fr_filing_requested (-> fr:fr_filing_fee_assessed)
  and fr_filing_fee_assessed. No write outside fr.

Gold: runoff_days 17 (baseline 10), fee_amount 7.91 (baseline 25.00), filing_fee 13.00 (baseline 25.00). COMPUTE OK.
Edge skips: no SR-26 -> household 10.00, late fee 9.91; no late fee -> household 17.00.

Probe table
| probe | result |
|---|---|
| SR base | 17 |
| exclusion instead of removal | 19 (MN(10, days to expiration)=10) |
| decoy removal, near-name driver | 17 (exact driver_name key) |
| decoy removal, same name, other term | 17 (term key) |
| no removal/exclusion recorded | 12 |
| removal dated after the SR-26 (negative lag) | 19 (zero days) |
| UB opening (no SR-26) | 9.91 |
| UB after SR-26 | 7.91 |
| UB delay 10 days | 21.00 (standard basis) |
| UB delay 150 days | 7.00 (half rounded down) |
| UB certificate end date passed | 5.91 |
| UB fifth copy | 7.91 (already in the two-or-more tier) |
| UB release-request document (not a copy) | 7.91 |
| HH opening | 14.00 |
| HH after SR-26 only | 17.00 |
| HH after both | 13.00 |
| HH fee later reversed (waiver decoy) | 17.00 |
| HH no removal change | 9.00 |
| HH zero plan balance | 14.00 |

Method-tier pair table
| factor | tier A | tier B | fall-through | distinguishing input/op |
|---|---|---|---|---|
| removal_counting | std - MX(0, DAYS(removal date, SR-26 date)) | MN(std, DAYS(SR-26 date, expiration)) | std | A adds the removal date + subtraction; B adds the expiration date + min |
| posting_basis_method | std x days left / term_days | int(std/2) | std | A adds two term inputs + division; B adds the floor-to-dollar op |
| household_fee_basis | MX(0, std - fees standing) | ceil(std x 3/4) | std | A adds the fee-ledger input + floor; B adds the round-up op |

Gates task 1: extended OK, task_tools OK, replay OK, solvability OK, compute OK, grounding OK, cross_fire OK.
Revisions: persona passive lines named the hidden problems ("a notice to the state", "a charge never put on the
account") -> replaced by a contentless go-ahead in both tasks; closure evidence path fixed to a field path.
Realism note (honest): the fr charter fixes flat fees; every adjustment above is stated as Cardinal Point's own
filing-services schedule (no statute invoked); FR-44 only FL/VA at 100/300/50 and 100/200/50; SR-26 timing
inherits the 3-day window. RND in compute is Python round; no gold value sits on a half-cent tie.

Revision (final compute gate): suite history_rows_max 2 < 8 -> the removal SR-26's certificate-age factor replaced by a
certificate-use factor counting copies issued in three whole months (COUNT on the certificate's own documents); Hector's
certificate now shows four copies (insured email 07-15, court mail 07-16, driver email 08-14, driver portal 09-18).
Late-posted fee 8.16 -> 7.91 (copy credit two-or-more tier); run-off 17 and household fee 13.00 unchanged; all
traces, tracing, closure figures and probes re-run and updated. history_rows_max now 9.

INSTANTIATE round 1: gates 7/7 green

## Round 2 rework (audits/policy_task/sr22_fr44_filings/, XF_recipe points 1-19)
Re-tree. Every factor now keys on certificate form/type, filing state vs residence/garaging state, backing package
(reinstatement window, bodily-injury limit), billing plan type, the reason and state of the coverage end, the state
of the backing term (Cardinal Point's own SR-26 notice and filing-fee schedules, worded as such), refiling after a
lapse as a new filing, and the certificate's own fee ledger and SR-26 dates. Removed: payment/lapse-fee/notice/copy
counts, relationship and points of a removed driver, plan balance, acceptance lag, requirement-days ladders, the
data re-check charge, term-remaining days.

Policies and tools (draw unchanged: T0 [6,5], T1 [4,6,6])
- T0: fr_ext_lapse_sr26_runoff 5 (transmit_lapse_sr26_2b138773) <- fr_ext_refiling_fee 6 (order_refiled_certificate_bf9cb0f2, user).
- T1: fr_ext_owner_sr26_runoff 4 (transmit_owner_sr26_911d0783) <- fr_ext_unbilled_fee 6 (post_unbilled_filing_fee_f14427ed)
  <- fr_ext_moved_refiling_fee 6 (order_moved_certificate_231455f7, user); fee also waits on the SR-26.
- Removed: fr_ext_removal_sr26_runoff / transmit_removal_sr26_3c79d8f5, fr_ext_household_fee / order_household_certificate_bb3829bf.
Worlds: T0 Darius Fenwick now resident in Savannah GA (CPN-GA-2471935), FL FR-44; T1 rebuilt: Renee Hollister,
TX owner term cancelled at her request 2026-10-05 after moving, VA owner term from 2026-10-05, AZ SR-22
Owner-Operator whose two 35.00 charges at the FR-44 rate were each reversed for company_error.
Gold (handling time, check_compute): T0 runoff 16, refiling fee 34.00; T1 runoff 12, fee charged again 26.00,
moved certificate fee 14.00. Baselines 10/35.00; 10/25.00/25.00.

Trigger rule: tools write fr_sr26_transmitted (triggers []), fr_filing_requested (-> fr:fr_filing_fee_assessed),
fr_filing_fee_assessed (triggers []). No tool writes or claims to write billing (docstrings say "nothing else is
posted by this action").

Probe table (scratch copies through check_compute's evaluator)
| probe | result |
|---|---|
| P1 base / absent non-owner term / in-state resident | 16 / 10 / 13 |
| P1 cancelled day 3 window 20 / window shut / negative lag | 26 / 19 / 19 |
| P1 minimum package (window 10) / insured_request | 14 / 15 |
| P2 opening / after SR-26 / ended 10 days / ended 40 days | 39.00 / 34.00 / 37.00 / 39.00 |
| P2 no fee rows / same-day second fee (tie) / decoy fee on other filing / Paid-in-Full | 51.00 / 34.00 / 34.00 / 31.00 |
| P3 base / nonpayment in window / underwriting / absent owner term | 12 / 17 / 14 / 10 |
| P3 closed after SR-26 (negative lag) / in-state filing / decoy later exclusion / second certificate | 14 / 10 / 12 / 12 |
| P4 opening / after SR-26 / fee already standing / no reversal recorded | 28.00 / 26.00 / 14.00 / 14.00 |
| P4 reversals same day (tie) / decoy reversal on other filing | 26.00 / 26.00 |
| P4 latest reversal 30 / 31 / 180 / 181 days before | 39.00 / 26.00 / 26.00 / 14.00 |
| P5 opening / after SR-26 only / after both | 44.00 / 39.00 / 14.00 |
| P5 same-day new-business tie / renewal decoy / no new term / second certificate | 14.00 / 14.00 / 0.00 / 14.00 |

Method-tier pair table (XF 10)
| factor | tier A | tier B | fall-through | distinguishing input/op |
|---|---|---|---|---|
| runoff_counting (P1) | std - MX(0, days lapse start -> SR-26) | MX(std, window - days closed -> SR-26) | std | A lapse date + subtraction; B window + max |
| owner_runoff_counting (P3) | std - MX(0, days closed -> SR-26) | MX(std, window - days) | std | A closed date + subtraction; B window + max |
| refiling_fee_basis / moved_fee_basis | MX(0, std - fees standing) | ceil(std/2) | std | A ledger input + floor; B round-up op |
| posting_basis_method (P4) | MN(reversed, int(std/2)) | 0 (fee standing, or delay > 180) | MN(reversed, std) | A floor-to-dollar op; B nothing tier, others non-zero |

Revisions this round: out-of-state reads guarded for an absent term (whole-input floor failed when a forced-off
read made "differs" true); P4 delay re-anchored on the latest reversal and capped at the fees reversed (history
floor); suite history_rows_max 9 from the fee ledgers; temporal entries for the SR-26 timing gates dropped where the
lapse rule's overwrites restate them (owner terms keep closed_date, stated in both SR-26 rules).

REWORK round 2: gates 7/7 green

## Round 3 rework (audits/policy_task/sr22_fr44_filings/ revision_2; XF_recipe points 1-23)

Items closed (class-wide across all five policies):
- F2-R1/F2-R2/F2-R3 (point 23 realism; one charge per dimension): struck the bodily-injury-limit credits, the
  billing-plan charges and the home-state/garaging-state charges that read the same field as the out-of-state
  charge, plus the package-window notices that counted the reinstatement window a second time. No add-ons replaced
  them; each computation was rebuilt on its real dimensions only: how the coverage ended or was restored (counting
  method, window counted once inside it), certificate type and backing (Owner / Operator / Owner-Operator), filing
  state against residence or garaging state (Florida/Virginia vs other), requirement period left
  (required_through_date), and transfer vs refiling after lapse (fee ledger fee_reason, reversed or not).
- F2-P1 (rule vs compute; point 20 zero edge): the fee charged again now states and computes "no charge past
  late_posting_days" as a zero basis, and the result is never below minimum_recharge, so a charge past the delay
  is the minimum, not a negative or a silent zero. Rule text, compute and ladder agree.
- F2-D1 (deadlock): the moved-certificate wait on a standing fee is carved out by record test (owner backing only;
  reason that is charged a filing fee; no fee reversed as withdrawn before transmission or as a duplicate request),
  and the depended-on fee never falls below its minimum. The non-owner backing never waits on it.
- F2-O1 (overwrite hygiene 5a): the lapse rule's suppression replaced_by restates the in-force content: an Owner
  Auto Policy term reinstated with or without a lapse, a non-owner term reinstated without a lapse, and a rescinded
  cancellation before the SR-26 still get no SR-26.
- Gate fixes this round: the P1 history floor (LATEST is not zeroed) answered by COUNT-by-fee_reason reads in all five
  prior-filing factors; the P4 coincidence with its baseline answered by moving T1 required_through_date to
  2027-03-31; the P5 prerequisite sentence reworded in business words (no code tokens); the T1 P3 cross-category
  reads cancelled out (+2/-2) and were made load-bearing by setting the owner-term out-of-state notice days to 5/3.
- Seeds: T0 and T1 certificates are now carrier_transfer with carrier_transfer fee rows; required_through 2027-08-31
  (T0) and 2027-03-31 (T1).

Method-tier table (in-scope tiers, all reachable):
| policy | method factor | tiers |
|---|---|---|
| lapse SR-26 | runoff_counting | lapse start counted / nonpayment cancel within window MX / std |
| refiling fee | refiling_fee_basis | std - standing within 30 days / ceil(std/2) 31-180 / std |
| owner SR-26 | owner_runoff_counting | insured_request from closed_date / nonpayment within window MX / std |
| fee charged again | posting_basis_method | MN(reversed, std) <= 30 / MN(reversed, int(std/2)) 31-180 / 0 then minimum |
| moved certificate | moved_fee_basis | std - standing within recent days / ceil(std/2) / std |

Probes (scratch copies; result of the probed computation):
| policy | probe | result | reading |
|---|---|---|---|
| lapse SR-26 | gold / in-state GA / other state NV | 18 / 14 / 16 | out-of-state tiers |
| lapse SR-26 | reinstatement_refiling ledger / correction-only ledger | 19 / 16 | prior tiers incl. none |
| lapse SR-26 | no or passed required_through / insured_request / absent term | 15 / 15 / 17 / 15 | absent-record tiers |
| lapse SR-26 | decoy filing with reinstatement fee | 18 | HID-scoped |
| refiling fee | gold / skip SR-26 / same-day second fee | 31 / 36 / 31 | tie stated |
| refiling fee | in-state / no required_through / absent term / empty ledger / end date before refiling | 16 / 36 / 13 / 43 / 34 | |
| owner SR-26 | gold / nonpayment / underwriting / garaged AZ / filed FL / absent term / 450 days | 16 / 21 / 18 / 13 / 18 / 15 / 14 | |
| fee charged again | gold / skip SR-26 / delay 17 / delay 0 | 20 / 22 / 33 / 33 | |
| fee charged again | delay > 180 / all lowest / decoy reversal on another filing | 10 / 10 / 20 | minimum floor; HID-scoped |
| moved certificate | gold / skip fee / fee at minimum | 10 / 30 / 20 | no deadlock |
| moved certificate | (TX term garaged AZ) VA not new_business / none at all / later renewal / later new_business / same-day tie | 0 / 0 / 10 / 0 / 10 | renewal ignored; tie out of scope by rule wording |

validate_scenario: only "required document ... not found" for the five policies (KB not rendered yet, same as every
difficulty). task_tools.py forbidden-substring scan clean. qcheck (verbatim compute_basis quotes, param names in
rule, factor ids not in tool names) clean.

REWORK round 3: gates 7/7 green

## Round 4 rework (audits/policy_task/sr22_fr44_filings/ revision_3; XF_recipe points 1-26; coordinator ruling)

Coordinator ruling applied: a fee or run-off built only from the publishable keys (company state schedule
grouped FL/VA, TX/GA, AZ/OH; certificate form; certificate type; backing type; filing state vs
residence/garaging state; how coverage ended or was restored) is acceptable at 4-6 factors; channel is out
(base fixes electronic); every incidental key is struck with no replacement; each dimension once.

Items closed:
- F3-R1 (requirement days): every remaining-requirement-days factor is struck in all five policies; no
  computation reads required_through_date.
- F3-R2 (prior-filing reason): every prior-filing/fee_reason factor is struck; no computation reads
  filing_reason or fee_reason. Also struck as incidental: the ledger fee-basis credit and the posting-delay
  method (ledger keys) and the date-gap continuity/standing credits.
- F3-B (counts): the two SR-26 rules were re-split along how coverage was restored instead of backing kind:
  the lapse SR-26 now covers any backing term (owner or non-owner) cancelled and since reinstated with a
  lapse; the cancellation SR-26 (renamed fr_ext_cancellation_sr26_runoff, new tool
  transmit_cancellation_sr26_eaec830f replacing transmit_owner_sr26_911d0783) covers any backing term
  cancelled and not reinstated. Type and backing therefore vary in each scope, and each run-off carries all
  six publishable keys: counting method (how coverage ended), state schedule (backing term's state group),
  form (the term's financial_responsibility_filing, keyed honestly on the stamp per XF 18), type, backing,
  out-of-state grade (different group / same group / in-state). Fees: method = how the certificate's
  coverage with the state ended (still certified -> half the fee rounded up; lapsed -> one and a half times
  rounded down; no SR-26 -> standard), plus state schedule, type, backing (refiling, re-charge),
  out-of-state, and for the fee charged again how the backing coverage ended. The moved certificate's method
  also tests whether a filing fee stands on the replaced certificate (transfer priced as a transfer only for
  a paid certificate). Draws met: T0 [6 lapse run-off, 5 refiling fee]; T1 [6 cancellation run-off, 6 fee
  charged again, 4 moved fee].
- F3-D1 (late SR-26): both SR-26 rules overwrite the base timely clause: an SR-26 not transmitted within
  sr26_transmit_within_days is still owed, is sent at once, and its certificate end date counts from its
  actual transmission; every wait on an SR-26 is satisfiable. T1's retired timely precondition removed.
- O3-1: the fee-charged-again docstring now says "whose charges were all reversed in full as charged in error".
- Owner-term reinstatement with a lapse now receives the lapse SR-26 (replaced_by restates: a term
  reinstated without a lapse, or a rescinded notice, still gets none).

New figures: T0 run-off 18 (end 2026-11-15), refiling fee 34.00 (skip SR-26 51.00). T1 run-off 17 (end
2026-10-24), fee charged again 31.00 (skip SR-26 43.00), moved fee 31.00 (skip either prerequisite 43.00).

Method-tier table:
| policy | method factor | tiers |
|---|---|---|
| lapse SR-26 | lapse_runoff_counting | nonpayment: from lapse_start_date / insured_request: from reinstatement_date / std |
| cancellation SR-26 | cancel_runoff_counting | insured_request: from closed_date / nonpayment in window: MX(std, window-days) / std |
| refiling fee | refiling_fee_method | still certified: ceil(std/2) / lapsed: floor(1.5 std) / std |
| fee charged again | recharge_fee_method | same three tiers on the filing itself |
| moved certificate | transfer_fee_method | fee standing and certified: ceil(std/2) / fee standing and lapsed: floor(1.5 std) / std |

Probes (scratch copies):
| policy | probe | result |
|---|---|---|
| lapse | gold with the customer's FL owner term as decoy | 18 |
| lapse | insured_request reinstated 10-27 / underwriting / stamp none | 20 / 21 / 15 |
| lapse | in-state GA / same-group TX / absent term / late SR-26 found 11-10 | 15 / 16 / 10 / 11 |
| refiling | gold / skip SR-26 / end date before refiling / absent term / in-state | 34 / 51 / 68 / 18 / 26 |
| cancellation | gold with the converted non-owner term as decoy / nonpayment in window / underwriting | 17 / 22 / 19 |
| cancellation | non-owner backed Operator certificate / absent term / late SR-26 found 10-20 | 16 / 10 / 9 |
| fee again | gold / skip SR-26 / end date passed / absent backing / decoy reversal on another filing | 31 / 43 / 55 / 13 / 31 |
| fee again | partly standing fees (outside its scope): cap 0 | 0 |
| moved | gold / skip fee / fee at the 10.00 minimum / renewal decoy | 31 / 43 / 31 / 31 |
| moved | later new_business on TX term / new term garaged AZ / no new term / end date passed | 28 / 17 / 13 / 55 |

Checks: compute_basis quotes, params named in rules, baselines, overwrites and prerequisite sentences all
verbatim (scratch check, 0 misses); no factor id inside a tool name; no duplicate factor ids; tracing
quotes re-matched to the current docstrings and rules; forbidden-substring scan clean; validate_scenario
lists only the five KB documents not yet rendered. Gate block: EXTENDED, TASK TOOL CONTRACT, REPLAY,
SOLVABILITY, COMPUTE (history_rows_max 9, branches_max 113), GROUNDING, SCOPE all OK.

REWORK round 4: gates 7/7 green

## Round 5 rework (audits/policy_task/sr22_fr44_filings/ revision_4; XF_recipe points 1-27; coordinator rulings a/b/c)

Rulings used: (a) cancellation reason and the certificate's standing with the state are two dimensions; (c) lapse length
keys how coverage was restored. (b) was weighed and not used: the filing-state group could only replace the out-of-state
grade (its condition forbids keeping both with the backing-state group), and no residence state other than a non-owner
term's own is readable, so the accepted pair (backing-state group + filing vs backing grade) stays. The fees now start
from flat company fees (refiling_base_fee, recharge_base_fee, transfer_base_fee), so the form stamp is charged once.

Items closed:
- F4-1: type and backing merged into one factor per computation (type ladders read the backing kind as evidence).
- F4-2: no "no backing term" tier anywhere; state ladders end at Arizona or Ohio; out-of-state ladders end at in-state.
- F4-3: the lapse counting method keys on lapse length (up to lapse_brief_days: from the reinstatement_date; up to
  lapse_extended_days: from the lapse_start_date; longer: from the SR-26 date); all three reachable within the
  10-30 day reinstatement windows; no cancellation-reason tier inside the lapse scope.
- F4-4: the refiling method's tiers are all in scope: still certified / ended more than refile_gap_days before the
  refiling / ended within refile_gap_days; no "no SR-26" tier.
- F4-5: no method reads the fee ledger; the moved certificate's wait on a standing fee is a state gate on
  fr_filings.fees_charged_total. The ledger is read only by the fee-charged-again cap guard.
- F4-6: each SR-26 timely overwrite names the other's case: lapse SR-26 day 0 = lapse_start_date, cancellation SR-26
  day 0 = closed_date; every other ended-term SR-26 keeps the base window; late SR-26 sent at once in both.
- F4-7: counts met without padding: T0 refiling fee 6 (standing method, lapse length, state group, out-of-state,
  type, form), lapse run-off 5 (lapse-length method, state group, out-of-state, type, form); T1 cancellation run-off
  4 (reason/window method, state group, out-of-state, type), fee charged again 6 (standing method, cancellation
  reason, state group, out-of-state, type, form), moved fee 6 (standing method, old term's cancellation reason —
  scope widened to any cancellation reason —, new-term state group, out-of-state, type, form).
- Seed: T1 certificate ledger gains the August and September wrong-rate charges and reversals (net zero on the plan),
  so the fee-charged-again cap reads eight rows (suite history depth 8).

Figures: T0 run-off 18 (end 2026-11-15), refiling fee 38.00 (skip SR-26 50.00). T1 run-off 15 (end 2026-10-22), fee
charged again 32.00 (skip SR-26 44.00), moved fee 35.00 (skip SR-26 47.00; skipping the fee charged again leaves the
gate unmet and the fee row missing).

Probes (scratch copies):
| policy | probe | result |
|---|---|---|
| lapse | gold with FL owner term decoy / 1-day / 6-day / 15-day lapse | 18 / 18 / 16 / 19 |
| lapse | in-state GA / same group TX / stamp none / late SR-26 found 11-10 | 15 / 16 / 15 / 9 |
| refiling | gold / end 8 days before / end 57 days before / 15-day lapse / no lapse | 38 / 50 / 62 / 41 / 36 |
| cancellation | gold with converted NNO decoy / nonpayment in window / underwriting / NNO Operator / late 10-20 | 15 / 20 / 17 / 14 / 7 |
| fee again | gold / no SR-26 / end passed / company cancellation / decoy reversal on another filing | 32 / 44 / 56 / 34 / 32 |
| moved | gold / skip fee / after nonpayment cancellation / end 36 days before | 35 / 35 / 37 / 59 |
| moved | later renewal premium decoy / later new_business on TX term / new term garaged AZ | 35 / 32 / 21 |

Checks: compute_basis, params, baselines, overwrites, prerequisite sentences and tracing quotes verbatim (0 misses);
no factor id inside a tool name; forbidden-substring scan clean; validate_scenario lists only the five unrendered KB
documents. Gate block: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE (history_rows_max 8, branches_max
113), GROUNDING, SCOPE all OK.

REWORK round 5: gates 7/7 green

## Round 6 rework (audits/policy_task/sr22_fr44_filings/ revision_5; text-only)

revision_5: task0 PASS, charter CLEAN; task 1 RED on one stale world assertion. Charter, tools and both
initial_states untouched (sha256 of fr.extended.yaml, task_tools.py and each initial_state identical before and after).
Fixed in tasks/1.json (all left over from the round-4 two-pair ledger):
- design_rationale WORLD ROWS: "four fee rows (two charges, two reversals; ...)" -> the eight rows actually seeded
  (four 35.00 charges 07-10, 07-15, 08-14, 09-14; four company_error reversals 07-12, 07-16, 08-17, 09-16; every
  pair mirrored on the Four-Pay plan, the first netted on invoice 1, the other three net zero).
- evaluation_criteria find_billing_transactions objective: "two 35.00 filing-fee charges" -> four, with four waivers.
- fee-charged-again call, fr_filing_id tracing: "the two 35.00 charges" -> the four charges and four reversals.
- prerequisite_closure edge (moved -> fee charged again) why_false: "both of its fee charges" -> all four.
Sweep of every proof, rationale, closure, contract and tracing text in both tasks for round-4 counts and figures
(two-charge wording, 70.00, 34.00, 31.00, 2026-10-23, owner-term / late-posted names): nothing else found.
Gate block: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.

REWORK round 6: gates 7/7 green

## Round 7 rework (audits/render_source/sr22_fr44_filings/render_r1.md: S1-S4)

Charter edits only (task_tools.py and both worlds untouched); scored values unchanged (COMPUTE OK on the same
expected figures and sensitivities).
- S1 (all 5 policies): the plain state-group bindings *_filed_group / *_home_group are removed; the out-of-state
  factor's own decision binding now tests "same state group" inline (compound tests, so the factor stays
  multi-source), and the group definition moved from the schedule sentence into the out-of-state factor's lead
  sentence. Class check: the only plain bindings read solely by factor bindings are the baseline's standard
  amount and P5's shared new-term record selection (XF 1 allows both).
- S2 (all 5 policies): each assembly sentence is now one generic order sentence by kind of adjustment —
  run-offs: "an adjustment that changes how the standard run-off is counted is applied first, and every
  adjustment that adds days is then added"; fees: "an adjustment that replaces the standard fee is applied
  first, and every adjustment that adds an amount is then added" (the fee-charged-again sentence keeps its
  minimum and cap). Each fee method's lead sentence now says its basis replaces the standard fee.
- S3: the moved certificate's ending ladder names converted_to_owner_policy in its no-charge tier.
- S4: the re-charge ending charge reads the recorded cancellation_reason, which a reinstated term keeps; a term
  whose recorded reason is nonpayment, underwriting or down_payment_dishonored takes the company tier whether or
  not since reinstated; only a never-cancelled term takes 0 (rule now matches the compute).
- task 1: recharge_ending_charge tier_taken updated to the new ladder wording.
Probes: reinstated owner term with recorded nonpayment -> company tier (34.00 vs gold 32.00); never-cancelled term
-> 0 tier (30.00); converted non-owner backing -> no ending charge; cancellation run-off in-state / same group /
other group -> 12 / 13 / 15. Checks: compute_basis quotes, params, baselines, overwrites, prerequisite sentences
verbatim (0 misses); no task text quotes a replaced sentence. Gate block 7/7 OK.

REWORK round 7: gates 7/7 green

## Round 8 rework (audits/policy_kb + audits/runtime_context, SRC-1; seed-only)

fr.extended.yaml (sha256 1af747543543cd72...) and task_tools.py (b1ec27e054c37065...) unchanged, checked after the gates.
SRC-1 (task 1): the moved-certificate gold equalled each seeded 35.00 charge (copy shortcut) and the four identical
wrong charges were an unrealistic history. Re-seed:
- the replaced certificate is a Florida SR-22 Owner-Operator (Florida order, out-of-state on the Texas term), so the
  moved fee prices FL against VA in the same state group: moved certificate fee 31.00 (was 35.00); cancellation run-off
  15 and fee charged again 32.00 unchanged (FL against TX is out of group, as AZ against TX was).
- fee ledger: four charges with distinct real errors, each reversed once as company_error: 35.00 on 07-10 at the FR-44
  rate (Florida is an FR-44 state), 25.00 on 07-15 at the right rate but coded new_requirement, 50.00 on 08-14 billed
  for a Florida and a Texas certificate though only one exists, 25.00 on 09-14 re-sent by the September billing run;
  plan mirrors re-priced to the same amounts (net zero; balances and invoices unchanged). Cap now 135.00.
- point 26: no recorded amount in the world equals a scored value (31.00, 32.00), and the fee charged again (32.00,
  recorded before the move) differs from the moved fee; copying any old fee misses gold.
- persona: the requirement is Florida's (suspension for driving uninsured in Orlando); all task-1 proof, rationale,
  closure, contract, objective and tracing text swept for Arizona/AZ and the old figures (35.00 gold, 47.00, 140.00).
Suite rules kept: history depth 8 (fee-charged-again cap reads the eight rows), multi-source and cross-difficulty
factors unchanged. Gate block 7/7 OK; check_traceability against the published KB OK (0 missing).

REWORK round 8: gates 7/7 green

## Round 9 rework (KB cross-product re-judge revision_3: SRC-2..SRC-5; seed-only)

fr.extended.yaml (1af747543543cd72...) and task_tools.py (b1ec27e054c37065...) unchanged, checked after the gates.
- SRC-2 (task 0): Darius is now a Tampa, Florida resident (profile phone 8135552174, ZIP 33604, Tampa address, home
  state FL; non-owner term CPN-FL-2471935, resident_state FL) and his FR-44 Operator certificate is a Virginia
  requirement filed with Virginia: the non-owner rule backs an FR-44 only where the residence state is among the
  package's FR-44 states (FL, VA). Florida's nonpayment notice days (10) equal Georgia's, so every seeded date stands.
  Gold moves: lapse run-off 18 (state FL +4, out-of-state VA vs FL same group +1), refiling fee 37.00 (state FL +6.00,
  out-of-state +4.00); persona, tracing, traces, sensitivities, closure and rationale rewritten.
- SRC-3 (task 0): reinstatement re-written premium by the certified-exposure rule (certificate filed 05-15, required
  through 2027-08-31): 128.93 for 18 days from 2026-10-25; term written premium 1318.00, reactivation charge 128.93,
  Six-Pay balance 148.93.
- SRC-4 (both): insured-request returns by the published auto rules: task 0 FL term 842.00 x 69/181 = 320.98 (vehicle
  sold, nothing retained; Paid-in-Full), written premium 521.02, PIF credit and refund 320.98; task 1 TX term
  1164.00 x 87/184 - 15.00 = 535.37 for 87 days (SR-22 run-off 10 days; moved out of state; Four-Pay charge),
  written premium 628.63, Four-Pay credit 535.37, balance -234.37.
- SRC-5 (task 1): the six plan mirrors of the 07-15, 08-14 and 09-14 fee charges and their reversals are removed
  (reversed before the next invoice, so never billed); only the first fee and its reversal sit on the plan; contract
  and rationale text updated.
Point 26: no recorded amount equals a scored value in either world (37.00; 32.00, 31.00). Suite rules kept (history
depth 8 in task 1; multi-source and cross-difficulty factors unchanged). Gate block 7/7 OK; traceability OK.

REWORK round 9: gates 7/7 green
