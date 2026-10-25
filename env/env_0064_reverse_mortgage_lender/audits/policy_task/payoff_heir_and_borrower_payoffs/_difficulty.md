# Policy-task audit — payoff_heir_and_borrower_payoffs / charter-global

## charter_global_frozen

- Freeze time: 2026-10-15T08:14Z (round 1). Auditor: independent erl-task-policy-audit agent. I did not write any of the audited artifacts.
- Hashes (sha256 prefix): `payoff.extended.yaml` fa65fb0d50a4781c; `task_tools.py` a7117c71ed79c7f3; `blueprint/products/payoff.yaml` ed03720d3e4d2cd2; masked views `0.json` d8de6ca750c3cf7f, `1.json` 4a6897f3397a12a4. These match the coordinator's snapshot `snapshot_r1.txt`.
- Read: `blueprint/` (payoff, hecm, setaside, residency and maturity charters, db_schema, share_tools); `payoff.extended.yaml`; `task_tools.py`; the two masked views; and `skills/erl-task-instantiate/scripts/check_compute.py`, for the semantics of the compute DSL: XCOUNT/XLATEST scoped to the customer, `within_months` = `0 <= MONTHS(d, NOW) < n`, LATEST/SUM scoped to the case, CFIELD/CPARAM = first match.
- Masked and not read before this section was written: `tasks/payoff_heir_and_borrower_payoffs/tasks/*.json`, `worklog.md` (difficulty and scenario), `docs/`, and every other audit. No recursive search touched `tasks/*/tasks/`. Nothing in this section comes from a revealed GT.
- Entry conditions: the gate snapshot came with the brief. All gates are green except two expected pre-render items (traceability tool-name provenance, and validate "required document not found"). The masked views came with their hashes. Input is complete.
- Base copy: every base key of the extended file (`category` … `policies`) is identical to `blueprint/products/payoff.yaml`, checked by a programmatic equality test.

### policy_conflict_scan

The charter has 8 extended policies in two disjoint chains:

- **Retention chain** (scope: Borrower Voluntary Payoff on a HECM whose maturity case is due_and_payable or extension_period):
  - p0 `payoff_ext_retention_daily_accrual` → `record_payoff_daily_accrual_16b003bd` (per_diem_amount)
  - p1 `payoff_ext_retention_statement_balance` → `issue_retention_payoff_statement_a856e53a` (statement_balance)
  - p2 `payoff_ext_retention_payoff_approval` → `approve_appraisal_based_payoff_a02ac9a5` (required_payoff_amount)
  - p3 `payoff_ext_retention_remittance` → `remit_borrower_payoff_funds_17f1493b` (amount, owner=user)
- **Sale chain** (scope: Estate Market Sale Payoff on a HECM, living borrower):
  - p6 `payoff_ext_sale_daily_accrual` → `record_sale_daily_accrual_1c6aaad4`
  - p4 `payoff_ext_sale_statement_balance` → `issue_sale_payoff_statement_764045f1`
  - p5 `payoff_ext_sale_cost_allowance` → `approve_sale_closing_costs_11c6cfd9`
  - p7 `payoff_ext_sale_seller_shortfall` → `remit_seller_closing_shortfall_d501bd8d` (owner=user)

The two chains' scopes do not overlap: BVP and Estate Market Sale are different `variant_name` values, so they share no subject or trigger. The four "only for such a … ; every other … remains under the base rule" carve-outs agree with each other.

Scope mismatch inside the sale chain: p4's balance applies to *any* Estate Market Sale statement on a HECM ("For an Estate Market Sale Payoff statement on a HECM, and only for such a statement"). But p6 (the per diem it waits on) applies only "requested by the living borrower of record", and so do p5 and p7. On an heir-requested estate sale, p4's prerequisite sentence ("fixed only after the payoff case carries a recorded per diem") has no writer in this charter. Neither task world is affected (both requesters are the borrower). Recorded as observation O-2.

Claimed scopes, read from the policy structure only (charter_scope is masked): task 0 = retention chain p0–p3, task 1 = sale chain p4–p7. The two are pairwise disjoint and together cover all 8 extended policies. This is confirmed against the masked fields at reveal (task files).

Cross-category read boundaries: hecm, setaside, residency and maturity are read only through CFIELD/CPARAM/EXISTS/X* with no writes. Base conflicts that touch these reads are listed under findings SF-2, SF-3 and SF-4.

### rule_compute_equivalence

I swept every compute binding against its `compute_basis` quotation and back against the rule. Rounding, window, filter, cap/floor and branch conventions match **except** for these (findings SP-4 and SP-5):

1. **p3/p7 `remitter_later_receipts`.**
   - Rule: "recall_holdback_pct_wire percent of that remitter's **later** receipts".
   - Compute: `SUM(... remitter_name=returned_remitter) - returned_receipt_amount`. This counts every receipt of that remitter, including ones *earlier* than the returned receipt.
   - Probe (task-0 world plus an earlier Dana wire of 5,000.00 dated 2026-10-01): compute gives 156,500.00 → holdback 15,650.00; the rule's "later receipts" gives 151,500.00 → 15,150.00.
   - Probe (Lorraine's 2,500.00 cashier's check returned on 2026-10-14): compute "later receipts" = 2,250.00, made up of her 10-09 and 10-11 checks, which are *earlier* than the returned 10-13 check.
2. **Rule names one object; compute reads the whole customer.**
   - p2 `intent_count`, `intent_date`, `extensions_granted` and `hud_extension_approvals`, and p5 `extensions_granted`, are XCOUNT/XLATEST over all of the customer's maturity history. The rule says "on the maturity case" / "the loan's maturity case carries".
   - p0/p1/p4/p6 `inspections_ordered`, and p2/p5 `latest_inspection_outcome`, read residency events on all of the customer's profiles. The rule says "on the borrower's occupancy profile" / "on it".
   - Probe (task-0 world plus a cured Property Charge Default case for the same customer with one `extension_approved` and one `maturity_extension_granted`): compute gives extension_charge 1,500.00 and result 609,600.00; the rule ("the HUD extension_approved steps on the maturity case") gives 750.00 and 608,850.00.
3. **p2 `prompt_credit`.**
   - Rule: the credit applies "when the **latest** accepted intent_declaration on the maturity case **states** retain_property".
   - Compute: filters `stated_intent='retain_property'` and then takes the latest. A later accepted `sell_property` declaration does not cancel the credit in compute, but does under the rule.
   - Neither seeded world carries such a decoy (task 0 has one declaration).
4. **p4 rule ends with an empty promise.** It says "leaves the required payoff amount at 0.00 for the sale review to set". p5 (the sale review) computes only `allowed_closing_costs`. Its tool `approve_sale_closing_costs_11c6cfd9` "leaves … required payoff amount … unchanged", and no policy of the charter writes the sale required payoff (finding SP-4).

