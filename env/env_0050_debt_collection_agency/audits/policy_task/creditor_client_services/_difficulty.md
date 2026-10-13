# Policy-task audit — creditor_client_services / charter-global

## charter_global_frozen

- Freeze time: 2026-10-10T18:15Z (wall clock of the audit host). Revision: r1. Auditor: an independent erl-task-policy-audit subagent (Claude Opus 5.5). It did not write any of the audited artifacts.
- Shared inputs and their hashes (re-hashed on disk and equal to the brief's values):
  - `tasks/creditor_client_services/client.extended.yaml` sha256 `a331a76e594589151d4c12496fa34c02d932206116aa54465cc90c8ca0d05345`
  - `tasks/creditor_client_services/task_tools.py` sha256 `6740437454a7c9d269923fd9340aa17fee91639f883b4721632f389a55f3a860`
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/client.yaml` (plus `legal.yaml` and `flatfee.yaml`, read only for the cross-category parameters and rules the extended policies cite), `blueprint/share_tools.py` (client/legal/flatfee finders, identity verification), the extended charter, the task tool module, and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (this gives the meaning of `within_months`, `MONTHS`, `DAYS`, `XCOUNT`, `CFIELD`).
- Masked and not read when this section was written: every `tasks/creditor_client_services/tasks/*.json` field outside the coordinator's views, meaning `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure` and the closure fields. Also not read: `worklog.md`, any sibling difficulty's audits or tasks, and any other scenario.
- Entry conditions (Step 0) were all supplied. The gate snapshot `/tmp/env0050_views/gates/env0050_creditor_client_services_gates.txt` shows EXTENDED, TASK TOOL CONTRACT, REPLAY (0.json 63/63, 1.json 92/92), SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK. check_traceability is deferred because the KB is unpublished. The masked views and their sha256 values match the brief.
- Nothing in this section comes from a revealed GT. It was written before any task's GT was opened.

### policy_conflict_scan

- **Base copy.** Lines 1–1215 of the extended charter equal `blueprint/products/client.yaml` byte for byte, ignoring one trailing newline (`diff` after stripping trailing whitespace shows only the extra blank line). The base section is therefore verbatim.
- **Extended policies (4) and their writes:**

  | policy | trigger | subject | target_tool (owner) | computes | prerequisite |
  |---|---|---|---|---|---|
  | client_ext_early_termination_charge | state_due | client_early_termination_fee_assessed | book_early_termination_charge_4cc8362c (agent) | charge_amount | [] |
  | client_ext_closing_settlement_payment | on_request | client_fee_payment_received | pay_closing_fee_settlement_180c3708 (user) | payment_amount | early_termination_charge (value_input, state) |
  | client_ext_invoice_late_charge | state_due | client_late_charge_assessed | assess_invoice_late_charge_7a6464d6 (agent) | late_charge_amount | [] |
  | client_ext_past_due_invoice_payoff | on_request | client_fee_payment_received | pay_past_due_invoice_8492adb5 (user) | payment_amount | invoice_late_charge (value_input, state) |

- **Overlapping subjects.** `client_fee_payment_received` is the subject of two extended policies and of base `client_evt_fee_billing`.
  - The two extended triggers are disjoint on their stated objects. The closing payment covers "the fees it owes on that agreement" for a client "that has given termination notice". The payoff covers "a past-due fee invoice that is accruing late charges" that the client names.
  - The charter does not say which governs when a client with a termination notice on record names a single past-due invoice. That is a domain overlap. It is an observation only: neither task's world contains that situation. In task 0 the persona refuses to name an invoice, and in task 1 there is no termination notice.
- **Triggers and state_due cross-fire on each world** (this is a world fact; each task's file demonstrates it):
  - The late-charge policy is state_due on every agreement with an invoice past its late-charge start.
  - The early-termination charge is state_due on every agreement with a termination notice on record.
  - Neither fires outside its own task: task 0 has no invoice past its late-charge start at frozen_time, and task 1 has no termination notice.
- **Eligibility, time anchors and terminal states.**
  - The base eligibility gates that bear on these four writes are inherited unchanged: the late-charge start, the notice on record, and the runoff gates (runoff is not reached in either world).
  - The termination effective date is the same in base and extended: the later of notice + termination_notice_days and the named date.
  - Terminal states: ETC raises fees_receivable; the late charge raises fees_receivable; both payments lower fees_receivable. No status transition is scored.
- **Cross-category read boundaries.**
  - ETC reads legal (status, legal_suit_filed rows) and flatfee (status, flatfee_conversion_requested rows).
  - Closing reads legal (status, cost_advance_balance).
  - Late charge reads flatfee (purchase_date, paid_date, invoice_due_days) and legal (status, cost_deposit_balance, cost_deposit_minimum_balance_usd).
  - Payoff reads legal (legal_suit_filed rows).
  - All are read-only branch or history reads. Every write lands in client tables.
- **Scope exclusivity and completeness.**
  - The prerequisite graph has exactly two components: {ETC → closing} and {late charge → payoff}.
  - The personas raise "settle everything owed on the agreement after a termination notice" (view 0) and "pay off invoice OV-526061" (view 1). The two trees are therefore disjoint and together cover all four extended policies.
  - The authoritative `charter_scope` is masked here. It is compared at reveal in each task file.

### rule_compute_equivalence

Check 2 was run over all four policies. Each line pairs a `compute` binding with its `compute_basis` quotation and the rule sentence.

**client_ext_early_termination_charge**
- Termination effective date: `notice_to_effective_days = MX(required_notice_days, named_notice_days)` implements "the later of the notice date plus the tier's termination_notice_days calendar days and the date the client names in its notice". Equivalent.
- `unexpired_days = DAYS(notice_date, term_end) − notice_to_effective_days` equals DAYS(effective termination date, term end), which is "counted in calendar days from the termination effective date to the end of the initial term". `initial_term_days = DAYS(effective_date, term_end_date)`. Both use the difference convention B − A. That is the same convention the base charter states wherever it counts days ("the day after X being day one and the last day included").
- Proration ladder: the three tiers in the rule ("no more than half … 24 or more … whole months, each complete 30 calendar days … divided by initial_term_months"; "… under 24 … unexpired days / length in days"; "more than half … in full") equal the `prorated_charge` ternary.
- Legal, notice-lead, pre-collect and goodwill ladders: each tier sentence is quoted in compute_basis and implemented. The share arithmetic, "added into one reduction share … multiplied by a goodwill share … reduced once", equals `reduction_share` and `result`. "nothing when it takes effect on or after that end" equals `… if unexpired_days > 0 else 0`. "rounded to the cent" is `RND(…,2)`.
- Gap, observation: the rule restricts suits to those "filed under that legal agreement" and conversions to "its debtors" (the program naming this contingency agreement). `XCOUNT` is scoped to the customer, not to that legal agreement or program.
  - Legal allows one live agreement per client (`legal_agg_multi_holding` max_per_customer 1), but a terminated earlier agreement's suits would still be counted.
  - Flatfee allows several programs (max_per_customer null), so another program's conversions would be counted.
  - Neither task world holds a second legal agreement or a second program, so this costs no task anything.
- Gap, observation: "The end of the initial term is the agreement's term end date while the agreement has not renewed." No compute binding tests renewal. After a renewal, compute would read the renewed term_end_date. That is an empty promise on renewed agreements, and neither world is renewed.

**client_ext_closing_settlement_payment**
- `fees_owed = F('fees_receivable')` implements "the agreement's fees owed to Ridgeline on the day the payment is made".
- `termination_charge = SUM(ETC entries)` implements "the early-termination charge booked on the agreement".
- `open_invoiced = MX(0, invoiced − payments − credits)` implements "the fee invoices booked on the agreement less every fee payment and every fee credit booked on it, and never less than zero". This is verbatim, including payments that settled late charges.
- Reserves:
  - `returns_6m` (within_months=6, reversal_reason payment_returned) and `recent_collections` (within_months=1, client_collection_booked) implement "all of the collections booked in the month before the payment where 3 or more collections were reversed as returned payments in the 6 months before the payment, half … 1 or 2 …, nothing where none".
  - `legal_reserve_share` implements the active/suspended/advance > 0 ladder.
  - `trust_available = MX(0, …)` implements "never less than zero".
- `trust_met` implements the three-way remittance method.
- `prompt_share` uses `DAYS(notice_received, NOW)` against 10 and 30, matching "no more than 10 … more than 10 but no more than 30 …".
- `waiver_share` implements "exactly one … in full, exactly two … by half, otherwise not at all".
- `result = RND(MX(0, fees_owed − trust_met − prompt_discount − late_waiver), 2)` implements "all taken off the same fees owed, never less than zero and rounded to the cent once at the end".
- No compute basis is invented and no rule promise is left unimplemented. The closing sentence "The amount met from trust is settled from the trust balance when the closing statement is drawn, and the discount and waiver are cleared by credit on that statement" describes a later back-office statement. It drives no binding and no tool of this difficulty.

**client_ext_invoice_late_charge**
- Unpaid amount: `unpaid_amount = MX(0, invoice − paid − credited)` per invoice_number. Verbatim.
- Base-rate ladder: `pack_paid_days = DAYS(purchase, paid) ≤ CPARAM(flatfee, invoice_due_days)` and `pack_age = MONTHS(purchase, NOW) ≥ 12` implement "paid … within the pack's invoice_due_days after purchase and the pack was bought 12 or more months before the handling date".
- Aging ladder (`DAYS(invoice_date, NOW)` against 150 and 100) and minimum-combination ladder ("late charges booked on the agreement's other invoices in the 12 months before the handling date", where `other_late_12m` is the total minus the same invoice's count) are both verbatim.
- Part-payment ladder (`invoice_paid / invoice_amount` against 0.5 and 0.25), tenure ladder (`MONTHS(effective_date, NOW)` against 36 and 18) and legal standing ladder (status and `cost_deposit_balance` against `CPARAM(legal, cost_deposit_minimum_balance_usd)`) are all verbatim.
- "first added into one share … reduced once … rounded to the cent once at the end" equals `result`.
- Compute-only selector, observation: `lc_invoice` picks the invoice by the latest late charge already on the ledger. The rule's object is "a past-due fee invoice" that has reached its month. The two agree only where the invoice now due is the one carrying the latest prior late charge. That holds in task 1 (see 1.md).
- Compute-only selector, observation: `CFIELD('flatfee','purchase_date')` carries no agreement filter. The rule's "its flat-fee pre-collect pack invoice" is singular. Both worlds hold one program, so there is no consequence.

**client_ext_past_due_invoice_payoff**
- `payoff_unpaid` is verbatim.
- `late_entering` implements the three-tier inclusion ladder ("no more than 10 calendar days after the invoice's most recent late charge and … 3 or fewer … only that most recent …; … more than 3 … only those in the 3 months before …; otherwise every late charge").
- Concessions are verbatim: fee payments in 6 months (≥4 / 1–3 / 0), suits in 12 months (≥3 / 1–2 / 0), collections in 3 months (≥10000 / ≥4000 / otherwise), returned-payment reversals in 3 months (≥2 / 1 / 0).
- `concession_share = MN(1, Σ)` implements "never more than the whole". `result = RND(unpaid + late_entering × (1 − share), 2)` implements "the unpaid amount itself is never reduced … rounded … once at the end".
- Selector observation: `payoff_invoice` is the latest late charge's invoice. The rule's object is the invoice the client names. Same caveat as above.

**DSL window semantics** (check_compute `_within`): a row is inside `within_months = n` iff `0 ≤ MONTHS(row_date, NOW) < n`, with MONTHS counted in whole months and the day of month compared. This is how "in the N months before the handling date / payment" is read throughout. Both task files use it.

**Rounding**, observation: `RND` is Python `round` on a float, while the tool contracts say "rounded half-up". The two differ only on exact half-cent ties. No gold candidate in either task sits on a tie. Two baseline-substitution figures in task 1 do (see 1.md factor_weight).

Conclusion: rule and compute are equivalent in both directions on all four policies. There is no SOURCE-POLICY RED. The four gaps above are observations with no task consequence.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are 4cc8362c/charge_amount, 180c3708/payment_amount, 7a6464d6/late_charge_amount and 8492adb5/payment_amount. Each is claimed by exactly one policy.
- Tool bodies (`task_tools.py`): each body performs one `ctx.create("client_ledger", …)` and one `ctx.update("client_agreements", …, fees_receivable=…)`.
  - No body reads another ledger row type, tests a status, compares a date or rejects a call. There is no prerequisite validation and no hint.
  - The module docstring states: "No tool checks eligibility, prerequisites or amounts".
- Docstrings:
  - No docstring names another tool or states a position in a sequence.
  - The only ordering-like words are "rounded half-up to 2 decimal places before it is passed" (argument formatting) and the receipt field `fees_owed_after` (a balance after this booking). Neither orders business actions.
  - `pay_closing_fee_settlement_180c3708` says "on a contingency placement agreement for which it has given termination notice". That describes the object, not an order relative to the ETC booking.
- Owners: two agent writes (ETC, late charge) and two user writes (closing payment, invoice payoff). This matches the charter ("which the client makes itself" in both payment rules).
- uuid8s: `4cc8362c`, `180c3708`, `7a6464d6`, `8492adb5`. There is no shared prefix or suffix, no sequential or adjacent values, and no tail-modified copies. Each is consistent with independent generation.
- Pass.

### prerequisite_graph

Check 7 results:

- `prerequisite` is filled in on all four extended policies: [] / 1 edge / [] / 1 edge. Each `problem` points at an extended policy id in this file, never at a base policy and never at the policy itself. The graph is two disjoint edges and is acyclic.
- Edge closing → client_ext_early_termination_charge:
  - kind value_input, gate `termination_charge`. That is an existing binding of the closing compute, feeding `prompt_discount`. The edge also moves `fees_owed` through the booked amount.
  - form state, no fallback_reason (correct for state form).
  - `policy_source` "The closing settlement payment is worked out only after the agreement's fees owed carry the early-termination charge due for the termination notice on record." This is sentence 2 of the closing rule, verbatim.
  - `resolved_by` book_early_termination_charge_4cc8362c is the ETC policy's target_tool. Its body adds a client_early_termination_fee_assessed entry and raises fees_receivable, which is exactly the `effect`.
  - `condition` ("carries an early-termination charge entry dated the request date of the termination notice on record, booked at the figure the early-termination charge rule gives, and the agreement's fees owed include it") is the state that "fees owed carry the early-termination charge due for the termination notice on record" names. It is neither strengthened nor weakened: "due" carries "at the figure the rule gives".
- Edge payoff → client_ext_invoice_late_charge:
  - kind value_input, gate `late_entering`. That is an existing binding of the payoff compute.
  - form state, no fallback_reason.
  - `policy_source` "A payoff figure for a past-due invoice is not quoted until the invoice carries a late charge for every full calendar month it has stayed unpaid after its late-charge start." This is sentence 2 of the payoff rule, verbatim.
  - `resolved_by` assess_invoice_late_charge_7a6464d6 is the late-charge policy's target_tool. Its body adds a late-charge entry tied to the invoice, dated today, which is exactly the `effect`.
  - `condition` restates the sentence with the late-charge start spelled out from base (invoice date + due days + grace days). Same strength.
- No `condition`, `effect` or `policy_source` carries authoring-viewpoint phrasing ("this task", "the opening", "the current world").
- Pass.

### prerequisite_sentences

Check 6 results:

- **Closing edge, four-point test.**
  1. "only after" is an ordering connective joining the policy's own result ("the closing settlement payment is worked out") to what it waits on.
  2. What it waits on is a record-visible state in record words: the agreement's fees owed (`fees_receivable`) carrying the early-termination charge (`client_early_termination_fee_assessed` entry). No action, performer or tool is named.
  3. No tool name, policy id, snake_case token or row id.
  4. Strength: "the early-termination charge due for the termination notice on record" is one charge, the one the notice makes due. The condition says the same.
- **Exactly one write brings that state about:** book_early_termination_charge_4cc8362c. No other tool of this module, and no shared tool, creates an early-termination entry.
- **Derivation the reader performs.**
  1. The closing rule waits on "fees owed carry the early-termination charge due for the termination notice on record".
  2. The records show a termination_notice service request and no early-termination entry.
  3. The ETC policy's own rule says "The early-termination charge owed for a termination notice on record is figured … and booked on the date the notice was received".
  4. So the agent books that charge with the ETC tool, then works out the closing payment.
  - There is a single reading. The waited-on object is named by kind (the ETC charge) and tied to the notice on record.
- **Payoff edge, four-point test.**
  1. "not … until" is an ordering connective joined to the policy's own result ("A payoff figure … is not quoted").
  2. The state is in record words: the invoice carrying a late charge for every full calendar month since its late-charge start (late-charge entries with that invoice_number). The late-charge start is defined in base `client_evt_fee_billing`.
  3. No tool name, id or snake_case token.
  4. Strength equals the condition.
- **Exactly one write brings it about:** assess_invoice_late_charge_7a6464d6.
- **Derivation the reader performs.**
  1. The payoff waits on one late charge per full month since the late-charge start.
  2. Count the months from invoice date + fee_invoice_due_days + late_charge_grace_days to the handling date.
  3. Compare with the invoice's late-charge entries.
  4. The late-charge rule ("Each monthly late charge on a past-due fee invoice is figured as set out in this rule, one charge for each full calendar month …") gives the missing month's figure.
  5. The agent books it with the late-charge tool, then quotes the payoff.
- **Reading caveat, observation.** "full calendar month" admits a calendar-month reading. Under it, months run 1st to last day, so the first full calendar month after a mid-month start ends at that month's end. The anniversary reading has months run start-day to start-day.
  - The ledger's own precedent settles it. Every seeded late charge in both worlds is dated exactly one month after its invoice's late-charge start: task 1 has 2025-10-15, 2026-01-16, 2026-05-14 and 2026-09-16, against starts on 2025-09-15, 2025-12-16, 2026-04-14 and 2026-08-16.
  - Each task file states what the reading costs its world.
- **No second wording.** Neither blocked rule restates its dependency in other words.
  - The closing rule's later "A prompt-settlement discount is taken off the early-termination charge booked on the agreement" uses the charge as an input. It is not a second ordering statement.
  - The payoff rule's "no more than 10 calendar days after the invoice's most recent late charge" is likewise an input.
- **Depended-on rules stay silent.** Neither the ETC rule nor the late-charge rule mentions the closing payment or the payoff.
- **No undeclared cross-problem order.**
  - The extended rules state no order between two writes of this difficulty beyond the two declared sentences.
  - Base sentences that order business events (for example "A fees_past_due hold is lifted when every invoice past its due date is paid or credited" in `client_evt_placement_hold`) ground no edge. They concern writes that have no tool in this difficulty. Observation only.
- **The state form is used on both edges.** No fallback needs testing.
- Pass.

### override_declarations

Check 1, findings half. Each base policy each extended policy cites was swept sentence by sentence.

**client_ext_early_termination_charge vs `client_evt_termination_and_renewal`**
- "An agreement renews automatically …": followed. Not a quantity of this write.
- "The client may instead terminate … the later of the notice date plus that notice period and the date the client names.": followed verbatim.
- "Notices are given only by the client through a termination_notice or nonrenewal_notice service request.": followed ("a termination notice on record").
- "A termination that takes effect before the end of the initial term carries the early_termination_fee_usd, charged on the date the notice was received": **handled differently** (proration and reductions). This is **declared** in `overwrite` (superseded_clause verbatim, replaced_by verbatim in the rule).
- "non-renewal at a term end and any termination after the initial term carry no fee": followed ("nothing when it takes effect on or after that end").
- The runoff and closing sentences are not quantities of this write.
- Merged semantics are unique: the extended rule fully defines the charge.

**client_ext_closing_settlement_payment vs `client_evt_fee_billing`, `client_evt_termination_and_renewal`, `client_evt_remittance`**
- fee_billing:
  - Invoicing cadence and minimum monthly fee: not this write.
  - "Fee payments are applied to the invoice the client names, and otherwise to the oldest unpaid invoice first.": compatible. The closing payment settles the whole agreement, and the tool carries no invoice.
  - The offset sentence is **handled differently** and **declared** (superseded verbatim; replaced_by "on a gross_remit agreement whose tier has fees_offset_against_remittance true, the available trust balance is set against the open invoiced fees, whether or not they are past due …" is verbatim in the rule).
  - The dispute-credit sentence: not this write.
- termination_and_renewal: the notice sentence is followed. The runoff/remit sentence ("accounts already placed keep being worked and remitted for runoff_days") concerns future periods and is not overridden for the scored quantity.
- remittance:
  - "For a net_remit agreement the period's fees are first retained from trust and the rest is remitted; for a gross_remit agreement the whole period's collections are remitted and the fees are invoiced." For gross_remit, the trust-against-fees use is exactly the declared offset replacement.
  - For **net_remit**, the closing rule sets the available trust balance "against the whole of the fees owed", which includes early-termination, recall and late charges. Base retains only "the period's fees" from trust. That net_remit deviation is **not named** in `overwrite`.
  - Observation: neither task world is net_remit (task 0 is gross_remit), so no scored value moves.
- "Only cleared funds are remitted: collections received in the last funds_clearance_holdback_business_days business days of a period roll into the next period." The closing rule defines "available trust balance" exhaustively as "the trust balance held less two reserves", so the holdback is not a competing reading of that quantity. Each task file records whether this matters on its world.
- Anonymous-intermediate, 0/1-multiplier and dropped-branch shapes: none found. The `trust_met` ladder's "on any other agreement nothing is met from trust" is the base-consistent default for gross_remit tiers without offset.

**client_ext_invoice_late_charge vs `client_evt_fee_billing`**
- "A late charge accrues on an unpaid invoice only when the handling date is later than the late-charge start counted from the invoice date.": followed.
- "The late-charge start is the invoice date plus fee_invoice_due_days calendar days plus late_charge_grace_days calendar days;": followed.
- "from then a charge of late_charge_pct_per_month percent of the unpaid invoice amount, and at least late_charge_minimum_usd, accrues once for each full calendar month the invoice stays unpaid.": **handled differently** (rate ladders, minimum combination, reliefs). This is **declared** (superseded verbatim; replaced_by verbatim).
- The rest of fee_billing (application of payments, offsets, disputes) is not this write.
- The base eligibility block's `counting_rule` still quotes the superseded clause. That is a base copy and may not be edited, and the declared overwrite governs.

**client_ext_past_due_invoice_payoff vs `client_evt_fee_billing`** (`overwrite: []`)
- Base defines no payoff figure.
- "Fee payments are applied to the invoice the client names": followed (the tool carries the named invoice).
- No base sentence governs the amount of a single-invoice payoff, so reducing the late charges that enter the payoff deviates from no base sentence on the scored quantity. Late charges that do not enter stay in fees owed: nothing in the extended rule credits them away, and base says nothing to the contrary.
- `overwrite: []` holds on the same sentence-by-sentence standard.

Conclusion: every base/extended conflict on a scored quantity is declared. One undeclared net_remit deviation is recorded as an observation because no task world is net_remit.

### factor_ladders

Structure only. Whether each factor bears weight is in each task's `factor_weight`.

**client_ext_early_termination_charge**: 5 factors (method 1, parameter 4). Bindings are disjoint and every `decides` is an input, not `result`.

| factor | effect | tiers | multi-source | cross_difficulty | rule states all tiers | compute implements | distinct outcomes |
|---|---|---|---|---|---|---|---|
| unexpired_term_proration | method (whole-month pro rata / day pro rata / full) | 3 | yes (unexpired vs half term AND tier initial_term_months) | – | yes | yes | yes |
| legal_forwarding_reduction | parameter 40/20/0 % | 3 | yes (legal_agreements.status AND legal_matter_events suit count) | legal | yes | yes | yes |
| notice_lead_reduction | parameter 10/5/0 % | 3 | no | – | yes | yes | yes |
| precollect_conversion_reduction | parameter 10/5/0 % | 3 | yes (flatfee_programs.status AND flatfee_unit_ledger conversion count) | flatfee | yes | yes | yes |
| late_charge_goodwill | parameter 0 / 0.5 / 1 kept | 3 | no | – | yes | yes | yes |

- Labels are honest: the proration tiers change the algorithm, and the others change a share.
- Fall-through tiers equal `baseline.rule`, which is the full fee and no reduction.
- Realism: proration of an early-termination fee by unexpired term, credit for longer notice, relationship credit for other live business, and withholding goodwill from late payers are all treatments a collection agency's client contract plausibly carries.

**client_ext_closing_settlement_payment**: 5 factors (method 1, parameter 4).

| factor | effect | tiers | multi-source | cross_difficulty | rule | compute | distinct |
|---|---|---|---|---|---|---|---|
| trust_offset_method | method (against whole fees / against open invoiced, capped / nothing) | 3 | yes (remittance_basis AND tier fees_offset flag) | – | yes | yes | yes |
| returned_payment_reserve | parameter 1 / 0.5 / 0 | 3 | no | – | yes | yes | yes |
| legal_cost_reserve | parameter 1 / 0.5 / 0 | 3 | yes (status AND cost_advance_balance > 0) | legal | yes | yes | yes |
| prompt_settlement_discount | parameter 10/5/0 % | 3 | no | – | yes | yes | yes |
| closing_late_charge_waiver | parameter 1 / 0.5 / 0 | 3 | no | – | yes | yes | yes |

- The baseline ("fees owed … on the day the payment is made") is self-sufficient, and every fall-through equals it (nothing from trust, no reserve, no discount, no waiver).
- Realism: holding back recent collections against returns, and the agency's unreimbursed court costs against trust, are standard trust-accounting reserves. Prompt-payment discounts and a goodwill waiver of an isolated late charge are ordinary settlement concessions.
- The waiver fall-through ("otherwise" means 0 or 3 or more late charges) selects 0, which differs from 1 and 0.5.

**client_ext_invoice_late_charge**: 6 factors (method 1, parameter 5).

| factor | effect | tiers | multi-source | cross_difficulty | rule | compute | distinct |
|---|---|---|---|---|---|---|---|
| precollect_payment_rate | parameter (−0.50 / −0.25 / tier pct) | 3 | yes (paid within the pack's invoice_due_days AND pack age) | flatfee | yes | yes | yes |
| invoice_aging_step | parameter (+0.50 / +0.25 / 0) | 3 | no | – | yes | yes | yes |
| minimum_combination | method (pct + min / pct alone / max(pct, min)) | 3 | no | – | yes | yes | yes |
| part_payment_relief | parameter 25/10/0 % | 3 | no | – | yes | yes | yes |
| tenure_relief | parameter 15/5/0 % | 3 | no | – | yes | yes | yes |
| legal_standing_adjustment | parameter +10 % relief / −10 % surcharge / 0 | 3 | yes (status AND deposit vs programme minimum) | legal | yes | yes | yes |

- Labels are honest. `minimum_combination` changes how the percentage charge and the minimum are combined, which is an algorithm and not a number.
- The fall-through baseline ("late_charge_pct_per_month percent of the invoice's unpaid amount, and at least late_charge_minimum_usd") is the base's own formula.

**client_ext_past_due_invoice_payoff**: 5 factors (method 1, parameter 4).

| factor | effect | tiers | multi-source | cross_difficulty | rule | compute | distinct |
|---|---|---|---|---|---|---|---|
| late_charge_inclusion | method (latest only / last 3 months / all) | 3 | yes (recency of the latest late charge AND count of the invoice's late charges) | – | yes | yes | yes |
| payment_record_concession | parameter 50/25/0 % | 3 | no | – | yes | yes | yes |
| legal_volume_concession | parameter 25/10/0 % | 3 | no | legal | yes | yes | yes |
| collection_volume_concession | parameter 20/10/0 % | 3 | no | – | yes | yes | yes |
| returned_payment_concession | parameter 10/5/0 % | 3 | no | – | yes | yes | yes |

- The baseline (unpaid amount plus every late charge) is self-sufficient and equals the late_charge_inclusion fall-through.

**Per-task floors** (task scope inferred from the graph; confirmed at reveal):
- Task tree {ETC, closing}: multi-source factors are 5 (proration, legal_forwarding, precollect_conversion, trust_offset, legal_cost_reserve; the strongest is legal_forwarding_reduction, which reads two tables). Cross-difficulty factors are 3 (legal, flatfee, legal).
- Task tree {late charge, payoff}: multi-source factors are precollect_payment_rate, legal_standing_adjustment and late_charge_inclusion. Cross-difficulty factors are 3 (flatfee, legal, legal).
  - Observation: all three multi-source factors combine predicates over the fields of one record or one ledger family, plus a charter parameter. That meets the "distinct evidence" definition in `references/product_extended.yaml` ("the account's tier AND a count over a window"), but it is weaker than the two-table conjunction task 0 has.
- Cross-difficulty categories read: legal and flatfee.
  - Observation: `blueprint.yaml` claims only account, plan, settle, hardship and client under its five difficulties. legal and flatfee are the blueprint's surplus categories (C ≥ N + 2), so strictly they are another *product's* records rather than another *difficulty's*.
  - For a creditor-client customer, the only other holdings that can exist are legal and flatfee, because the consumer products cannot be held by a creditor.
  - The factors read these as another product line's seeded holdings and ledgers, which is the requirement's evident purpose. This is recorded, not red-lit.

Conclusion: the structure passes on all four policies.
- Each policy has 4 to 6 factors, at least 2 parameter and at least 1 method.
- Every ladder has 3 pairwise-disjoint tiers, all stated in the rule and in compute, with no two tiers sharing an outcome.
- Every fall-through equals the policy baseline.

### findings

The charter-global findings are listed below. Unless marked otherwise, none carries a demonstrated consequence on a task world, so all are observations.

1. **Observation, overlap.** Both payment policies share the subject `client_fee_payment_received` and have no precedence rule for a client with a termination notice on record who names one past-due invoice. Neither task's world contains that case. Bears on tasks 0 and 1 (each file confirms its persona avoids the overlap).
2. **Observation, rule/compute scope.** The ETC suit and conversion counts and the payoff suit count use customer-scoped `XCOUNT`, while the rules say "under that legal agreement" and "its debtors". The late charge's `CFIELD('flatfee', 'purchase_date')` carries no agreement filter. There is no consequence on either world (one legal agreement and one program each). Bears on tasks 0 and 1.
3. **Observation, rule/compute.** "while the agreement has not renewed" has no compute counterpart. No world is renewed. Bears on task 0.
4. **Observation, undeclared net_remit deviation.** The closing rule sets trust against "the whole of the fees owed" on net_remit agreements, against base `client_evt_remittance`, which retains only "the period's fees". This is not named in `overwrite`. Task 0 is gross_remit, so there is no consequence. Bears on task 0.
5. **Observation, reading of "full calendar month".** A calendar-month reading is possible. Ledger precedent fixes the anniversary reading. Task 1 states the cost of the alternative. Bears on task 1.
6. **Observation, compute-only object selectors.** `lc_invoice` and `payoff_invoice` are picked as the latest late charge's invoice, whereas the rule's object is the past-due invoice that has reached its month or the invoice the client names. They coincide on task 1's world. Bears on task 1.
7. **Observation, cross-difficulty definition.** legal and flatfee are claimed by no difficulty. Bears on tasks 0 and 1.
8. **Observation, rounding.** `RND` is Python float rounding, while the tools specify half-up. There are no gold ties. Bears on task 1 (two substitution figures sit on ties).

There is no charter-global SOURCE-POLICY RED.

## closing_checklist

Written after both reveals (2026-10-10T18:22:25Z). It sits outside the pre-reveal charter-global section above, which is unchanged: its sha256 before this append was `a61f5233043d6b4e01a23fa251cd3134c893410f8cefacd10674f5afdf597169`, mtime 18:19:29Z. The hand-written "18:15Z" freeze line above is an estimate; see the erratum in `0.md`.

**The difficulty is NOT closed.** Task 0 carries a SOURCE-FACTOR RED (`0.md` finding 0-F1), so Step 4's precondition that all four relationships PASS for every task fails.

Checklist status, item by item:
- **Audit files:** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, and this file sits alongside them. This is the first revision (r1), so there are no older revisions. Comparison sections: task 0 is SOURCE-FACTOR RED and task 1 is PASS.
- **Coverage and scopes:** the revealed `charter_scope` is {ETC, closing} for task 0 and {late charge, payoff} for task 1. The scopes are pairwise disjoint, span each whole tree, and jointly cover all four extended policies. Task tools and GT are closed: the GT writes are exactly each scope's two target tools. Each tool's uuid8 is independent. Holds.
- **Trees:** each tree has 1 prerequisite problem, 1 value_input edge and 1 `owner=user` problem (the root), with no cycle. The difficulty-wide prerequisite graph is two disjoint edges and acyclic. Holds.
- **Factors:**
  - Every computation declares a self-sufficient baseline and 5, 5, 6 or 5 factors, each with at least 2 parameter and 1 method.
  - Every task has at least 1 multi-source and at least 1 cross-category (legal or flatfee) factor.
  - Every ladder has three distinct tiers, all stated in its rule.
  - Every factor bears weight on its world, and every all-baseline figure differs from gold.
  - Holds structurally. It fails for task 0 on the authenticity of the seeded cross-category evidence (0-F1).
- **Gate re-run on the final form:** not performed. The artifacts are not final while 0-F1 stands. The gate snapshot supplied with the brief (all green) is the pre-audit state, and gates do not detect 0-F1.

## revision_2

### charter_global_frozen (r2)

- Freeze: written 2026-10-10 ≈20:16Z, before any r2 GT field, `tasks/*.json` or `tasks/creditor_client_services/worklog.md` was read. The authoritative order is the file mtimes, as in r1. Auditor: the same independent subagent as r1.
- r1 report state is preserved above, untouched. sha256 before this append: `_difficulty.md` `9a3a192a…d1d434`, `0.md` `7dfe3897…617617`, `1.md` `6ea7ff8c…d1fd`.
- Shared inputs changed, so the charter-global section is re-derived in full:
  - `client.extended.yaml` sha256 `7882eaf4907b339d959867114084d2c1cc56aace5359a3b8939f5914776e8ac7` (r1 `a331a76e…`)
  - `task_tools.py` sha256 `a95a21d3d97acba68b6854e12033732c8ef75e457f1861d6e7475c01b189e12a` (r1 `67404374…`)
- Entry conditions: the r2 gate snapshot `/tmp/env0050_views/gates/env0050_creditor_client_services_r2_gates.txt` is all OK (EXTENDED, TASK TOOL CONTRACT, REPLAY with 0.json 64/64 and 1.json 92/92, SOLVABILITY, COMPUTE, GROUNDING, SCOPE). The r2 view hashes match the brief.
- Masked fields are as in r1.
- Item ids: the reworker's D1–D8 are this file's r1 `### findings` items 1–8, in the same order.

### policy_conflict_scan (r2)

- Base copy: lines 1–1215 still equal `blueprint/products/client.yaml`, apart from the trailing newline. The blueprint files are unmodified (mtimes 2026-10-08).
- Extended policies, tools, owners, triggers and the prerequisite graph are unchanged from r1, so scope exclusivity and completeness are unchanged.
- **D1 (overlap) is closed.**
  - The closing rule now states: "Where a termination notice is on record, a payment of the fees owed on that agreement is a closing settlement payment even when the client names one of its invoices."
  - The payoff rule now opens: "… with one payment it makes itself, naming the invoice, on an agreement with no termination notice on record."
  - The two payment policies are now disjoint on a record-visible test: a termination notice is or is not on record.
  - Residual observation: "a payment of the fees owed on that agreement" does not say whether a single-invoice payment by a client under notice is itself recast as the whole closing balance. Neither world contains that case.
- New sentences add no cross-problem order: none states an order between two writes of this difficulty.

### rule_compute_equivalence (r2)

**New or changed sentences, each against compute:**

- **Window definition**, added to all four rules: "A window of a number of months before a date covers the dates after the same day that number of months earlier, up to and including that date."
  - The DSL `_within` keeps a row iff `0 ≤ MONTHS(d, NOW) < n`, with MONTHS reduced by 1 when NOW's day-of-month is below d's.
  - For d = NOW − n months on the same day, MONTHS = n, so it is excluded. The day after gives MONTHS = n − 1, so it is included. Future dates are negative, so they are excluded.
  - Equivalent, except where "the same day" does not exist in the earlier month (for example NOW = the 31st). The rule leaves that undefined. Observation; no world date hits it.
  - This closes the r1 "month before the payment" reading weighed in task 0 (0-O2): the window is now a defined trailing span.
- **ETC day-count**: "Each such count is the difference between the two dates in calendar days: the first date is not counted and the last date is counted." This equals `DAYS(a, b)` and closes the r1 day-count reading (0-O2).
- **ETC renewal (D3 closed)**: "The agreement has renewed when its term end date lies the tier's initial_term_months or more whole months after its effective date, and a termination of a renewed agreement takes effect after the initial term and carries no charge." This equals `renewed = MONTHS(effective, term_end) >= P('initial_term_months')` and `result = … if (unexpired_days > 0 and not renewed) else 0`. The sentence is also in `baseline.rule`.
  - Residual observation: the test reads the *current* tier's initial_term_months. After a tier change at review to a tier with a longer initial term (for example Standard 12 to Select Volume 24), a once-renewed agreement could test as not renewed. No world has a tier change.
  - The test also assumes term ends are seeded as the day before the anniversary, which is the seed convention in both worlds.
- **Scope of counts (D2 closed)**:
  - ETC `legal_suits_12m` now filters `legal_agreement_id = CFIELD('legal','legal_agreement_id', agreement_id=HID)`, which is "filed under that legal agreement".
  - `precollect_conversions_12m` filters `program_id = CFIELD('flatfee','program_id', agreement_id=HID)`, which is "its debtors".
  - Payoff `suits_12m` filters by the legal agreement naming this contingency agreement. The rule says "the client's legal forwarding agreement". A client holds at most one (`legal_agg_multi_holding`), so the two agree.
  - Late-charge `pack_bought`, `pack_paid` and `pack_due_days` now carry `agreement_id=HID`. The rule's "its flat-fee pre-collect pack" is singular, so this is consistent.
- **Full calendar month (D5 closed)**: added to the late-charge and payoff rules: "A full calendar month after a late-charge start runs from that day to the same day of the next month, or to that month's last day where the same day does not exist."
  - It fixes the anniversary reading. It governs which month's charge is due and the payoff's prerequisite, not an amount.
  - Its `compute_basis` placement under `invoice_date` is cosmetic.
- **Unchanged.** Every other rule sentence and compute binding is as in r1, and the r1 equivalence holds (r1 `### rule_compute_equivalence`).
- **Rounding (D8 closed).** The tool docstrings now say "rounded to the nearest cent (2 decimal places)" instead of "half-up". That matches the rules' "rounded to the cent". The residual tie convention (Python `round` against half-up) is now unstated rather than contradicted. No gold or substitution figure in either r2 world sits on a half-cent tie (see the task files).
- **Still open.** D6 (compute-only object selectors `lc_invoice` and `payoff_invoice`) is unchanged, and the reworker kept it. Observation, as in r1.

### action_binding_and_uuids (r2)

- The four tool bodies are byte-identical in logic to r1. Only the "rounded …" phrase in four docstrings changed. The uuid8s are unchanged and independent.
- No docstring gained an ordering word or another tool's name. No tool validates a prerequisite.
- (target_tool, computes) uniqueness is unchanged. Pass.

### prerequisite_graph and prerequisite_sentences (r2)

- Both `prerequisite` blocks are verbatim r1: policy_source, condition, form, kind, gate, resolved_by and effect are all unchanged. Each `policy_source` is still a verbatim sentence of its blocked rule.
- The r1 four-point tests and single-reading derivations hold.
- The payoff edge's single reading is now stronger: the full-month definition removes the r1 calendar-month caveat.
- No new rule sentence names a tool, policy id or snake_case token for another problem. The depended-on rules are still silent about the blocked side. Pass.

### override_declarations (r2)

- **D4 closed.** A second `overwrite` entry on the closing policy names base `client_evt_remittance`. Its superseded_clause "For a net_remit agreement the period's fees are first retained from trust and the rest is remitted" is a verbatim substring of the base rule. Its replaced_by "on a net_remit agreement, the available trust balance is set against the whole of the fees owed" is a verbatim substring of the closing rule.
- ETC, late charge and payoff overwrites are unchanged. The new sentences (window, day-count, renewal, full month, scope) deviate from no base sentence:
  - The renewal sentence restates base "any termination after the initial term carry no fee".
  - The full-month sentence fixes base's own "full calendar month" without changing it.
- Conclusion: every base/extended conflict on a scored quantity is declared. No undeclared deviation remains.

### factor_ladders (r2)

- Factor sets, effects, ladders, baselines and cross-difficulty labels are unchanged from r1, apart from the added scope bindings (`legal_agreement_ref`, `precollect_program_ref`, `payoff_legal_ref`). These sit inside their own factors' disjoint binding sets.
- Counts:
  - ETC 5 (1 method, 4 parameter)
  - closing 5 (1/4)
  - late charge 6 (1/5)
  - payoff 5 (1/4)
- Per task, multi-source and cross-category floors are as r1. Structure passes.
- D7 (legal and flatfee are claimed by no difficulty) is unchanged, kept by the reworker. Observation.

### findings (r2, charter-global)

| r1 item | r2 status |
|---|---|
| D1 overlap | closed (record-visible precedence sentence in both payment rules) |
| D2 count scope | closed |
| D3 renewal | closed (residual observation: tier-change edge case) |
| D4 net_remit overwrite | closed |
| D5 full calendar month | closed |
| D6 selectors | open, observation (kept) |
| D7 cross-difficulty definition | open, observation (kept) |
| D8 rounding | closed (tools say "nearest cent"; no ties in either world) |

New charter-global findings, all observations:
- The window sentence is undefined for a nonexistent same day.
- The renewal test after a tier change.
- The single-invoice-under-notice phrasing.

There is no charter-global SOURCE-POLICY RED.

### closing_checklist (r2)

Written after the r2 reveal (2026-10-10T20:17:23Z). The r2 charter-global section above was frozen at 20:16:14Z (mtime) and is unchanged.

- **Audit files:** `0.md` and `1.md` correspond one-to-one with the tasks. The r1 text of all three files is preserved, and each now carries `## revision_2`. r2 comparison sections: task 0 **PASS** (round-1 RED 0-F1 closed), task 1 **PASS**.
- **Round-1 claims, item by item:**
  - D1, D2, D3, D4, D5 and D8 are closed and verified in the charter.
  - 0-F1, 0-O1, 0-O2, 1-O1, 1-O2 and 1-O3 are closed and verified on the worlds.
  - The window-definition sentence is present in all four rules and equivalent to the DSL.
  - D6, D7 and 0-O3 were kept with reasons. The reasons hold, and all three remain observations.
- **No new defect** reaches RED. New observations:
  - The window sentence is undefined where "the same day" does not exist in the earlier month.
  - The renewal test reads the current tier's initial term after a tier change.
  - The closing-precedence wording does not say how a single-invoice payment under notice is figured.
  - The worklog's costs_first argument cannot be verified because no account linkage is seeded.
- **Coverage and scopes:** `charter_scope` {ETC, closing} / {late charge, payoff}. The scopes are disjoint and cover all four extended policies. GT writes equal the scope tools. The uuid8s are unchanged and independent.
- **Trees:** each has 1 prerequisite, 1 value_input edge and an `owner=user` root, with no cycle. The difficulty graph is acyclic.
- **Factors:** 5, 5, 6 and 5 factors, each with at least 2 parameter and 1 method. Every task has at least 1 multi-source and at least 1 cross-category factor. Every ladder has 3 distinct tiers stated in its rule. Every factor bears weight against an honest baseline, and every all-baseline figure differs from gold. The cross-category seed rows are consistent with the legal and flatfee charters.
- **Gates on the final form:** the coordinator's r2 re-run (`/tmp/env0050_views/gates/env0050_creditor_client_services_r2_gates.txt`) is all OK, and it is on the hashed final form (`7882eaf4…`, `a95a21d3…`).
- **The difficulty passes the source-layer audit at r2:** policy self-consistency, problem tree, factors and unique solution all PASS for both tasks.
