# Policy-KB bijection audit — entrance_fee_contracts_and_refunds / task 1

Round 1 (revision_1). Written after the blind answer in `audits/runtime_context/entrance_fee_contracts_and_refunds/task_1.md` was frozen (hash `98123870...018e`, recorded 2026-10-05T11:00:04Z).

Scope: charter_scope `entrance_ext_final_period_amortization`, `entrance_ext_annual_tax_letter`, `entrance_ext_closing_year_tax_letter`, `entrance_ext_estate_refund_release`; tools `book_final_period_amortization_cad149c9`, `issue_annual_tax_letter_ce10c97a`, `issue_closing_year_tax_letter_050bd78c`, `release_estate_refund_4b5e42b1`; governing base policies `entrance_occupancy_and_amortization`, `entrance_tax_letter_policy`, `entrance_refund_timing`, `entrance_refund_calculation`, `entrance_termination` (death ending), and the base refs of the estate release (`entrance_rescission`, `entrance_pre_occupancy_cancellation`); variant parameters read; corpus `docs/entrance/*.json` title/content, plus the docs/independent figures the entrance documents name (post-death fee days, internal transfer notice days).

Entry conditions (Step 0), cited from the brief: policy-side PASS (round 2); DOCS OK; TRACEABILITY OK; runtime view + DB path supplied and re-verified. Complete.

## source_to_kb

### entrance_ext_final_period_amortization
| Source atom | KB home | Equivalence |
|---|---|---|
| Rule: month begun on/before termination date without an entry is amortized after termination, once, whatever the status; others only while occupied, each once | amortization_after_termination: "Rule." + ledger table + months numbering / dating | Equivalent |
| Baseline: entrance fee × amortization_pct_per_month / 100 for that month, capped at refundable balance above the floor, half-up once; entry dated first day of that month (params amortization_pct_per_month, refundable_floor_pct) | final_period_amortization_amount: "Amount." + terms (floor amount rounded half up — compute `RND(fee × floor/100, 2)`) + order; plan figures in amortization_schedule_by_plan | Equivalent; silent about variation; fall-back 5752.00 definite |
| Thirty-day convention; first day of last month amortized = latest amortization posting date; days ≥ 0 | final_month_amortization_share "Counting the days." | Equivalent |
| Factor `final_month_count_end` (vacated before termination → vacate date; death & not vacated before → date of death, counted as a day; else termination date) | final_month_day_count_end_date: sentence, records read (paired Independent Living Residency Agreement vacate date), end-date table, cases (39 → 9 / 10) | Full ladder; equivalent (incl. MX(0) on the vacate branch) |
| Factor `final_month_share` (≤10 → d/30; 11–20 → 0.5; >20 → 1) | final_month_amortization_share: "Share." + ladder + boundaries | Full ladder; equivalent |
| Factor `amortization_step_rate` (≥36 → ×0.5; 18–35 → ×0.75; <18 → plan %) | long_tenure_amortization_percentage: sentence, ladder, boundaries, per-plan derived table (2.0/1.5/1.0 rows correct) | Full ladder; equivalent |
| Factor `estate_surrender_reduction` (death & vacate ≤15 days → 0.5; 16–30 → 0.25; else 0) | estate_apartment_surrender_reduction: sentence, records read, ladder incl. "before the date of death, or not vacated", boundaries | Full ladder; equivalent (compute `0 <= DAYS(...) <= 15`) |
| Order: reduced percentage × fee, then share, then cap, single rounding | estate_apartment_surrender_reduction ¶2 + final_month_amortization_share "Where the share acts" + final_period_amortization_amount "Order" | Order entailed jointly; equivalent |
| Overwrite 1: "booked only while occupied ... once" retired → after-termination rule | occupancy_and_amortization_rules item 5 retired note; replacement in amortization_after_termination | Correct retired surface |
| Overwrite 2: "of amortization_pct_per_month percent ... rounded" retired → "every month at plan % ... except the final period ... scaled" | occupancy_and_amortization_rules item 3 retired note; replacement in long_tenure_amortization_percentage ¶1 | Correct |
| Overwrite 3: "a month that starts on or before the termination date is amortized in full" retired → share ladder | occupancy_and_amortization_rules item 4 retired note; replacement in final_month_amortization_share | Correct; the rest of item 4 (floor stop, stop at termination) still in force |
| `prerequisite: []` | — | Nothing to carry; no document states that the amortization waits on anything |
| Tool `book_final_period_amortization_cad149c9` (agent; entrance_agreement_id, amortization_month, month_start_date, amortization_amount; entry dated month_start_date; balance down; status unchanged) | amortization_after_termination "Booking the entry" + parameter table + receipt | Equivalent to task_tools.py |