Factor ladders against `decides` bindings: every `factors[].ladder` tier is a sentence of its rule and a branch of its `decides` binding, and the reverse holds too. No tier lives only in compute.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct; each tool is claimed by exactly one policy.
- The uuid8 values 16b003bd, a856e53a, a02ac9a5, 17f1493b, 1c6aaad4, 764045f1, 11c6cfd9 and d501bd8d share no prefix, show no sequence pattern and are not reused.
- No tool body checks eligibility or a prerequisite. Every body is an unconditional `ctx.update`/`ctx.create`, so the tool layer judges nothing.
- **Docstrings violate check 3** by stating sequence or prerequisite state (finding SP-6):
  - `record_payoff_daily_accrual_16b003bd`: "the daily figure the case's payoff statement is **then** built on"
  - `record_sale_daily_accrual_1c6aaad4`: "the daily figure the case's sale payoff statement is **then** built on"
  - `issue_retention_payoff_statement_a856e53a`: "uses the daily accrual **already recorded** on the case"
  - `issue_sale_payoff_statement_764045f1`: "uses the daily accrual **already recorded** on the case" … "can be set **once** the purchase contract is reviewed"
  - `approve_appraisal_based_payoff_a02ac9a5`: "on a payoff case **whose statement has been issued**"
- No docstring carries an example figure, so there is no gold leak through docstrings.

### prerequisite_graph

- `prerequisite` is filled on all 8 policies (`[]` on p0, p5 and p6).
- Edges: p1←p0, p2←p1, p3←p2, p4←p6, p7←p4, p7←p5. All are `value_input`, `form: state`, with no `fallback_reason` needed. The graph is acyclic.
- Every `problem` is an extended policy id. Every `resolved_by` equals that policy's `target_tool`.
- Every `gate` names a real binding of the blocked compute: `case_daily_accrual`, `stmt_on_case`, `required_on_case`, `daily_accrual`, `stmt_on_case` and `allowed_on_case`.
- Every `policy_source` is found verbatim in the blocked policy's own rule.
- `condition` text matches the sentence's strength. p7's second condition adds "the purchase contract submission is accepted". That is the same state the sentence calls "an approved … allowance with the approved contract price", so it is neither strengthened nor weakened.
- No authoring-viewpoint wording appears in the `prerequisite` text.

### prerequisite_sentences

| edge | sentence (own rule) | connective | waited-on state (record) | writer |
|---|---|---|---|---|
| p1←p0 | "The retention statement balance is fixed only after the payoff case carries a recorded per diem for the statement date." | only after | payoff_cases.per_diem_amount | p0 tool (p6 tool writes the same field; scope picks p0 on a BVP case) |
| p2←p1 | "The approved retention payoff is not set until the payoff case carries an issued statement balance." | not … until | payoff_cases.statement_balance / status | p1 tool (p4 tool writes the same field; scope picks p1) |
| p3←p2 | "The retention remittance is worked out only once the payoff case carries an approved appraisal basis with its required payoff amount." | only once | appraised_value_basis + required_payoff_amount | p2 tool only |
| p4←p6 | "The sale statement balance is fixed only after the payoff case carries a recorded per diem for the statement date." | only after | per_diem_amount | p6 tool (scope) |
| p7←p4 | "The seller closing shortfall is fixed only after the payoff case carries an issued sale statement balance." | only after | statement_balance | p4 tool |
| p7←p5 | "The seller closing shortfall is not worked out until the payoff case carries an approved sale closing-cost allowance with the approved contract price." | not … until | contract_price, allowed_closing_costs, submission accepted | p5 tool only |

- Each sentence passes the four-point test: it is state form, names no tool, policy id or row id, and has the edge's strength.
- No blocked rule carries a second wording of its edge, and no depended-on rule restates the sentence.
- Derivation, rule + records → resolving write:
  - On a BVP case with `per_diem_amount` 0.00, the only rule that sets a per diem on such a case is p0, so p0 is the resolving write.
  - The issued statement balance is p1's subject.
  - The "approved appraisal basis with its required payoff amount" is p2's subject.
  - The sale chain resolves in the same way through p6, p4 and p5.
