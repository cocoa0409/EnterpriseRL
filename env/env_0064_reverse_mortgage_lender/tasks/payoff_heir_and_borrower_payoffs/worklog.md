# Worklog — payoff_heir_and_borrower_payoffs (env_0064)


## REWORK round 2 — audit items closed (audits/policy_task/payoff_heir_and_borrower_payoffs/: _difficulty.md, 0.md, 1.md; plus XF_recipe.md)
- SP-1: approval no longer substitutes max_claim_amount or the closing appraisal; the base sentence "Terms that rely on an appraisal use the latest appraisal recorded on the loan's maturity case ..." is followed, not retired (appraised value basis = case appraisal, 640000.00 in task 0).
- SP-2: relocation allowance removed; no sale policy carries an incentive (payoff_relocation_incentive untouched).
- SP-3: the seller contribution on a borrower short sale is taken before signature only through a declared overwrite of payoff_acceptance's first clause, whose replaced_by restates the in-force rule for every other plan and names its scope; payoff_acceptance added to the policy's base refs.
- SP-4: the short-sale approval now sets contract_price, allowed_closing_costs, required_payoff_amount (scored) and appraised_value_basis; the statement tool no longer sets required to 0.00 and no rule leaves it for a later step.
- SP-5: every maturity read is scoped by maturity_case_id, every residency read by the loan's residency_profile_id, every payoff read by payoff_case_id; the credit tests the latest accepted declaration's stated intent. Decoys seeded and excluded: a cured 2021 maturity case with an extension and notices (task 0), withdrawn earlier payoff cases with a wire and its return (both tasks). Probe: unscoped readings give approval 424435.66 (task 0) and contribution 2736.85 (task 1) instead of 424310.66 / 2721.85.
- SP-6: all eight docstrings rewritten without ordering, prerequisite state or downstream use (no "then", "already recorded", "whose statement has been issued", "once ... reviewed").
- SOURCE-CHAIN (task 1): persona no longer says Cedarline "has to sign off on the sale"; no_user_hint rewritten and true.
- SF-1: approval is HUD's due-and-payable payoff, lesser of the amount owed and 95% of the current appraisal (24 CFR 206.125(c)); no occupancy percent ladder, no flat charges above the cap; company items (resolution charges, credit) act only on the balance side and the world has equity (cap 608000.00 > 424310.66).
- SF-2: no inspection-fee factors; every inspection order's fee posts on the HECM the same day in both seeds.
- SF-3: no posting-lag tiers; both ledgers post interest, MIP and fees on the 1st through 2026-10-01; balances reconcile with the postings (O-6).
- SF-4: a Partially Funded LESA pays no bill in any policy (it appears only as a declined-bill tier of the short-sale shortfall); set-aside carries use one joint limit; task 1's LESA is a Fully Funded LESA whose shortfall the seller pays at closing; no paid bills on a partial LESA.
- SF-5: no daily fee share; the servicing fee enters only the statement, once per unposted fee month; per diem interest on set-aside disbursements follows the HECM month-end-basis convention.
- SF-6: remittance ladders rebuilt: distinct tier outcomes, cushion is the only method (time-based vs flat), no uncollected-check or recall-holdback factors; task 1's plan is wire-only and every receipt is a wire.
- SF-7: lien-release charge no longer depends on property type; it counts recorded instruments (lender mortgage and the Secretary's second mortgage for a HECM, plus the trustee certification for a Living Trust profile).
- Plan use: task 1 now uses Approved Short Sale Payoff for the living borrower's below-balance sale (Estate Market Sale no longer used for a living borrower).
- XF recipe: every baseline paragraph defines each quantity of the combination with its default; each factor replaces only its own quantity and acts alone (solo and removal results in the factor cards); combinations stated once with floor-before-add order; no cross-policy definitions; overwrite tails name both scopes where two policies retire one clause; compute_basis quotes swept verbatim by script (0 misses); absent-record / None / zero branches stated (no sentinels).

## Task 0
WORKLOG task 0 (payoff_heir_and_borrower_payoffs, env_0064), REWORK round 2. Draw (draw_counts.py --task 0): prerequisite_problems=3, factor_counts=[6,5,5,6]; assigned daily accrual 5, statement 6, approval 6, remittance 5.

WHY THIS TEST. Lorraine Whitcombe's HECM matured (Principal Residence Change, called due 2025-12-21, extended once, referred to foreclosure 2026-09-20). She asks to pay it off today and keep her condominium; the scored root is her own wire amount (owner=user). The agent must discover a 3-hop chain she never mentions (daily accrual -> statement -> HUD due-and-payable approval -> remittance), each hop a multi-factor computation over the HECM ledger, the Fully Funded LESA and its bills, the occupancy profile's inspections and the maturity case, then hand the remittance to her. One tool per problem; no near-synonym tools.

SCOPE. Claimed (task 0): payoff_ext_retention_daily_accrual / record_payoff_daily_accrual_16b003bd; payoff_ext_retention_statement_balance / issue_retention_payoff_statement_a856e53a; payoff_ext_retention_payoff_approval / approve_appraisal_based_payoff_a02ac9a5; payoff_ext_retention_remittance / remit_borrower_payoff_funds_17f1493b (owner=user). Scope of all four: a Borrower Voluntary Payoff requested by the borrower of record on a loan whose maturity case is due_and_payable, extension_period or foreclosure_referred. Left for task 1: the Approved Short Sale Payoff chain of a living borrower. Compute constraint: CUST is the payoff requester, so cross-category reads only reach a living borrower's own records; both tasks therefore use a living borrower.

HUD REALISM (SF-1). The approval is HUD's due-and-payable payoff: the lesser of the amount owed (statement plus recoverable resolution charges less a company credit) and 95 percent of the maturity case's current appraisal (24 CFR 206.125(c)); no appraisal substitution (SP-1 closed: the base appraisal sentence is not retired and is followed). In this world the borrower has equity (cap 608000.00 > balance figure 424310.66), so she pays the balance figure, as HUD requires.

FACTOR CARD (tier taken; result with that factor at its standard value; solo = only that factor off standard):
 daily accrual 85.31: retention_setaside_disbursement_carry -> 84.16 (solo 84.96); retention_preservation_advance_carry -> 85.23 (solo 83.89); retention_called_due_appraisal_carry -> 85.30 (solo 83.82); retention_replacement_appraisal_carry -> 85.23 (solo 83.88); retention_foreclosure_charge_carry -> 85.14 (solo 83.98); all standard -> 83.80.
 statement 422545.26: statement_window_days -> 423824.91 (solo 416669.86); statement_tax_disbursement -> 419932.86 (solo 420561.91); statement_hazard_disbursement -> 420577.26 (solo 419917.51); statement_flood_disbursement -> 421405.26 (solo 419089.51); statement_servicing_fee -> 422510.26 (solo 417984.51); statement_maintenance_charge -> 422425.26 (solo 418069.51); all standard -> 417949.51.
 approval 424310.66: approval_called_due_appraisal_charge -> 424235.66 (solo 423095.26); approval_replacement_appraisal_charge -> 423915.66 (solo 423415.26); approval_foreclosure_charge -> 423435.66 (solo 423895.26); approval_property_securing_charge -> 424025.66 (solo 423305.26); approval_notice_postage_charge -> 424275.26 (solo 423055.66); approval_prompt_decision_credit -> 424685.66 (solo 422645.26); all standard -> 423020.26.
 remittance 244233.21: remittance_clearing_cushion -> 243806.66 (solo 244075.21); remittance_wire_receipt_fee -> 244203.21 (solo 243678.66); remittance_returned_item_fee -> 244208.21 (solo 243673.66); remittance_release_title_search -> 244178.21 (solo 243703.66); remittance_release_recording -> 244185.21 (solo 243696.66); all standard -> 243648.66.
 Tiers: LESA (Mandatory) active, bills tax 2612.40 pay-by 2026-10-28 / hazard 1968.00 pay-by 2026-10-21 / flood 1140.00 pay-by 2026-11-08 within the 30-day statement period; latest inspection 2026-09-29 vacant on profile c337ab71, condominium (securing 285.00 + flat maintenance 120.00); called-due appraisal 550.00 (condominium); replacement appraisal 395.00 (2026-09-30 appraisal 283 days after the call, not within 30 days of the 2026-06-10 extension); foreclosure 875.00 (referred 24 days); window 15 days (foreclosure_referred); one fee month 35.00; notices 4 -> 35.40; timely retain declaration with one extension -> credit 375.00; cushion 5 x 85.31; 4 wires -> 30.00; recalled wire -> 25.00; closed 2016-04-28 (125 months) -> 95.00; HECM, standard profile -> 2 x 48.00.
 Near-misses: flood pay-by 2026-11-08 falls after the 2026-10-29 good-through date but inside the 30-day statement period, so it is carried; paid bills excluded by request_status; the cured 2021 maturity case (its extension and notices) excluded by maturity_case_id; the withdrawn March payoff case's wire excluded by payoff_case_id; the 2026-10-09 Dana wire is recalled (returned) but still counts as a wire receipt.
 Every factor moves its result alone and on removal (solo / removal tests above); each baseline paragraph defines every quantity of the combination with its standard value; combinations stated once; caps/floors stated in the rule.

BASE-INVARIANT CARD. payoff_statement_terms.authorized_request_on_file: request ac5e47ef payoff_statement_request received 2026-10-07 by the borrower (statement within 7 business days: Oct 8, 9, 13, 14; Oct 12 Columbus Day excluded). appraisal_current: appraisal 2026-09-30, valid 6 months (Principal Residence Change appraisal_valid_months 6). payoff_sale_review.contract_on_file: carried as in round 1 (policy_scope). payoff_agg_funds.remittance_once: retired for the borrower's own remittance by the declared overwrite (reference issued by the servicer). BVP acceptance_required false, so funds need no signature.

BUSINESS-OBJECT CARD. Object: open BVP case a9f3281e (loan a6d59105, maturity 18dfafbf). Receipts counted: 7 receipts and 1 return on that case only (net 180750.00). Excluded: the withdrawn March case 333c70bd-3b27-4cc2-b73a-854c6bc18038 (by payoff_case_id), the cured 2021 maturity case (by maturity_case_id), paid bills (by status).

PERSONA. Polite, anxious retired librarian; volunteers name, the foreclosure letter, the goal (pay off today, keep the condo, be told the amount, wire from own savings in own name). Phone and SSN only on request; occupancy, Dana's wires and her own checks only when asked; generic consent when told something must be prepared; one re-check request if the figure seems large; sends the wire on hand-over; ends when told the money is received. No prerequisite named (closes the round-1 SOURCE-CHAIN pattern).

PROBLEM TREE CARD. root payoff_ext_retention_remittance; edges R->P (required_on_case), P->A (stmt_on_case), A->X (per_diem_on_case), all value_input, state form (sentences in prerequisite_closure). Opening evidence: per_diem 0.00, status opened, statement 0.00, appraisal basis and required 0.00. Deletion sensitivity: skip X -> statement 420156.58; skip A -> approval 1765.40; skip P -> remittance 242467.81; root on the opening world 246.00. Each state is brought about by exactly one write of this difficulty within the retention scope (the short-sale tools write the same fields only on Approved Short Sale cases).

PROBES (decoy / absent / edge, rule-equal outcomes): second received tax bill with an earlier due date -> the latest-due bill is counted, per diem unchanged 85.31; no inspection result -> preservation carry 0.00, per diem 85.23; no nonoccupancy_date -> one month (condominium flat unchanged) 422545.26; foreclosure_referred without referral_date -> counted 0 days, initial charge, approval unchanged; extension_period with deadline 10 days out -> window 10, statement 422118.71; later accepted sell_property declaration -> credit 0.00, approval 424685.66; LESA balance 3000.00 -> disbursements limited in type order, statement 419824.86; returned cashier's check -> 35.00 fee, remittance 244243.21; a customer-wide (unscoped) reading of the extensions would count the 2021 extension and give approval 424435.66, which the case-scoped rule excludes.

STANDARD SOLUTION / WRITES. 1 record_payoff_daily_accrual_16b003bd per_diem_amount 85.31; 2 issue_retention_payoff_statement_a856e53a good-through 2026-10-29, balance 422545.26; 3 approve_appraisal_based_payoff_a02ac9a5 basis 640000.00, required 424310.66; 4 (user) remit_borrower_payoff_funds_17f1493b wire 'Lorraine Whitcombe' 244233.21. Verification: /tmp scratch harness replays the real tools and evaluates every compute on handling-time worlds; outputs equal computations and gold.

## Task 1
WORKLOG task 1 (payoff_heir_and_borrower_payoffs, env_0064), REWORK round 2. Draw (draw_counts.py --task 1): prerequisite_problems=3, factor_counts=[4,6,6,6]; assigned daily accrual 6, statement 6, short-sale approval 6, seller contribution 4.

WHY THIS TEST. Raymond Tolliver, a living borrower in assisted living, is selling his vacant duplex below the balance (690000.00 against a statement balance of 764632.62 and an appraisal of 740000.00) while the loan is referred to foreclosure. The plan used is Approved Short Sale Payoff, open to the borrower by its entry gate; the Estate Market Sale plan (estates) is no longer used (closes the round-1 plan-situation note). He asks only to wire what he must put in so the sale closes; the scored root is his own wire (owner=user). The agent must discover daily accrual -> statement -> short-sale approval -> contribution, each a multi-factor computation, and hand over the wire.

SCOPE. Claimed (task 1): payoff_ext_sale_daily_accrual / record_sale_daily_accrual_1c6aaad4; payoff_ext_sale_statement_balance / issue_sale_payoff_statement_764045f1; payoff_ext_sale_cost_allowance / approve_sale_closing_costs_11c6cfd9 (now sets contract price, allowed costs, required payoff and appraisal basis: SP-4 closed); payoff_ext_sale_seller_shortfall / remit_seller_closing_shortfall_d501bd8d (owner=user). Scope: an Approved Short Sale Payoff requested by the borrower of record. Task 0 holds the retention chain; scopes are disjoint by plan.

FACTOR CARD (result with that factor at its standard value; solo = only that factor off standard):
 daily accrual 127.37: short_sale_setaside_carry -> 127.06 (solo 126.96); short_sale_securing_carry -> 127.32 (solo 126.71); short_sale_maintenance_carry -> 127.24 (solo 126.79); short_sale_called_due_appraisal_carry -> 127.34 (solo 126.69); short_sale_replacement_appraisal_carry -> 127.32 (solo 126.71); short_sale_foreclosure_carry -> 127.22 (solo 126.81); all standard -> 126.66.
 statement 764632.62: short_sale_statement_setaside -> 762832.62 (solo 762202.62); short_sale_statement_fee -> 764602.62 (solo 760432.62); short_sale_statement_preservation -> 763577.62 (solo 761457.62); short_sale_statement_called_due_appraisal -> 764457.62 (solo 760577.62); short_sale_statement_replacement_appraisal -> 764337.62 (solo 760697.62); short_sale_statement_foreclosure -> 763757.62 (solo 761277.62); all standard -> 760402.62.
 approval 621183.34: short_sale_commission_allowance -> 617733.34 (solo 631302.00); short_sale_other_cost_allowance -> 622483.34 (solo 626552.00); short_sale_property_charge_shortfall -> 624529.00 (solo 624506.34); short_sale_release_allowance -> 621231.34 (solo 627804.00); short_sale_postponement_allowance -> 621433.34 (solo 627602.00); short_sale_marketing_allowance -> 626358.34 (solo 622677.00); all standard -> 627852.00.
 contribution 2721.85: contribution_clearing_cushion -> 2085.00 (solo 2626.85); contribution_wire_fee -> 2706.85 (solo 2005.00); contribution_returned_item_fee -> 2696.85 (solo 2015.00); contribution_title_search -> 2666.85 (solo 2045.00); all standard -> 1990.00.
 No relocation allowance (SP-2 closed). The acceptance sentence is retired only for the seller's own contribution on a borrower short sale, with the in-force wording restated (SP-3 closed). Wire-only plan: every receipt is a wire (SF-6 closed). LESA bills are paid by a Fully Funded LESA whose balance runs short; the shortfall is the seller's (setaside shortfall rule), not projected twice (SF-4 closed). Postings on the 1st through 2026-10-01; inspection fees posted the day ordered (SF-2/SF-3 closed).
 Near-misses: the recalled 1000.00 wire still counts as a wire receipt but not as held funds; the February case's wire and return are excluded by payoff_case_id; paid bills excluded by status; the 2025 appraisal is not on the case (only the 2026-07-14 update).

BASE-INVARIANT CARD. authorized_request_on_file: request fc080b19 received 2026-10-06 (statement within 7 business days); the statement recipient overwrite admits the borrower on his own short sale. appraisal_current: 2026-07-14, within 6 months. contract_on_file: contract 6296dd89 received 2026-10-08, reviewed within 10 business days; arm's length; price 690000.00 >= 88% x 740000.00 and below the Estate Market Sale minimum 703000.00; listed 2026-03-20, at least 30 days before.

PROBLEM TREE CARD. root payoff_ext_sale_seller_shortfall; R->B value_input (allowed_on_case), B->A state_gate (payoff_cases.statement_balance), A->X value_input (per_diem_on_case). Skip X -> statement 759028.34; skip B -> contribution 771.85; skip A -> approval may not be made; root on the opening world 135.00.

PERSONA. Dry-humoured retired machinist; volunteers the sale below the balance, the foreclosure letter and the wish to wire his own share today; identity on request; Marcus's and his own recalled wire, the buyer and the vacancy only when asked; generic consent; one re-check; wire on hand-over; ends on receipt. It no longer says Cedarline 'has to sign off on the sale' (round-1 SOURCE-CHAIN closed).

WRITES. 1 record_sale_daily_accrual_1c6aaad4 127.37; 2 issue_sale_payoff_statement_764045f1 good-through 2026-11-14, balance 764632.62; 3 approve_sale_closing_costs_11c6cfd9 contract 690000.00, allowed 59950.00, required 621183.34, basis 740000.00; 4 (user) remit_seller_closing_shortfall_d501bd8d wire 'Raymond Tolliver' 2721.85.

## Probe tables
Task 0: older received tax bill -> latest-due bill counted, per diem 85.31; no inspection result -> 85.23; no nonoccupancy_date -> 422545.26; referral without date -> approval 424310.66; extension 10 days out -> statement 422118.71; later sell_property declaration -> approval 424685.66; LESA 3000.00 -> statement 419824.86; returned cashier's check -> remittance 244243.21.
Task 1: Partially Funded LESA with declined bills -> approval 621623.34, per diem 127.06; no contract -> required 0.00; no listing_date -> 626358.34; extension_period instead of referral -> contribution 2185.00; price 1050000.00 -> 975033.34; Living Trust profile -> 621135.34.

## Gate block (full, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK
SOLVABILITY OK
COMPUTE OK
GROUNDING OK
SCOPE OK
check_traceability: 8 misses, all unlock_*_tool tool_name values (pre-render, expected); 0 other misses.

REWORK round 2: gates 7/7 green

## REWORK round 3 — items (audits revision_2: R2-N1 RED; observations R2-O1..O6, persona note)
- R2-N1: p3/p7 excess-refund overwrite no longer retains the cushion: "the remittance charges collected with the borrower's own remittance, other than its clearing cushion, are then retained ...; the clearing cushion, per diem collected in advance, is kept only for the per diem the case owes for each day its funds were credited after the statement's good-through date, per interest_through_basis; any held excess left, an unused cushion included, is refunded". The cushion is moved out of the retained-charge list in each baseline ("shortfall plus the clearing cushion plus four remittance charges" / "plus the contribution cushion plus three contribution charges") and each cushion factor states it is collected in advance and refunded to the extent unused. Factor floors kept (p3 5, p7 4; cushion still the method factor); scored values unchanged (244233.21, 2721.85).
- R2-O1: p4 maintenance carry now keyed on the latest inspection result found vacant (same as p5's preservation charge).
- R2-O2: p3/p7 title search: 'a loan with no closing_date counts 0 months' stated.
- R2-O3: 'set out in this policy' removed from p0/p4 rule and replaced_by.
- R2-O6: splice artefacts fixed (p6 'The required payoff amount ...', p7 acceptance clause ends with a full stop).
- R2-O4/O5: unchanged (projection convention; blueprint short-sale floor).
- Persona task 0: 'a couple of wires' (two wires from her in the records).
- Same-day ties: bills of one type on the latest due_date summed (XSUM, stated in p0/p1/p4/p5/p6, declined bills in p6 too); inspection results on the latest date: vacant, then unable_to_determine, then the latest (p0/p1/p2/p4/p5); intent declarations on the latest date: retain only if all retain (p2); fee period by latest accrual_period (p1/p5); p6 approves only with exactly one received contract; p7 reads the latest accepted request_date, largest commission and other costs among same-day accepted contracts. All compute_basis quotes re-swept verbatim (0 misses).
- Probes (gold -> probe): t0 same-day occupied_by_others result 85.31 -> 85.31; t0 second same-due tax bill 85.31 -> 85.41; t0 same-day sell declaration 424310.66 -> 424685.66; t0 duplicate 2026-09 fee 422545.26 -> 422545.26; t1 second received contract 621183.34 -> 0.00; t1 same-day accepted contract (commission 42000.00) 2721.85 -> 3321.85; t1 latest inspection occupied_by_others 127.37 -> 127.19; t1 no closing_date 2721.85 -> 2666.85.


## Gate block round 3 (full, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK
SOLVABILITY OK
COMPUTE OK
GROUNDING OK
SCOPE OK
check_traceability: only unlock tool_name misses (pre-render); 0 other misses.

REWORK round 3: gates 7/7 green