### entrance_ext_annual_tax_letter
| Source atom | KB home | Equivalence |
|---|---|---|
| One annual letter per tax year, January run, missed letter in next run, never twice | annual_tax_letter_issue "Rule." | Equivalent |
| Year covered: not the ending year; year after latest letter, or year of first entrance fee payment | annual_tax_letter_issue "Year covered." + table | Equivalent |
| Baseline: pct_entrance × entrance fee received + pct_monthly × IL payments, window 1–12 whole months, half-up (params medical_expense_pct_*) | annual_tax_letter_amount "Amount stated." + inputs; tax_letter_percentages_by_plan | Equivalent; fall-back 3495.80 definite |
| Sum of four portions before one rounding (overwrite replaced_by) | annual_tax_letter_amount ("two portions are added together before the single rounding"), care_stay_medical_share ¶2, stay_add_on_medical_share ¶2 ("added to the letter's medical expense amount before its single rounding") | Entailed jointly |
| Factor `letter_window` (latest letter ≥23 months → 13–24; none → 1 month back to month of latest deposit; else 1–12) | tax_letter_entry_window: sentence, month-count restatement, tables, boundaries | Full ladder; equivalent |
| Factor `settlement_basis` (returned → net of returns and returned-payment fees; offset and none returned → without offsets; else all) | independent_living_payments_on_annual_letter | Full ladder; equivalent |
| Factor `stay_charges_basis` (early-departure → net; level-change only → net; else full), trial stay excluded | care_stay_credits_on_annual_letter | Full ladder; equivalent |
| Factor `stay_payer_basis` (insurer → less insurer; no insurer & guest refund → less refunds; else as counted; floor 0) | care_stay_charges_borne_on_annual_letter | Full ladder; equivalent |
| Factor `care_stay_share` (recovery → 1.0; AL/MC respite only → 0.6; else 0), applied to charges counted as borne | care_stay_medical_share | Full ladder; equivalent |
| Factor `stay_addon_share` (medication setup → 1.0; only incontinence/companion → 0.5; else 0), applied to total of the three add-ons | stay_add_on_medical_share | Full ladder; equivalent |
| 0.0 plans → 0.00 | annual_tax_letter_amount "Plans at 0.0."; tax_letter_general_terms item 2 | Equivalent |
| Overwrites: base amount clause and "One tax letter ... per tax year" retired | tax_letter_general_terms items 2 and 4 retired notes; items 1, 3 and the 0.0 sentence carried in force | Correct |
| Tool `issue_annual_tax_letter_ce10c97a` | annual_tax_letter_issue "Issuing the letter" + table + receipt (mailing address on file, as in the docstring) | Equivalent |