- Two tools can write per_diem_amount, and two can write statement_balance. The policies' scopes pick exactly one in each world, so the hop resolves in one reading (observation O-1).
- One base sentence implies a cross-problem order: payoff_sale_review's price-minimum test uses "the lesser of the statement_balance and sale_min_pct_of_appraised percent of the appraised value", which needs the statement first. It grounds no declared edge, and p4/p5 commute on the tools' effects (neither tool touches the other's fields), so this is observation O-3.

### override_declarations

I compared each policy sentence by sentence against its `base_policy_refs`, plus any base policy whose quantity it governs even when that policy is not listed.

- **p0 / p6 (per diem)**
  - Base sentence "The per diem is the loan balance on the statement date times … divided by per_diem_day_count, rounded half up" is replaced, and the replacement is declared.
  - "The per diem's annual rate follows per_diem_rate_basis …" is followed.
  - Recipient, request-on-file and issue-within-business-days sentences are followed.
- **p1 / p4 (statement)**
  - The good-through sentence and the statement_balance sentence are replaced, both declared.
  - p4 also replaces the recipient sentence, declared. This is realistic: a borrower is always entitled to the statement on their own loan.
  - Other statement_terms sentences are followed.
- **p2 (approval)**
  - "The required payoff amount is the statement_balance for BVP …" is replaced, declared.
  - "Reissued terms replace every figure …" is replaced for BVP retention approvals, declared.
  - **Undeclared:** base "Terms that rely on an appraisal use **the latest appraisal recorded on the loan's maturity case** …". p2's `claim_capped_value_basis` replaces that appraisal with `max_claim_amount`, or with `MN(appraised_value, appraised_value_at_closing)`. No `overwrite` entry names the sentence → **SP-1**.
- **p3 (retention remittance)**
  - The remittance-reference sentence is replaced, declared.
  - Pooling, accepted methods (BVP: wire, cashiers_check), recall handling and short-funds return are followed.
  - Base "On satisfaction exactly the required payoff amount is applied …; any held excess is refunded …" is not overwritten. Under it, the lien-release charge and the wire processing fee that p3 adds to the remittance are refunded as excess, so the charges are never retained. This has no scored consequence: observation **O-4**.
- **p5 (sale cost allowance)**
  - The caps/decline sentence is replaced, declared.
  - Contract on file, arm's length and the Estate Sale price minimum are followed.
  - **Not implemented:** base "the required payoff amount is the lesser of the statement_balance and the contract price less the allowed closing costs" → **SP-4**.
  - **Undeclared:** base payoff_relocation_incentive "…a relocation incentive of cash_for_keys_max is committed …; **no other plan carries an incentive**". p5's `seller_relocation_allowance` pays relocation money on an Estate Market Sale, and p5's refs omit payoff_relocation_incentive → **SP-2**.
  - p5's subject is `payoff_terms_reissued`, but its tool keeps every other figure and does not restart the good-through period. That differs from the merged reissue sentence ("every other reissue replaces every figure and restarts the good-through period") and is undeclared. The consequence is not demonstrable on task 1, because the reissue happens on the statement day: observation **O-10**.
- **p7 (seller shortfall)**
  - The remittance-reference sentence is replaced, declared.
  - **Undeclared:** base payoff_acceptance "On plans whose acceptance_required is true, **nothing is taken toward satisfaction until the borrower or confirmed successor signs the agreement** under the issued terms". Estate Market Sale has `acceptance_required: true`. p7 takes the borrower's closing funds as a `payoff_funds_received` receipt, which counts in `payoff_msr_net_remitted`, on a case still in `terms_issued`, and does not overwrite that sentence → **SP-3**.
  - **Contradicted by its own factors:** base "Funds are accepted only by a method in the plan's accepted_remittance_methods". Estate Market Sale accepts `[wire]` only, so the cashier's-check tiers p7 relies on cannot be reached lawfully → **SF-6**.
- **Disguised forms checked:**
  - 0/1 multipliers: none found.
  - Dropped branch: base's BVP required payoff = statement_balance stays reachable through p2's "every other BVP …" carve-out.
  - Anonymous intermediate: yes, p2's value_basis (SP-1).

### factor_ladders

Each factor below has at least three tiers; tiers are distinct in value or method unless marked; fall-through equals baseline; every tier is stated in the rule and implemented in compute.

| policy | factor | label | multi-source? | xd | structural/realism verdict |
|---|---|---|---|---|---|
| p0, p6 | accrued_interest_carry / sale_ | method (daily×days vs monthly×months) | no | hecm | tier 2 (>31 days) unreachable under hecm charter → SF-3 |
| p0, p6 | insurance_renewal_carry, tax_installment_carry / sale_ | parameter | yes (LESA holding + bill rows) | setaside | Partially-Funded tier contradicts setaside charter; separate caps can carry 2× one LESA balance → SF-4 |
| p0, p6 | daily_servicing_fee_share / sale_daily_fee_share | parameter | no (one loan row) | hecm | same month's fee charged daily and as a carried fee → SF-5 |
| p0, p6 | unposted_inspection_carry / sale_ | parameter | yes (residency orders + hecm postings + plan param) | residency | nonzero tiers unreachable (fee posts on order date); `inspection_fee_chargeable` true in all 6 residency plans → SF-2 |
| p0, p6 | next_fee_date_carry / sale_ | parameter | no | hecm | "two or more" tier unreachable → SF-3; fee also in SF-5 |
| p1, p4 | statement_unposted_accrual / unposted_accrual_since_posting | method | no | hecm | tier 2 unreachable → SF-3; tier 1 applies inflated per diem to elapsed days → SF-5 |
| p1, p4 | statement_fee_per_month / servicing_fee_carried_per_month | parameter | no | hecm | double count with daily fee share → SF-5 |
| p1, p4 | statement_fee_count / servicing_fees_carried_count | parameter | no | hecm | tier 2 unreachable → SF-3 |
| p1, p4 | statement_bill_projection / lesa_bill_projection | parameter | yes | setaside | Partially-Funded tier contradicts setaside charter → SF-4 |
| p1, p4 | statement_inspection_projection / inspection_fee_projection | parameter | yes | residency | SF-2 |
| p1, p4 | retention_deadline_window / maturity_deadline_window | parameter | no | maturity | sound |
| p2 | occupancy_retention_percent | parameter | yes (profile status + inspection result) | residency | 100% fall-through / 97% tier vs HUD 95% → SF-1 |
| p2 | claim_capped_value_basis | method | yes (case appraisal vs loan MCA/closing appraisal) | hecm | MCA / origination-appraisal substitution has no HUD basis → SF-1 (and SP-1) |
| p2 | prompt_retain_intent_credit | parameter | yes (declaration + case deadline + extensions) | maturity | proprietary credit, plausible as own schedule (O-5) |
| p2 | hud_extension_carry | parameter | no | maturity | flat charge added above the HUD figure → SF-1 |
| p2 | vacant_home_preservation | parameter | yes (maturity plan + profile) | maturity/residency | flat charge added above the HUD figure → SF-1 |
| p3, p7 | uncollected_cashiers_check / seller_ | parameter | no | — | **tiers 1 and 2 both select "its amount"**; no guard for an already-returned check; on p7 (wire-only plan) tiers 1–2 unreachable → SF-6 |
| p3, p7 | recalled_remitter_holdback / seller_ | **method (mislabelled)**: 10% vs 100% of the same quantity is a rate | yes | — | SF-6; p7 tier 2 unreachable (cashier's check on a wire-only plan) |
| p3, p7 | multiple_wire_fee / seller_wire_fee | parameter | no | — | sound structurally (O-5 realism note) |
| p3 | lien_release_property_charge | parameter | no | hecm | property type is not a condition a servicer weighs for a lien-release charge → SF-7 |
| p3, p7 | deadline_clearing_cushion / seller_ | parameter | no (one maturity row) | maturity | sound |
| p5 | commission_cap_price_band | parameter | no | — | sound |
| p5 | other_cost_cap_property_type | parameter | no | hecm | sound |
| p5 | tax_installment_settlement | method | yes | setaside | tier 2 counts a Borrower-Elected Fully Funded LESA bill as fully seller-paid while p0/p1/p4/p6 treat that LESA as paying it → SF-4 |
| p5 | vacant_home_upkeep | parameter | yes | residency | sound (proprietary) |
| p5 | extended_marketing | parameter | yes | maturity | proprietary, no HUD basis (O-5) |
| p5 | seller_relocation_allowance | parameter | yes | residency | contradicts base (SP-2) |

Counts as declared:

| policy | factors | parameter | method | multi-source | cross-difficulty |
|---|---|---|---|---|---|
| p0, p6 | 6 | 5 | 1 | 3 | 6 |
| p1, p4 | 6 | 5 | 1 | 2 | 6 |
| p2 | 5 | 4 | 1 | 4 | 5 |
| p3 | 5 | 4 | 1 (mislabelled) | 1 | 2 |
| p5 | 6 | 5 | 1 | 4 | 5 |
| p7 | 4 | 3 | 1 (mislabelled) | 1 | 1 |

Counting only factors that survive the tests:
- p3 drops uncollected_cashiers_check and lien_release_property_charge, and its only method is mislabelled. That leaves 3 factors and 0 methods.
- p7 drops seller_uncollected_check, and its only method is mislabelled. That leaves 3 factors and 0 methods.
- p0, p6, p1 and p4 each lose their method factor to SF-3, and most of their parameter factors to SF-2, SF-4 and SF-5.

All of these fall below the 4–6 factors with ≥1 method bound. This follows directly from the findings below; it is not a separate finding.

### findings

Each finding: symptom → root cause → evidence → demonstrated consequence → affected location. "Bears on" names the tasks whose files demonstrate the consequence.

**SP-1 SOURCE-POLICY RED: undeclared override of the base appraisal sentence (p2).**
- Base payoff_statement_terms: "Terms that rely on an appraisal use the latest appraisal recorded on the loan's maturity case, which must still be within that case's appraisal validity period".
- p2 compute: `value_basis: max_claim if appraised_value > max_claim else (MN(appraised_value, closing_appraisal) if appraisal_age_months >= K('stale_appraisal_months') else appraised_value)`.
- p2 `overwrite` lists only the required-payoff and reissue sentences.
- Two readings reach different numbers in the same world. Bears on **task 0**: 640,000.00 vs 655,000.00 basis, demonstrated in 0.md.

**SP-2 SOURCE-POLICY RED: relocation allowance on an Estate Market Sale contradicts base "no other plan carries an incentive" (p5, undeclared; refs omit payoff_relocation_incentive).** Bears on **task 1**.

**SP-3 SOURCE-POLICY RED: p7 takes closing funds on an unsigned Estate Market Sale case.**
- Base payoff_acceptance: "nothing is taken toward satisfaction until the borrower or confirmed successor signs the agreement under the issued terms".
- Estate Market Sale has acceptance_required true, and p7 does not overwrite the sentence.
- Second reading: wait, or decline, until the agreement is signed. No tool records a signature, so an agent following base cannot take the wire now.
- Bears on **task 1**.

**SP-4 SOURCE-POLICY RED: empty promise on the sale required payoff.**
- p4: "The statement keeps the per diem the case carries and leaves the required payoff amount at 0.00 for the sale review to set."
- Base sale review: "the required payoff amount is the lesser of the statement_balance and the contract price less the allowed closing costs".
- p5's rule and compute never set it, and `approve_sale_closing_costs_11c6cfd9` "leaves … required payoff amount … unchanged".
- After the sale chain the case therefore carries required_payoff_amount 0.00 while base says 637,254.34-class figures (task-1 numbers are in 1.md).
- A reader following base must record that figure. The only tool that writes `required_payoff_amount` (plus `appraised_value_basis`) is the BVP-scoped `approve_appraisal_based_payoff_a02ac9a5`, so the reader either makes an extra, out-of-scope write or hands the case off.
- Bears on **task 1**.

**SP-5 SOURCE-POLICY RED: rule/compute mismatches on decoy rows.** All members, with probes, are listed under rule_compute_equivalence items 1–3:
- (a) p3/p7 `remitter_later_receipts` counts earlier receipts;
- (b) p2 intent_count/intent_date/extensions_granted/hud_extension_approvals and p5 extensions_granted are customer-wide, not case-wide; p0/p1/p4/p6 inspections_ordered and p2/p5 latest_inspection_outcome are customer-wide, not profile-wide;
- (c) p2 prompt_credit takes the latest *retain* declaration instead of testing the latest declaration.

Probes give 15,650.00 vs 15,150.00 (a) and 609,600.00 vs 608,850.00 (b). Neither seeded world contains the decoy, so the scored values of tasks 0 and 1 are unaffected. This is a charter defect only.

**SP-6 SOURCE-POLICY RED: docstrings state sequence and prerequisite state (check 3).**
- The five docstrings are quoted under action_binding_and_uuids.
- Consequence: three of task 0's three edges (p0→p1, p1→p2 and, through "already recorded", p0→p1 again) and one of task 1's edges (p6→p4, plus "once the purchase contract is reviewed") can be read off the tool layer, without deriving them from the prerequisite sentences.
- Bears on **tasks 0 and 1**.

**SF-1 SOURCE-FACTOR RED: the retention figure departs from HUD's lesser-of-balance-or-95%-of-appraised-value treatment (p2).**
- Real practice: 24 CFR 206.125(c), and HUD Handbook 4000.1 / ML 2015-10 FAQs. When a HECM is due and payable, the borrower, estate or heirs may satisfy the debt for the lesser of the mortgage balance or 95% of the current appraised value. The charter's own base schedule applies 95% to Heir Retention (`retention_pct_of_appraised: 95.0`).
- Members:
  - `occupancy_retention_percent`: the fall-through tier gives an occupying borrower 100%, and the `occupied_by_others` tier 97%. Occupancy is not a condition HUD weighs for this figure, and 100% for the ordinary customer is a treatment an FHA-insured HECM servicer would not publish.
  - `claim_capped_value_basis`: tier 1 substitutes the loan's max_claim_amount (an origination-era figure) for the current appraisal; tier 2 substitutes the 2016-era `appraised_value_at_closing` for a ≥3-month-old appraisal. No servicer values a payoff on either. Base instead says a stale appraisal makes new terms "wait for a new appraisal".
  - `hud_extension_carry` and `vacant_home_preservation`: flat charges added on top of the value-based figure push the payoff above HUD's 95% ceiling.
- Bears on **task 0**.

**SF-2 SOURCE-FACTOR RED: unposted-inspection tiers are unreachable, and the seeded rows contradict the residency charter (p0, p1, p4, p6).**
- residency `residency_inspection_ordered` triggers `hecm:hecm_advance_posting` with `effective_date: effective_date`, `advance_type: occupancy_inspection_fee`, `source_txn_ref: residency_event_id`. Every order therefore posts its fee the same day, the "unposted" difference is always 0 under the charters, and tiers 1–2 of all four inspection factors can never be reached.
- Both seeds carry orders with no posting, and postings dated days after their order (task 0: order 2026-08-04 posted 2026-08-14; task 1: order 2026-08-25 posted 2026-09-02). These states the residency charter cannot produce.
- Separately, the conjunct "inspection_fee_chargeable true" holds in all six residency plans (`inspection_fee_chargeable: true` ×6), so that part of each compound tier holds for every customer.
- Bears on **tasks 0 and 1**.

**SF-3 SOURCE-FACTOR RED: posting-lag tiers are unreachable under the hecm charter (p0, p1, p4, p6).**
- hecm: "Interest and the annual mortgage insurance premium accrue monthly and are posted on servicing_fee_assessment_day [1] for the prior month … Interest and MIP accrue only while the loan status is active, due_and_payable or deferral_period". Fees: "The fee for a month is posted on servicing_fee_assessment_day of the following month".
- So days-since-posting is always 0–30 and the latest fee period is always one whole month back.
- Unreachable members: accrued_interest_carry tier 2 (p0, p6); statement_unposted_accrual tier 2 (p1); unposted_accrual_since_posting tier 2 (p4); next_fee_date_carry "two or more" (p0, p6); statement_fee_count "2" (p1); servicing_fees_carried_count "2" (p4).
- Task 1's seed omits the 2026-10-01 postings (Sept interest, MIP and fee) on a due_and_payable loan at 2026-10-15, so its tiers rest on a ledger the hecm charter cannot produce.
- Bears on **task 1** (task 0 sits on the normal tier 1).

**SF-4 SOURCE-FACTOR RED: LESA tiers contradict the setaside charter.**
- The Partially Funded LESA has `pays_property_tax: false`, `pays_hazard_insurance: false`, `continues_while_due_and_payable: false`. Setaside: "a bill for a charge the plan does not pay … is declined with reason not_payable_from_this_setaside, and the charge stays the borrower's to pay".
- Members:
  - p0/p6 insurance and tax carry tier 2 ("up to the Partially Funded LESA's setaside_balance"). Each bill is capped separately, so one balance can be carried twice.
  - p1/p4 bill_projection tier 2.
  - p5 tax_installment_settlement tier 2. It fires when "no active Fully Funded LESA (Mandatory)", which includes an active Borrower-Elected Fully Funded LESA that, per setaside and per p0/p1/p4/p6, pays the bill itself. The same bill is then both projected into the balance and allowed in full as a seller cost.
- Task 1's seed carries `paid` tax and insurance bills on its Partially Funded LESA (rows b67716cc, 33625369), which the setaside charter forbids.
- Bears on **task 1**.

**SF-5 SOURCE-FACTOR RED: the same month's servicing fee is charged twice, and the per diem is charged on elapsed days for amounts not yet advanced (p0/p6 with p1/p4).**
- p1/p4 add the next fee date's fee ("carried servicing fees") **and** multiply the recorded per diem by the elapsed days and the window days. That per diem includes "the daily servicing-fee share" (fee × 12 / 365) and interest on a basis that carries bills not yet disbursed, inspection fees and the next fee.
- So each statement collects the carried month's fee a second time pro rata, and charges interest for elapsed days on amounts not yet on the loan.
- HUD caps the monthly servicing fee (the charter's $35 / $30, matching HUD's limits), and interest accrues only on amounts advanced.
- Bears on **tasks 0 and 1** (figures in each task file).

**SF-6 SOURCE-FACTOR RED: the remittance ladders (p3, p7) are unreal or mislabelled.**
- uncollected_cashiers_check / seller_uncollected_check: tiers 1 and 2 both select "its amount", so one tier is written as two.
- There is no guard for an already-returned check. Probe on task 0's world: the 2,500.00 check returned on 2026-10-14 lowers held credit by 2,500.00 and is still added back by 2,500.00.
- recalled_remitter_holdback / seller_recall_holdback is labelled `method`, but its tiers are `pct × later receipts` with pct 10 or 100, which is a parameter. p3 and p7 therefore have no honest method factor.
- On p7's own plan (Estate Market Sale, `accepted_remittance_methods: [wire]`), the cashier's-check tiers (uncollected tiers 1–2, holdback tier 2) can never be reached for a lawfully recorded receipt.
- Realism: a servicer holds satisfaction until funds clear. It does not demand the borrower re-send the amount of a received cashier's check (next-day availability under Reg CC) or 10–100% of another remitter's receipts.
- Bears on **tasks 0 and 1**.

**SF-7 SOURCE-FACTOR RED: the lien-release charge depends on property type (p3).**
- Tiers: condo/PUD 92.00, two-to-four unit 64.00, otherwise 0.00. Property type is not a condition a servicer weighs for a lien-release charge (recording costs follow the county and the document).
- Under base payoff_agg_funds any amount above the required payoff is refunded after satisfaction (O-4), so the charge is never actually retained.
- Bears on **task 0**.

**Observations (not grounds for rework):**
- **O-1:** two tools write per_diem_amount, and two write statement_balance. Policy scope resolves each hop in one reading.
- **O-2:** p4 balance scope is wider than p6/p5/p7 (heir-requested estate sales have no per-diem writer).
- **O-3:** the base price-minimum test needs the statement first, while p4/p5 commute on the tools.
- **O-4:** the fees in p3/p7 are refunded under base's excess rule.
- **O-5:** prompt-intent credit, extended-marketing allowance and multiple-wire fee have no HUD basis but are plausible as the company's own schedule.
- **O-6:** seeded principal_balance does not reconcile with the posted ledgers (task 0: +564.92 over the Oct-1 balance implied by the 3,732.78 interest posting; task 1: −1,911.19 below the Sep-1 implied balance).
- **O-7:** task 0's insurance premium (due 2026-11-02, Fully Funded LESA, `insurance_payment_lead_days: 30`) is still unpaid 9 days after receipt.
- **O-8:** the p0/p6 accrual basis includes unposted interest, which compounds daily against HECM monthly compounding.
- **O-9:** `RND` is Python binary `round`, not decimal half-up. I checked every scored intermediate with Decimal half-up and none sits on a half-cent.
- **O-10:** p5's reissue keeps figures, undeclared against the merged reissue sentence.

## closing_checklist

Written after both reveals (2026-10-15T08:20Z). The sections above were frozen before either reveal and have not been changed.

- **Audit files:** one per task (0.md, 1.md), plus this `_difficulty.md`. Round 1, so there are no older revisions.
- **Scope:** charter_scope revealed task 0 = p0–p3 and task 1 = p4–p7. The two are pairwise disjoint and together cover all 8 extended policies, as derived in the policy_conflict_scan.
- **Tools:** uuid8s are independent; every task tool is used in GT.
- **Trees:** each has 3 prerequisite problems, 3 value_input edges and an owner=user root. Both are acyclic, and so is the whole difficulty's graph.
- **Factors:** every factor bears numerical weight on its world, every baseline is honest, and each full baseline is definite and differs from gold. GT's factor_sensitivity matches my figures exactly. However, the surviving-factor bounds fail once SF-1 through SF-7 are applied.
- **Gates:** not re-run by me. The coordinator snapshot (round 1) is green apart from pre-render items.
- **The difficulty does NOT close:**
  - Task 0: SOURCE-POLICY RED and SOURCE-FACTOR RED.
  - Task 1: SOURCE-POLICY RED, SOURCE-CHAIN RED and SOURCE-FACTOR RED.
  - Charter-wide REDs: SP-1 through SP-6 and SF-1 through SF-7.

task0=SOURCE-POLICY+SOURCE-FACTOR RED task1=SOURCE-POLICY+SOURCE-CHAIN+SOURCE-FACTOR RED
charter=SP-1,SP-2,SP-3,SP-4,SP-5,SP-6,SF-1,SF-2,SF-3,SF-4,SF-5,SF-6,SF-7

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Charter-global section frozen 2026-10-15T19:02Z, before either task's revision-2 GT was read.
- **Gate check passed.** `tail -1 worklog.md` = `REWORK round 2: gates 7/7 green`. Snapshot `.audit_views/policy/payoff_heir_and_borrower_payoffs/snapshot_r2.txt` (2026-10-15T18:53:31Z): EXTENDED, TASK TOOL, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK.
  - Traceability: only the unlock tool-name miss (`issue_sale_payoff_statement_764045f1`); non-tool-name misses 0.
  - validate_scenario is INVALID. I re-ran `erlbench.validate.validate_scenario` to see why: all 20 errors are "required document ... not found" across the three unrendered difficulties, which is a pre-render condition, not a gate red.
- **Hashes:** `payoff.extended.yaml` 7a89a18c1ee8996c (was fa65fb0d50a4781c); `task_tools.py` 37f0e323eb919cd5 (was a7117c71ed79c7f3); views `0.json` b8e97ebbb3ac3599, `1.json` 13e923a62b324aa1. Both shared inputs changed, so **every charter-global section is re-derived in full** below. Round-1 text above is left unchanged.
- **Read set:** the same isolation as round 1, plus `audits/render_source/XF_recipe.md` (as instructed) and the blueprint hecm/setaside/maturity/residency charters for seed legality. worklog.md was read only through its last line. Task JSONs were not read before the freezes.
- **Base copy:** verbatim; programmatic equality check passes.

### rework summary (structure only)

- The sale chain changed plan, from Estate Market Sale to **Approved Short Sale Payoff** requested by the borrower of record.
  - p6 (`payoff_ext_sale_cost_allowance`) now computes **required_payoff_amount** and writes contract price, allowed costs, required payoff and appraised basis.
  - p6's edge to the sale statement is a `state_gate` (the Estate-minimum test).
  - p7 now depends on p6 only.
- Retention chain: p2 is now HUD's lesser of (statement balance + resolution charges − prompt credit) and 95% of the case appraisal.
- Every factor set was replaced.

### policy_conflict_scan (r2)

- **Scopes.** Retention = BVP requested by the borrower of record, maturity case due_and_payable / extension_period / foreclosure_referred. Sale = Approved Short Sale Payoff requested by the borrower of record. The two are disjoint.
- **Base clauses retired by two policies each:**
  - per diem (p0, p4)
  - statement_balance (p1, p5)
  - reissue (p2, p6)
  - remittance reference (p3, p7)
  - excess refund (p3, p7)

  Each pair's `replaced_by` names both carve-outs and restates base for every other case, so the merged texts agree.
- **Remaining cross-policy divergence.** The sale chain's per-diem basis (p4) carries the maintenance advance when the occupancy profile is `nonoccupancy_confirmed`. The sale statement (p5) charges maintenance only when the latest inspection found the home `vacant`. In a world where the profile is confirmed non-occupied but the latest inspection says `occupied_by_others`, interest would accrue on a maintenance advance the statement never charges. Neither task world has that combination: in task 1 both conditions hold. Observation R2-O1.

### rule_compute_equivalence (r2)

- I swept every `compute_basis` string against its rule with a scratch script. Every quote is verbatim, every compute binding has a basis, every `baseline.rule` sits inside its rule, every prerequisite `policy_source` and every `replaced_by` is verbatim in its rule, and rounding sentences match the RND placement.
- Every X*/CFIELD/CPARAM/EXISTS read now carries an object filter (`*_loan_id`, `maturity_case_id`, `residency_profile_id` or `setaside_id`); a mechanical scan found none without. The round-1 decoy classes are gone:
  - (a) "later receipts": the holdback is removed.
  - (b) customer-wide maturity and residency reads: now scoped. Task 0 seeds a cured 2021 Property Charge Default case carrying an extension, and it is excluded.
  - (c) prompt credit: now reads the latest accepted declaration of any intent and then tests it for retain_property.
- **Absent-record and sentinel branches** (XF 8) are stated in the rules: no posting → 0 days; no nonoccupancy_date → 1 month; no bill → nothing; no submission → 0.00; no listing → 0.00; no referral_date → 0 days. The one unstated sentinel is p3/p7 `loan_age_months` = 0 when there is no closing_date. Every funded loan has a closing_date, so this is observation R2-O2.

### action_binding_and_uuids (r2)

- The same eight tools and uuid8s; each `(target_tool, computes)` pair is unique. p6 now `computes: required_payoff_amount`, which no other policy claims for a short-sale case.
- No tool body checks anything.
- Docstrings:
  - No ordering word and no prerequisite state. "then built on", "already recorded", "whose statement has been issued" and "once the purchase contract is reviewed" are all removed; "Afterwards" became "On success".
  - Each docstring's stated effect matches its body: the sale statement leaves required unchanged; the short-sale approval writes all four figures.
  - No example figures.
- **SP-6 closed.**

### prerequisite_graph (r2)

| edge | kind | form | gate binding | sentence (own rule, verbatim) |
|---|---|---|---|---|
| p1←p0 | value_input | state | per_diem_on_case | "The retention statement balance is fixed only after the payoff case carries a recorded per diem for the statement date." |
| p2←p1 | value_input | state | stmt_on_case | "The approved retention payoff is not set until the payoff case carries an issued statement balance." |
| p3←p2 | value_input | state | required_on_case | "The retention remittance is worked out only once the payoff case carries an approved appraisal basis with its required payoff amount." |
| p5←p4 | value_input | state | per_diem_on_case | "The short-sale statement balance is fixed only after the payoff case carries a recorded per diem for the statement date." |
| p6←p5 | **state_gate** | state | payoff_cases.statement_balance | "The short-sale approval is not made until the payoff case carries an issued statement balance." |
| p7←p6 | value_input | state | allowed_on_case | "The seller closing contribution is not worked out until the payoff case carries an approved short-sale allowance for its closing costs." |

- The graph is acyclic and every `resolved_by` equals the depended-on policy's target tool.
- The p6←p5 state gate is a real eligibility gate: base "A contract that meets the Estate Market Sale Payoff minimum is never approved as a short sale", restated in p6, needs the case's statement_balance.
- Writers per state:
  - per diem: p0 tool on a retention case, p4 tool on a short-sale case.
  - statement: p1 and p5 tools, by scope.
  - approval / allowance: one tool each.

  Each hop resolves in one reading (O-1 carried).

### override_declarations (r2)

Sentence by sentence against base:
- **p0/p4:** per diem replaced, declared; recipient, request-on-file and statement timing followed.
- **p1:** good-through and statement_balance replaced, declared.
- **p5:** recipient (adds the borrower of record on a short sale) and statement_balance replaced, declared. Short-sale good-through stays at statement_good_through_days, as base says.
- **p2:** required payoff for BVP and reissue replaced, declared. The appraisal sentence ("the latest appraisal recorded on the loan's maturity case … within that case's appraisal validity period") is now followed. **SP-1 closed.**
- **p6:** closing-cost caps, short-sale required payoff and reissue replaced, declared. Followed: contract on file, arm's length, the short-sale 88% minimum and 30-day listing, and "a contract that meets the Estate Market Sale minimum is never approved as a short sale" (restated). The required payoff is now set by this policy and its tool. **SP-4 closed.**
- **p7:** payoff_acceptance is declared (the seller's own contribution is held before signature and applied only from accepted status). **SP-3 closed.** Remittance reference and excess refund replaced, declared.
- No relocation incentive remains on any non-DIL plan. **SP-2 closed.**
- **New:** p3/p7's excess-refund overwrite now **retains** "the remittance charges collected with the borrower's own remittance", and each rule lists the **clearing cushion** among those charges. Base payoff variants carry `interest_through_basis: date_funds_received`, which is not overwritten. → finding **R2-N1**.

### factor_ladders (r2)

Counts per policy:

| policy | factors | parameter | method | cross-difficulty |
|---|---|---|---|---|
| p0 | 5 | 3 | 2 | 5 |
| p1 | 6 | 2 | 4 | 6 |
| p2 | 6 | 5 | 1 | 6 |
| p3 | 5 | 4 | 1 | 3 |
| p4 | 6 | 4 | 2 | 6 |
| p5 | 6 | 4 | 2 | 6 |
| p6 | 6 | 5 | 1 | 4 |
| p7 | 4 | 3 | 1 | 2 |

Every ladder has at least three tiers, each fall-through equals its baseline, and every tier is in the rule and in compute.

- **Method labels:** all honest. Each method factor changes the algorithm:
  - cap vs uncapped sum (set-aside / disbursements);
  - flat vs per-month (preservation / maintenance);
  - flat vs reduced-per-extension (prompt credit);
  - per diem × days vs flat (cushion);
  - bills − balance vs declined bills (property-charge shortfall).

  Round 1's rate-labelled-as-method holdback is gone.
- **Duplicate tiers:** none. The round-1 "its amount" twins are gone.
- **Seed and charter reachability:**
  - The posting-lag tiers (round-1 SF-3) and the unposted-inspection tiers (round-1 SF-2) are removed.
  - Partially Funded LESA now appears only in p6's "declined bills" tier, which matches setaside (the plan pays no bill; a declined bill "stays the borrower's to pay").
  - Borrower-Elected Fully Funded LESA is treated like Mandatory everywhere.
  - The Summit Reserve tiers are reachable via the jumbo charter (`shortfall_source: corporate_advance` matches "paid at once as a corporate advance").
- **Realism of conditions and values:**
  - Appraisal fee by property type, update vs replacement appraisal, foreclosure charges by time since referral, securing and maintenance of vacant property (`vacant_property_securing`), title search by loan age, and recording two instruments for a HECM (lender's mortgage plus the Secretary's second mortgage, three with a trust certification) are all real servicing practice.
  - Wire-receipt fee, returned-item fee, notice postage, prompt-decision credit and the extended-marketing allowance are proprietary (O-5 carried).
  - p2 now follows HUD 24 CFR 206.125(c): the lesser of balance owed and 95% of the current appraised value. **SF-1 closed.**
- **XF recipe, points 1–9, applied to all 8 policies:**
  1. Each baseline defines every combined quantity with its default and never names a factor.
  2. Each factor owns one quantity. p1's hazard/flood limits re-read the bill amounts through their own bindings, not through the tax factor's output.
  3. Every factor moves its own scored value on its task's world (see the task files).
  4. Each combination is stated once, with floor and lesser ordering stated.
  5. No cross-policy definitions.
  6. Each `replaced_by` restates base for out-of-scope cases. p0 and p4 say "the per diem is the … daily accrual set out in this policy", a self-pointer close to the forbidden "fixed below"; their merged semantics are unique. Observation R2-O3.
  7. Every quote is verbatim.
  8. Branches are stated (one exception, R2-O2).
  9. Docstrings are clean.

### findings (r2, charter-global)

**Closure of the round-1 charter REDs** (evidence in the sections above):

| id | status |
|---|---|
| SP-1 | closed |
| SP-2 | closed |
| SP-3 | closed (declared) |
| SP-4 | closed |
| SP-5 | closed for (a), (b) and (c) across all members |
| SP-6 | closed |
| SF-1 | closed |
| SF-2 | closed (factor removed; seeds post the inspection fee on the order date) |
| SF-3 | closed (tiers removed; seeds carry the 2026-10-01 postings) |
| SF-4 | closed |
| SF-5 | **closed** as a double-count class: no daily fee share now exists, and fee months come only from posted periods. Residual: the per diem, whose basis includes advances not yet made (bills due within 30 days, preservation, appraisal and foreclosure charges), is multiplied by the elapsed days since the last interest posting. That is interest for elapsed days on advances not yet made. Task 0: 5,720.40 of bills × 7.375% / 365 × 13 days ≈ 15.02. It is a projection convention with no second internal figure, so it is an observation (R2-O4), not a RED. |
| SF-6 | closed (round-1 ladders removed; p3/p7 methods honest) |
| SF-7 | closed |

**R2-N1 — new: SOURCE-FACTOR RED (realism) plus SOURCE-POLICY conflict. The clearing cushion is retained as a charge after satisfaction (p3 `remittance_clearing_cushion`, p7 `contribution_clearing_cushion`).**
- *Symptom.* p3 and p7 each list the cushion among the "remittance charges" / "contribution charges". Their shared overwrite of base payoff_agg_funds says "the remittance charges collected with the borrower's own remittance are then retained for those charges; any held excess left is refunded". The cushion is therefore kept even though the funds arrive before the good-through date.
- *Tier values.*
  - foreclosure_referred: per diem × late_funds_tolerance_days, i.e. 5 more days of interest on top of the statement's own projection to good-through;
  - extension_period: a flat 100.00.
- *Conflict.* Base interest_through_basis is `date_funds_received`, not overwritten. Base payoff_satisfaction already defines the only legitimate late-funds per diem: "funds received after the good-through date but within the tolerance must also cover the per diem for each day past the good-through date".
- *Round-1 comparison.* The rule said "any cushion left over after satisfaction is refunded under the plan's overpayment rule". The rework's retention clause turned that refund into a retained charge.
- *Realism.* No HECM/FHA servicer publishes "we keep an extra five days of interest on your loan even when your wire clears today".
- *Bears on.* Task 0 (426.55 retained) and task 1 (636.85 retained). The scored remittance amounts are unchanged; the defect is in what the charter does with them.

**Observations:**
- **R2-O1:** sale per-diem maintenance condition (profile status) vs statement maintenance condition (inspection result).
- **R2-O2:** unstated closing_date sentinel.
- **R2-O3:** "set out in this policy" self-pointer in p0/p4 replaced_by.
- **R2-O4:** elapsed-day interest on advances not yet made.
- **R2-O5:** the base Approved Short Sale floor (88% of appraised) is a blueprint-level choice, not this difficulty's; HUD's HECM sale rule is 95%. Noted for the blueprint owner only.
- **R2-O6:** the p6 and p7 rule texts carry splice artefacts ("…allowed closing costs. the required payoff amount…"; "…from accepted status; Each remittance…"). Wording only.

### closing_checklist (r2)

Written after the reveal at 2026-10-15T19:02:39Z.

- **Files:** revision_2 sections appended to 0.md, 1.md and `_difficulty.md`; round-1 text untouched.
- **Agreement with GT:** both tasks' blind derivations equal GT on every scored value, every factor figure and every baseline_result.
- **Scopes:** task 0 = p0–p3, task 1 = p4–p7. Disjoint and complete.
- **Tools:** uuid8s unchanged and independent; docstrings clean.
- **Trees:**
  - Task 0: 3 prerequisite problems and 3 value_input edges.
  - Task 1: 3 prerequisite problems and 2 value_input edges plus one state gate.
  - Both roots are owner=user; both graphs are acyclic.
- **Factors:** 4–6 per computation, at least 2 parameter and at least 1 method each, all honest. Multi-source and cross-difficulty factors are present in each task, and every factor bears weight on its world.
- **Seeds:** legal under the hecm, residency, setaside and maturity charters.
- **Gates:** green per snapshot_r2. The INVALID result is pre-render only.
- **Does not close:** one charter RED remains, R2-N1, carried into both tasks.

VERDICT revision_2: task0=SOURCE-FACTOR RED task1=SOURCE-FACTOR RED charter=R2-N1

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3. Charter-global section written 2026-10-15 (~20:02Z), before either task's revision-3 GT was read.
- **Gate check passed.** `tail -1 worklog.md` = `REWORK round 3: gates 7/7 green`. Snapshot `snapshot_r3.txt` (2026-10-15T20:00:41Z): seven gates OK; traceability has only the unlock tool-name miss (non-tool-name misses 0); validate_scenario INVALID for the same pre-render "required document not found" reason as round 2.
- **Hashes vs snapshot_r2:**

  | input | snapshot_r2 | snapshot_r3 | changed? |
  |---|---|---|---|
  | `payoff.extended.yaml` | 7a89a18c1ee8996c | e162db16b45ab0a9 | yes |
  | `task_tools.py` | 37f0e323eb919cd5 | 37f0e323eb919cd5 | no |
  | view `0.json` | b8e97ebbb3ac3599 | 4e24bcbf24e1926c | yes |
  | view `1.json` | 13e923a62b324aa1 | 13e923a62b324aa1 | no |

  The charter changed, so its sections are re-derived below. The tool module did not change, so action_binding_and_uuids is carried forward from revision_2 on the unchanged hash, and SP-6 stays closed.
- **Base copy:** verbatim.

### re-derived charter checks (r3)

- **Mechanical sweep, all 8 policies:**
  - every compute_basis quote is verbatim in its rule, and every binding has a basis;
  - every `replaced_by`, prerequisite `policy_source` and `baseline.rule` is inside its rule;
  - every cross-category read carries an object filter.
- **Prerequisite graph:** unchanged. p1←p0, p2←p1, p3←p2, p5←p4 and p7←p6 are value_input; p6←p5 is the state_gate. Acyclic.
- **Factor counts:** unchanged; each policy has 4–6 factors with at least 1 method. Methods honest; no duplicate tiers.
- **R2-N1 — closed.**
  - p3 and p7 now list the cushion apart from the "four remittance charges" / "three contribution charges".
  - Their overwrite reads: "the remittance charges … other than its clearing cushion, are then retained …, and the clearing cushion, per diem collected in advance, is kept only for the per diem the case owes for each day its funds were credited after the statement's good-through date, per interest_through_basis; any held excess left, an unused cushion included, is refunded".
  - Both rules say: "whatever of it is not needed for that per diem is refunded with the held excess".
  - This is consistent with base `interest_through_basis: date_funds_received` and with payoff_satisfaction's tolerance per diem.
- **Same-day ties.** Every "latest" pick that selects a *record* now has a stated tie rule, and compute matches it (probed on scratch copies):

  | where | tie rule | probe result |
  |---|---|---|
  | bills sharing the latest due_date (p0, p1, p4, p5, p6 approval bills; p6 declined bills) | billed_amounts taken together (XSUM on due_date = latest) | a second 100.00 tax bill on 2026-11-12 → 2,712.40 |
  | inspection results sharing the latest effective_date (p0, p1, p2, p4, p5) | vacant first, then unable_to_determine | vacant + occupied_by_others on 2026-09-29 → vacant |
  | accepted intent declarations sharing the latest request_date (p2) | retain only when all retain | retain + sell on 2026-01-12 → credit 0.00 |
  | accepted contracts sharing the latest request_date (p7) | largest commission and largest other costs (MAX) | — |
  | more than one received contract (p6) | no approval figures until a single one remains (`contracts_on_file == 1`) | two received contracts → 0.00 |

  The other "latest" picks (latest interest posting date, latest extension date, latest fee accrual_period) return a date or period value, so a tie cannot change them.
- **R2-O1 — closed.** p4's maintenance carry now uses the latest inspection result (vacant, with the same tie rule), the same condition as p5's statement preservation.
- **XF recipe, points 1–9:** still holds. Baselines define every quantity and name no factor; each combination is stated once with its order; docstrings are unchanged and clean; branches and ties are stated. R2-O2 (closing_date sentinel), R2-O3 ("set out in this policy") and R2-O4 (elapsed-day interest on advances not yet made) remain observations; no rework needed.
- **Regression scan:** none. Every round-1 and round-2 closure still holds on the new text.
- **New defects:** none found.

### closing_checklist (r3)

Written after the reveal at 2026-10-15T20:02:44Z.

- **Files:** revision_3 sections appended to 0.md, 1.md and `_difficulty.md`; earlier revisions untouched.
- **Agreement with GT:** both blind derivations equal GT on every scored value, every factor figure and every baseline_result.
- **Scopes:** task 0 = p0–p3, task 1 = p4–p7. Disjoint and complete.
- **Tools:** unchanged since r2 (same hash); uuid8s independent; docstrings carry no ordering or figures.
- **Trees:**
  - Task 0: 3 prerequisite problems, 3 value_input edges.
  - Task 1: 3 prerequisite problems, 2 value_input edges plus the Estate-minimum state gate.
  - Both roots are owner=user; the difficulty's graph is acyclic.
- **Factors:** 4–6 per computation, at least 2 parameter and 1 honest method in each. Multi-source and cross-difficulty factors are present in each task. Every factor bears weight; every all-baseline figure is definite and differs from gold.
- **Seeds:** legal under the hecm, residency, setaside and maturity charters.
- **XF recipe:** holds. Same-day tie rules are stated and probed wherever a "latest" pick selects a record.
- **Round-2 RED:** R2-N1 closed. All round-1 REDs remain closed; no regression; no new defect.
- **Gates:** green per snapshot_r3; the INVALID result is pre-render only.
- **Remaining observations (no rework):** R2-O2, R2-O3, R2-O4, R2-O5 (blueprint short-sale floor of 88% vs HUD's 95%), R2-O6, and O-5 (proprietary fees).

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN
