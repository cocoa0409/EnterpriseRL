# Runtime-context blind audit — entrance_fee_contracts_and_refunds / task 1

Round 1 (revision_1). Auditor: independent erl-kb-doc-policy-audit agent (not the renderer of docs/entrance, not the policy-side auditor).

## blind_answer

### Freeze declaration and scope
- Freeze time: 2026-10-05T11:05Z (written to disk before any source-layer artifact was opened).
- Scope: difficulty `entrance_fee_contracts_and_refunds`, product `entrance`, task index 1.
- Runtime view: `audits/_views/runtime/entrance_fee_contracts_and_refunds/task_1.runtime.json`, sha256 `bbadd63b7c3a5d5cfa1076758416c068557664fa4070ce42cbe10393277e8f81` (re-verified); DB access script sha256 `96c004f6a2c6561216f70c7f914cdf2c403e974524c96f040519f169b8aa6c50` (re-verified).
- Published corpus: `docs/entrance/*.json` (59 documents), title/content only; aggregate hash `25d0ba774b2a6e72c03a874504741b67dc6738a7f9ea935cc0229e5607175f12`. Cross-product figure lookup in `docs/independent/*` title/content (post-death fee days), as the runtime KB_search/grep would reach it.
- Visible materials used: frozen_time `2027-01-25 10:05:00 EST`; the agent system prompt (identical to task 0 except the time); user_scenario (only as lines the simulator would say); tool schemas; DB returns through `db_query.py entrance_fee_contracts_and_refunds 1 call <tool>` (find_customers, find_entrance_agreements/_ledger/_requests, find_independent_residencies/_ledger/_requests, find_respite_stays/_ledger/_requests, find_assisted_residencies, find_memory_residencies).
- Explicitly not read before this freeze: `*.extended.yaml`, `task_tools.py`, task JSONs, worklog, `audits/policy_task/`, `audits/_views/policy_task/`, docs `meta`, blueprint products yaml, raw `initial_state`. No recursive grep over `tasks/` or `audits/`.
- DB side: blind (tool-shaped queries only).

### Item 1 — what the user expresses; simulator mode
- Caller: Allison Whitfield Brandt, daughter and executor of Raymond Ellis Whitfield (died 2026-01-20); letters testamentary sent "in late December". Target: "the estate's refund from his entrance fee contract to be paid out". No figure ("go by their records"; recalls "a little over a hundred and forty thousand dollars").
- Simulator passive: identity on request (DOB 1937-09-14, SSN last4 7861; phones if more needed); care stays only if asked; apartment clearance only if asked; payee only if asked ("a check made out to the estate ... address Larkspur has on file"). Pre-agreed: "If the agent says some entries or paperwork on the account have to be completed or corrected before the refund can be released, say that is fine and they should go ahead." Executes the signing step with "the reference number and the amount the agent gives you".

### Item 2 — act / wait / refuse
Act now: three agent writes on the ledger, then the representative's release signature. Grounds:
- Profile: `date_of_death '2026-01-20'`, `representative_name 'Allison Whitfield Brandt'`, `representative_authority 'durable_poa'`, mailing address c/o Allison Brandt, Apex.
- Agreement `ea7a091e-791d-4d44-9d64-cd344fe3adc5`: LifeCare Declining Balance Plan, Larkspur at Brookfield, `status 'refund_scheduled'`, `entrance_fee_amount 287600.0`, `occupancy_date '2024-02-20'`, `termination_date '2026-01-20'`, `termination_reason 'death'`, `refund_due_date '2026-03-21'`, `refund_payee_type 'estate'`, `estate_documents_date '2026-12-28'`, `refundable_balance 143800`.
- Letters on file (refund_due_dates_and_payment: "may be paid only after letters testamentary or letters of administration are on file, shown by the date the letters were received on the agreement"); status permits payment ("refunds may be paid only while the agreement is in rescinded, cancelled or refund scheduled status").
- The release is the personal representative's own signature (estate_refund_release: "released by the estate's personal representative named in the letters on file, who signs the refund release"); the caller states she is the executor.
- Release conditions not yet met (see item 6), so the release cannot be handed over first.
- No offsets: IL `account_balance 0.0`, respite stays `account_balance 0.0`, no AL/MC residency; and deductions "may be recorded only while the agreement is in terminated status" (it is refund_scheduled).