### entrance_ext_closing_year_tax_letter
| Source atom | KB home | Equivalence |
|---|---|---|
| Prerequisite → final_period_amortization (state): "The tax letter for the year in which an agreement terminated is issued only after the agreement's ledger carries an amortization entry for every month of occupancy that began on or before the termination date." | closing_year_tax_letter_issue "Conditions of issue" — verbatim; same-form table in same doc | Verbatim, connective "only after", state form. Resolution: sentence + amortization_after_termination ("a month of occupancy that began on or before the termination date and carries no amortization entry ... is amortized after the termination") + ledger (months 1–23; month 24 began on the termination date). Hard gate both sides. Only in this hub |
| Prerequisite → annual_tax_letter (state): "The tax letter for the year in which an agreement terminated is not issued until the agreement's ledger carries a tax letter for every earlier tax year in which entrance fee or independent living monthly fees were paid." | closing_year_tax_letter_issue "Conditions of issue" — verbatim | Verbatim, "not issued until", state form. Resolution: sentence + annual_tax_letter_issue ("a letter the January run missed is issued with the next January run"; year covered = year after latest letter) + ledgers (letters 2023/2024; IL fees paid in 2025). Only in this hub |
| One closing-year letter, January run after that year, never a second | closing_year_tax_letter_issue "Rule." | Equivalent |
| Baseline: pct_entrance × fee received in closing year + pct_monthly × IL payments in closing year; 1–12 months; half-up | closing_year_letter_amount | Equivalent; fall-back 3495.80 definite |
| Sum of three shares before one rounding | closing_year_letter_amount ¶2 + closing_year_care_stay_share ¶2 | Entailed |
| Factor `closing_entrance_basis` (after-occupancy ending in closing year → retention + amortization posted in closing year; pre-occupancy ending → 0; else fee received) + "entrance fee share = pct × that amount" | closing_year_entrance_fee_amount (ending table; examples show the retention counts only when posted in the closing year, matching compute `retention_in_year`) | Full ladder; equivalent |
| Factor `closing_il_basis` (proration credit → charges less credits; returned payment → payments less returns; else payments) + residence fee share | closing_year_independent_living_amount | Full ladder; equivalent |
| Factor `post_residency_deduction` (death → post-death fee days; AL/MC transfer → internal transfer notice days; else 0) × monthly fee / 30, half-up, from IL amount before %, floor 0 | post_residency_fee_deduction (names the Independent Living Residency Agreement terms as the source of the day figures; docs/independent notice_and_statement_periods carries 14/30 post-death days by type) | Full ladder; equivalent (see PN6) |
| Factor `closing_care_share` (recovery → 1.0; AL/MC respite only → 0.6; else 0) | closing_year_care_stay_share | Full ladder; equivalent |
| Factor `closing_stay_payer` (insurer → less insurer; no insurer & early-departure credits → less credits; else full; floor 0) | closing_year_care_stay_charges_borne | Full ladder; equivalent |
| 0.0 plans → 0.00; overwrites (amount clause, one-letter clause) retired | closing_year_letter_amount; tax_letter_general_terms retired notes | Correct |
| Tool `issue_closing_year_tax_letter_050bd78c` | closing_year_tax_letter_issue "Issuing the letter" | Equivalent |

### entrance_ext_estate_refund_release
| Source atom | KB home | Equivalence |
|---|---|---|
| Prerequisite → final_period_amortization (state): "An estate refund is not released until the agreement's ledger carries an amortization entry for every month of occupancy that began on or before the termination date." | estate_refund_release "Conditions of release" — verbatim; same-form table | Verbatim, state form; resolution as above; only in this hub |
| Prerequisite → closing_year_tax_letter (state): "An estate refund is released only after the agreement's ledger carries the tax letter for the tax year in which the agreement terminated." | estate_refund_release — verbatim | Verbatim, state form; resolution: sentence + closing_year_tax_letter_issue ("The tax year in which an Entrance Fee Agreement ended receives one closing-year letter") + ledger (no 2026 letter); only in this hub |
| Released by the personal representative named in the letters on file; one payment by check to the estate c/o address on file | estate_refund_release "Release." + "The release signature" | Equivalent |
| Baseline: refundable amount = received − every retention, amortization, processing fee, offset, refurbishment deduction, refund; half-up; one payment (params none) | estate_refund_amount | Equivalent; fall-back definite |
| Closes on payment; delay interest is Larkspur's money, balance below 0.00 (overwrite replaced_by) | estate_refund_release "An estate refund closes the agreement when it is paid"; delay_interest_day_count_by_campus "Effect on the balance."; retired clause in refund_due_dates_and_payment | Correct retired surface and replacement |
| Delay interest on late payment, campus rate + step, interest days counted, added before rounding | delay_interest_day_count_by_campus "Delay interest." | Equivalent |
| Factor `delay_interest_start` (letters ≥180 days late → letters + 10; 1–179 → letters date; else due date; floor 0) | delay_interest_start_date | Full ladder; equivalent |
| Factor `interest_day_inclusion` (estate letters after due → +1; resident → −1 floor 0; else as run) | delay_interest_day_inclusion | Full ladder; equivalent |
| Factor `campus_statutory_rate` (Brookfield 8.0; Harbor View 9.0; else 0; only when paid after due) | campus_statutory_delay_interest_rate | Full ladder; equivalent |
| Factor `outstanding_step` (≥270 → 0.5; 90–269 → 0.25; else 0) | long_outstanding_refund_step | Full ladder; equivalent |
| Factor `delay_interest_day_count` (Brookfield /365; Harbor View ÷12 × whole months due→payment; else /360; half-up) | delay_interest_day_count_by_campus | Full ladder; equivalent |
| Tool `release_estate_refund_4b5e42b1` (user; entrance_agreement_id, refund_amount; check to estate; balance down; closed today) | estate_refund_release "The release signature" (agent unlocks, hands over to the personal representative) + table + receipt | Equivalent |