### Item 3 — object, keys, rows
- Customer `e462fa1d-439f-468d-a5c4-9ba538539d3a`; agreement `ea7a091e-...`; paired IL residency `d6472373-748a-45da-869d-9e8b00b8c09d` (One-Bedroom B-214, `monthly_service_fee 4540.0`, `vacate_date '2026-02-02'`, `termination_reason 'death'`).
- Entrance ledger: deposit 28760.00 (2023-11-28), balance 258840.00 (2024-02-12), admin retention 11504.00 (2024-02-20), amortization months 1–23 at 5752.00 (latest dated 2025-12-20), tax letters for 2023 (posted 2024-01-25) and 2024 (posted 2025-01-24). No tax letter for 2025 or 2026; no request records.
- IL ledger: monthly charges/payments 2024-02..2026-02; 2025-05 ACH payment returned (4325.12, 2025-05-06) with a 35.00 returned-payment fee and a 4360.12 certified-check payment (2025-05-09); 2026-01 and 2026-02 charges 4540.00 each, paid; move-out proration credit 4053.57 (2026-02-20) and credit-balance refund 4053.57.
- Respite ledger: Post-Hospital Recovery Stay 2025-09-08 charge 5572.00 (14 nights), medication_setup add-on 85.00, early-departure credit 796.00 (2025-09-20), family payment 2786.00, LTC insurer payment 2075.00 (2025-10-03); Recovery Stay 2026-01-06 charge 3980.00 (10 nights), medication_setup 85.00, family 2786.00, LTC insurer 1279.00 (2026-01-28).

### Item 4 — scored parameters
**(a) final-period amortization, month 24 (book_final_period_amortization_cad149c9)**
- Month 24 begins 2026-01-20 (monthly anniversary of 2024-02-20) = the termination date → "began on or before the termination date and carries no amortization entry" (amortization_after_termination) → booked once, `amortization_month 24`, `month_start_date 2026-01-20`.
- Computation document (final_period_amortization_amount): "the entrance fee times the plan's monthly amortization percentage, divided by 100 ... never more than the refundable balance above the refundable floor, rounded to the cent half up". Plan figures (amortization_schedule_by_plan): LifeCare Declining Balance 2.0, floor 0. **Fall-back: 287600.00 × 2.0% = 5752.00.**
- Factor "months already amortized" (long_tenure_amortization_percentage): "where 18 to 35 months do it is three quarters of the plan's percentage" → 23 entries → 1.5. Found from: count of amortization entries on the entrance ledger.
- Factor "surrender reduction" (estate_apartment_surrender_reduction): "terminated on the resident's death and the apartment was vacated within 15 days after the date of death, the reduction is 0.5 percentage points" → vacate 2026-02-02, 13 days after death → 1.0. Found from: IL residency vacate date vs date of death.
- Factor "end date of the count" (final_month_day_count_end_date): apartment not vacated before the termination date and terminated on death → "the count runs to the date of death and the date of death itself is counted as a day". Factor "share" (final_month_amortization_share): calendar days from the latest amortization posting date 2025-12-20 to 2026-01-20 = 31, less 30 = 1, plus the death day = 2 (consistent with that document's example 39 → 9 / death 10) → "10 days or fewer are amortized pro rata at that number of days over 30" → 2/30.
- Amount: 287600.00 × 1.0% × 2/30 = 191.7333; cap room 143800.00 → **191.73**.

**(b) annual tax letter for 2025 (issue_annual_tax_letter_ce10c97a)**
- Tax year: "the year after the latest tax letter on the agreement's ledger" → 2025 (latest is for 2024; 2025 is not the year the agreement ended). Missed by the January 2026 run → "issued with the next January run" (today, 2027-01-25).
- Computation document (annual_tax_letter_amount): entrance-fee % × entrance fee received + monthly-fee % × IL payments, window "1 to 12 whole months before the issue date". Plan percentages (tax_letter_percentages_by_plan): 34.6 / 38.5. **Fall-back** (window 2025-12-26..2026-12-25: IL payments 4540.00 + 4540.00): 38.5% × 9080.00 = **3495.80**.
- Factor "window" (tax_letter_entry_window): latest letter posted 2025-01-24 = 24 whole months before 2027-01-25 → "23 or more ... missed-run letter and reads the entries posted 13 to 24 whole months before the issue date" → posting dates 2024-12-26..2025-12-25.
- Entrance fee received in window: 0.00.
- Factor "IL payments counted" (independent_living_payments_on_annual_letter): a payment returned in the window → "net of the returned payments and net of the returned-payment fees" → (12 × 4325.12 + 4360.12) − 4325.12 − 35.00 = 51901.44 → × 38.5% = 19982.0544.
- Factors on Respite and Short-Term Stay records: credits (care_stay_credits_on_annual_letter) early-departure credit in window → 5572.00 − 796.00 = 4776.00; borne (care_stay_charges_borne_on_annual_letter) insurer paid → 4776.00 − 2075.00 = 2701.00; share (care_stay_medical_share) recovery nights → 1.0 → 2701.00; add-on (stay_add_on_medical_share) medication setup → 1.0 × 85.00 = 85.00.
- Amount: 0 + 19982.0544 + 2701.00 + 85.00 = 22768.0544 → **22768.05**.

**(c) closing-year tax letter for 2026 (issue_closing_year_tax_letter_050bd78c)**
- Closing year: entries 1–12 whole months before 2027-01-25 → 2025-12-26..2026-12-25.
- Computation document (closing_year_letter_amount): entrance fee received in the closing year (0) × 34.6% + IL payments in the closing year (9080.00) × 38.5% → **fall-back 3495.80**.
- Factor "entrance fee amount" (closing_year_entrance_fee_amount): death after occupancy, termination 2026-01-20 in the closing year → "administrative retention and the amortization entries posted in the closing year" → only month 24's 191.73 (retention 2024 and month 23 dated 2025-12-20 fall outside) → × 34.6% = 66.33858.
- Factor "IL amount" (closing_year_independent_living_amount): proration credit in the closing year → monthly fee charges 9080.00 − 4053.57 = 5026.43.
- Factor "post-residency deduction" (post_residency_fee_deduction): residency ended on death → post-death fee days of One-Bedroom = 14 (docs/independent notice_and_statement_periods: "Independent Living One-Bedroom | 30 | 7 | 14 | 30") × 4540.00/30 = 2118.67 → 5026.43 − 2118.67 = 2907.76 × 38.5% = 1119.4876.
- Factors on stay records: charges borne in the closing year (closing_year_care_stay_charges_borne) insurer paid 1279.00 → 3980.00 − 1279.00 = 2701.00; share (closing_year_care_stay_share) recovery nights → 1.0 → 2701.00. (No closing-year add-on rule is visible; the add-on share document speaks of the annual letter's window only.)
- Amount: 66.33858 + 1119.4876 + 2701.00 = 3886.82618 → **3886.83**.

**(d) estate refund (release_estate_refund_4b5e42b1)**
- Computation document (estate_refund_amount): refundable amount = received − every out entry, as the ledger stands at payment → 143800.00 − 191.73 = 143608.27. **Fall-back: 143608.27** (or 143800.00 if the amortization were skipped).
- Factors on the late payment (due 2026-03-21, paid 2027-01-25): campus rate (campus_statutory_delay_interest_rate) Brookfield 8.0; outstanding step (long_outstanding_refund_step) 310 days → 0.5 → 8.5; start (delay_interest_start_date) letters 2026-12-28 = 282 days after the due date → "180 or more days ... from 10 days after the letters were received" → 2027-01-07 → 18 days run; inclusion (delay_interest_day_inclusion) estate, letters after due date → +1 → 19; day count (delay_interest_day_count_by_campus) Brookfield "/365": 143608.27 × 8.5% × 19/365 = 635.4174 → 635.42.
- **refund_amount = 143608.27 + 635.42 = 144243.69.**

### Item 5 — executable sequence
1. `find_customers` (name "Raymond Ellis Whitfield") → `e462fa1d-...`; `verify_customer_identity` (customer_id, date_of_birth "1937-09-14", ssn_last4 "7861").
2. Lookups as in item 3.
3. agent unlock + call `book_final_period_amortization_cad149c9` {entrance_agreement_id "ea7a091e-791d-4d44-9d64-cd344fe3adc5", amortization_month 24, month_start_date "2026-01-20", amortization_amount 191.73} → balance 143608.27.
4. agent unlock + call `issue_annual_tax_letter_ce10c97a` {entrance_agreement_id, tax_year "2025", medical_expense_amount 22768.05} (independent of step 3; may precede it).
5. agent unlock + call `issue_closing_year_tax_letter_050bd78c` {entrance_agreement_id, tax_year "2026", medical_expense_amount 3886.83} — after 3 and 4.
6. agent `unlock_user_discoverable_tool("release_estate_refund_4b5e42b1")`; user calls {entrance_agreement_id, refund_amount 144243.69} → check number; agreement closed; balance −635.42.
- Terminal: month-24 amortization entry, 2025 and 2026 tax letters, refund payment entry, agreement closed.

### Item 6 — problem tree from the visible materials alone
- **P_root: estate refund release.** Visible prerequisite sentences (estate_refund_release, "Conditions of release"): "An estate refund is not released until the agreement's ledger carries an amortization entry for every month of occupancy that began on or before the termination date." and "An estate refund is released only after the agreement's ledger carries the tax letter for the tax year in which the agreement terminated." Records: month 24 began 2026-01-20 with no entry; no tax letter for 2026.
- **Hop P_root ← P_A (amortization of the month left open): state-derived.** The state words "amortization entry ... month of occupancy that began on or before the termination date" lead to amortization_after_termination ("a month of occupancy that began on or before the termination date and carries no amortization entry when the agreement terminates is amortized after the termination, once, whatever status the agreement has reached"), whose tool books it.
- **Hop P_root ← P_C (closing-year tax letter): state-derived.** "tax letter for the tax year in which the agreement terminated" leads to closing_year_tax_letter_issue ("The tax year in which an Entrance Fee Agreement ended receives one closing-year letter").
- **Hop P_C ← P_A: state-derived.** P_C's own sentence: "The tax letter for the year in which an agreement terminated is issued only after the agreement's ledger carries an amortization entry for every month of occupancy that began on or before the termination date."
- **Hop P_C ← P_B (annual letter for 2025): state-derived.** P_C's own sentence: "... is not issued until the agreement's ledger carries a tax letter for every earlier tax year in which entrance fee or independent living monthly fees were paid." Records: IL monthly fees paid throughout 2025, no 2025 letter. annual_tax_letter_issue: "a letter the January run missed is issued with the next January run"; year covered = year after the latest letter (2024) → 2025.
- Order: P_A and P_B (either order; P_A also feeds P_C's entrance-fee amount and P_root's balance) → P_C → P_root. Four problems; the root is the customer's own write.
- No hop was pre-solved: none of the blocked documents names another problem's tool, a route or an aggregated chain; each depended-on document was reached through the state words of the sentence and the ledger.

### Two-way counter-proof
- Alternatives excluded: (i) release the refund at the current balance (143800.00) — excluded by both release conditions; (ii) issue only the 2026 letter — excluded by P_C's earlier-years sentence and the missing 2025 letter; (iii) final amortization at the full 5752.00 (retired clause "a month that starts on or before the termination date is amortized in full", marked "no longer in force") or at the plan 2.0 — excluded by the three factor documents; (iv) day count to the vacate date (2026-02-02) — excluded by "Apartment vacated before the termination date | Yes" being false; (v) ordinary 1–12 month window for the 2025 letter — excluded by the missed-run tier (24 months since 2025-01-24); (vi) delay interest from the due date (310 days) — excluded by the start ladder (letters 282 days late); (vii) /360 or monthly day count — campus is Brookfield ("/365"); (viii) payee/address — estate, check, address on file (tool fixes it).
- "Do only the one thing asked": handing over the release now is excluded by the two visible release conditions and the ledger (no month-24 entry, no 2026 letter); issuing the 2026 letter directly is excluded by its own conditions.
- Fall-back numbers definite and different: 5752.00 vs 191.73; 3495.80 vs 22768.05; 3495.80 vs 3886.83; 143608.27 vs 144243.69.
- Factor findability: each was reached through record kinds — the amortization entry count and latest posting date, the IL residency's vacate date / termination reason / apartment type / monthly fee, the IL ledger's returned payment, returned-payment fee, proration credit, the respite ledger's stay type, early-departure credit, insurer payments and add-on codes, the agreement's campus, due date, payee and estate documents date. The post-death fee days figure had to be fetched from docs/independent (named by the entrance document as "the figures the Independent Living Residency Agreement terms set for that apartment type").
- Reading risks recorded: the closing-year entrance-fee sentence "the administrative retention and the amortization entries posted in the closing year" is read with "posted in the closing year" governing both (its examples support this; irrelevant here since the retention is dated 2024); the "date of death itself is counted as a day" read as +1 (the document's example 39 → 10 supports it).

contamination_disclosure: none. No scored value was in the brief; no source-layer file was opened before this freeze.

## gt_comparison
- Reveal: after both blind answers were on disk; freeze hashes recorded at 2026-10-05T11:00:04Z — task_1.md `9812387091d06bb1a37d927f82ad6083e6adadb2a62770824cea48c6dfe1018e`. (The freeze time written in the declaration, 11:05Z, was an estimate; the hash record time 11:00:04Z is authoritative, and no source-layer file was opened before it.) Revealed: `entrance.extended.yaml`, `task_tools.py`, `tasks/1.json`.
- Item 2: SAME — act now: three agent writes, then the representative's release.
- Item 3: SAME — customer `e462fa1d-...`, agreement `ea7a091e-...`, paired IL residency `d6472373-...`; same row inclusions (2025 IL payments with the returned payment and fee; 2026 charges with the proration credit; both recovery stays split by window).
- Item 4a amortization: SAME — GT 191.73 (month 24, month_start_date 2026-01-20); tiers SAME (18–35 → 1.5; surrender 0.5 at 13 days; death count end +1 → 2 days; share 2/30); GT baseline_result 5752.0 = blind fall-back.
- Item 4b annual letter: SAME — GT tax_year "2025", 22768.05; tiers SAME (missed-run window, returned-payment netting 51901.44, recovery share 1.0, early-departure netting 4776.00, insurer netting 2701.00, medication add-on 85.00); GT baseline_result 3495.8 = blind fall-back.
- Item 4c closing-year letter: SAME — GT tax_year "2026", 3886.83; GT baseline_result 3495.8 = blind fall-back.
- Item 4d estate refund: SAME — GT 144243.69; GT baseline_result 143608.27 = blind fall-back.
- Item 5: SAME — GT order book_final_period_amortization → issue_annual_tax_letter → issue_closing_year_tax_letter → unlock_user_discoverable_tool(release_estate_refund_4b5e42b1) → user call {entrance_agreement_id, refund_amount 144243.69}. The blind answer allowed steps 3/4 in either order; GT's prerequisite_closure has no edge between final amortization and the annual letter, consistent with that.
- Item 6: SAME — GT edges: release → final amortization (state), release → closing-year letter (state), closing-year letter → final amortization (state), closing-year letter → annual letter (state); policy_source sentences identical to the four visible sentences quoted in the blind answer. All four blind hops marked state-derived; none pre-solved.
- contamination_disclosure: none.
- Verdict: **PASS** (KB-RUNTIME).