### Base policies (full domain)
- `entrance_occupancy_and_amortization`: items 1 (full fee before occupancy), 2 (admin retention 4%), 3 (monthly booking schedule), 4 (floor stop, stop at termination), 6 (move to care), 7 (months-of-occupancy measure) in force; three retired clauses marked retired. Equivalent.
- `entrance_tax_letter_policy`: items 1, 3, 0.0 sentence in force; two retired notes. Percentages and 01-31 deadline in tax_letter_percentages_by_plan. Equivalent.
- `entrance_refund_timing`, `entrance_refund_calculation`, `entrance_termination`: refund_due_dates_and_payment, refund_payment_terms_by_plan, refund_calculation_and_deductions (offsets oldest first, received as entrance-refund-offset payments — event trigger; work order "exactly as printed" — event field; cap 5% rounded; statement 15 days; terminated-status gate; once-only; close without refund), termination_after_occupancy and termination_and_apartment_change_terms (90/60, death ending, survivor, care moves, for cause, apartment change, status gate). Equivalent.
- Variant parameters: every per-plan figure of the six variants matches the KB tables (pricing multipliers/second-person fees, floors, monthly rates, NW/income multiples, health screening, benefits, refund contingency, medical expense percentages).

## kb_to_source
- Every normative sentence in the documents above traces to the structured source (rules, baselines, ladders, compute, events, tool docstrings, variant parameters). Checked glosses: "The first day of the last month already amortized is the posting date of the latest amortization entry" (compute `LATEST posting_date`); "The months already amortized are the amortization entries on the agreement's ledger" (compute `COUNT`); "A refund is outstanding past its due date when it is paid on a day after the refund due date" (compute `DAYS(due, NOW) > 0`); "the letters date is the estate documents date on the agreement" (compute `F('estate_documents_date')`); the letter "is sent to the mailing address on file" (tool docstrings).
- Additions / rewrites / omissions: none at the level of entailment.
- Prerequisite-side check 1 (cross-problem operational guidance): none — estate_refund_release and closing_year_tax_letter_issue name only their own tools; neither says which tool or problem brings the waited-on states about.
- Prerequisite-side check 2 (opening world state as policy fact): none — no document says any agreement is missing an amortization entry or a tax letter; the annual_tax_letter_issue table and the delay-interest tables are labelled hypothetical.

## bijection_verdict
**PASS.** All atoms of the four extended policies and their governing base policies are carried with equal strength, including untriggered tiers (no-letter first window, offset-only settlement, level-change credits, guest refunds, AL/MC respite 0.6 share, incontinence/companion 0.5 share, Harbor View month-count day basis, resident-payee −1 day, transfer deductions); the retired surface is correct; the four prerequisite sentences are verbatim on their blocked hubs only. First revision.

Policy-side notes (recorded, verdict unaffected):
- **PN2 (age anchor, base pricing).** The rule says ages are measured "on the planned occupancy date", parameter_schema says "on the occupancy date"; the KB carries both (pricing_payment_and_qualification_rules §3 "planned occupancy date"; admission_qualification_standards "The ages are measured on the occupancy date"). Nature: source inconsistency; outside both tasks' paths.
- **PN5 (factor coupling).** Several method factors are defined on sibling factors' outputs (combined rate = campus rate + outstanding step and interest days counted; reduced percentage then share then cap; care-stay share applied to charges borne/counted); their documents therefore name those quantities. Source-pinned, not a rendering addition.
- **PN6 (cross-product reading, untriggered).** The ladder tier "ended on a transfer to Larkspur assisted living or memory care → the internal transfer notice days of that apartment type" reads CPARAM `internal_transfer_notice_days`; the independent-living corpus gives that schedule as the period "for a move to Larkspur assisted living" while its addendum Clause 1(a) says a move to memory care "adds 0 calendar days". A reader handling a memory-care transfer could take 0 or 7/14. Cross-product contradictions are outside this skill's detection range; recorded as observed, not judged.

## dependency_form
Blind hop marks: four hops (release ← final amortization; release ← closing-year letter; closing-year letter ← final amortization; closing-year letter ← annual letter), all state-derived; none pre-solved.

Scan of the whole entrance corpus and reachable docs:
- Each of the four prerequisite sentences stands verbatim on its blocked hub only (exact-string search over docs/*/*.json); the same-form tables beside them ("Read against the agreement's ledger, both states must stand before the release is signed"; "the closing-year letter waits while either of these states is missing") restate states, not actions, in the same document.
- The depended-on documents (amortization_after_termination, annual_tax_letter_issue, closing_year_tax_letter_issue as depended-on by the release) do not mention the release or the closing-year letter waiting on them; no document states a dependency the source does not state.
- Tool names: each tool only in its own hub; no other problem's tool in the blocked hubs.
- No aggregated table/checklist/roadmap spanning amortization → letters → release; no ordered step list; no FAQ or example walking across these problems.
- Titles/openings general ("Estate Services Terms for Releasing an Entrance Fee Agreement Refund to an Estate", "Closing-Year Tax Letter of an Ended Entrance Fee Agreement", "Entrance Fee Agreement Amortization of a Month Left Open at Termination", "Entrance Fee Agreement Annual Tax Letter: Tax Years Covered and Issue"); none restates a caller's request or labels a situation-specific procedure.
- Computation documents (final_period_amortization_amount, annual_tax_letter_amount, closing_year_letter_amount, estate_refund_amount): no hint that anything modifies them.
- Factor documents: no tier-of-most-customers statement, no task rows as fact; sibling-factor quantities named only where the source's ladder/rule text names them (PN5).
- Depended-on documents reachable through the sentence's own words ("amortization entry", "month of occupancy that began on or before the termination date", "tax letter", "tax year").

**PASS** (KB-EXPLICIT).

## part_verdicts (task 1)
- KB-RUNTIME: PASS
- KB-BIJECTION: PASS (policy-side notes PN2, PN5, PN6 recorded; PN1/PN3/PN4 in task_0's file concern the pre-occupancy policies)
- KB-EXPLICIT: PASS

## difficulty_closeout (entrance_fee_contracts_and_refunds)
- Audit files one-to-one with tasks 0 and 1 in both `runtime_context/` and `policy_kb/`; each carries blind_answer → gt_comparison and source_to_kb / kb_to_source / bijection_verdict / dependency_form; no older revisions exist (round 1).
- All six extended policies of the difficulty are covered across the two files; every prerequisite sentence (5) verbatim on its blocked hub only; every declared factor ladder (29 factors) carried in full in its own document, reachable from the record kinds it reads.
- Gates re-run on the final form (2026-10-05, repo root):
  - `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0034_senior_living_operator entrance` → `[PASS] mechanical gates ...` / `[MANUAL REQUIRED] ...` / `DOCS OK`
  - `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0034_senior_living_operator/tasks/entrance_fee_contracts_and_refunds` → `TRACEABILITY OK`
- Difficulty verdict: the rendering of `entrance_fee_contracts_and_refunds` passes (KB-RUNTIME PASS + KB-BIJECTION PASS + KB-EXPLICIT PASS for both tasks), with policy-side notes PN1–PN6 handed back on record.
- Coverage note: only product `entrance` is audited; cross-product contradictions (e.g. PN6) are outside this skill's detection range.
