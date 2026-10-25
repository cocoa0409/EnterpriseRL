# worklog — financial_assistance_screening (category `assist`), M=2

## Step 0 — difficulty pre-check (2026-10-20)

Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/assist.yaml,
db_schema.json (customers, assistance_*, encounter_*, claim_*, plan_*, estimate_*), share_tools.py,
audits/render_source/XF_recipe.md (27 points; applied to every policy and seeded row below).

Draw (scripts/draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3, factor_counts=[4, 6, 5, 6]
- task 1: prerequisite_problems=1, factor_counts=[6, 4]

### Writable events and their numeric fields (claim of this difficulty)
assist_application_received (create / merge into open case), assist_household_updated (update),
assist_approved, assist_documents_requested, assist_documents_completed, assist_denied,
assist_reconsideration_opened, assist_withdrawn, assist_document_logged, assist_notice_sent,
assist_eca_action_logged.
- NOT writable: assist_encounter_applied and assist_adjustment_reversed — both declare
  unconditional `triggers` into `encounter` (encounter_adjustment_posted / encounter_liability_posted);
  skill Principle D + recipe E23 forbid any task tool writing them. (Also not in the blueprint claim.)
- Scored numbers can only land on case fields: household_size, annual_household_income_usd,
  household_fpl_pct, qualifying_medical_debt_usd, liquid_assets_usd, hardship_liability_cap_usd,
  documents_due_date (date; DSL has no date-add, so a deadline must be scored as a whole-day count
  the tool turns into the date). Notice/document/ECA rows carry amount 0.00 by schema meaning (E24).
- Patient-owned acts (blueprint): signing the application attestation (assist_application_received,
  incl. the "added to the open case as supporting information" path of assist_agg_multi_holding)
  and withdrawing. Withdrawal carries no number, so every task's owner=user problem is a signed
  application/supplement/renewal whose computed field must be derivable from the records: only the
  medical-debt figure is (Riverbend's own ledgers); income/size/assets have no record source.

### BLUEPRINT-KNOWN (logged for the coordinator, not a stop)
The base's factor-rich computation (AGB / patient-responsibility charge basis x tier discount,
hardship cap, refund >= $5) lands on assist_encounter_applied, which no tool may write. What remains
numeric is thin; with two tasks each needing an owner=user problem with its own 4-6 factor
computation, the only record-derivable patient-signed figure is claimed medical debt, so both user
problems claim medical debt (on a hardship supplement, and on a renewal application). Routed around
inside extended policies; see design per task.

### Base automatic clauses to keep un-ignited in every seed
- encounter statement cycle / placement / credit reporting (no account seeded in bad_debt or past a
  FINAL_NOTICE unless an ECA_SUSPENSION_NOTICE for it is already logged on the case);
- assist pending_documents -> denied after the deadline (no seeded case past its documents_due_date);
- award expiry (no approved award past award_end_date);
- plan missed-installment / default (any seeded plan current);
- refunds of credit balances (no unrefunded credit older than refund_issue_days).

### Claim plan (Principle C) — both tasks, drafted together for headroom (current after rework round 3)
Tools (uuid8 generated one per tool): sign_hardship_supplement_15cad132 (user), record_qualifying_debt_da5f54be,
record_documented_costs_4c71e2b9, approve_hardship_award_afb08b0b (task 0); sign_renewal_debt_claim_3b9e07c1 (user),
send_missing_information_notice_7f5665e5 (task 1). (Earlier drafts: file_renewal_application_f2cfad6f, replaced in the task 1
build; record_countable_assets_effcaeaa, removed in rework round 3 / C15.)
- task 0 (first Medical Hardship award, all care at Riverbend, approval in this call), root = hardship cap:
  assist_ext_supplement_debt_claim (U, state form) -> assist_ext_qualifying_debt (A, action form)
  -> assist_ext_other_costs_debt (A, action form) -> assist_ext_hardship_cap (A, root).
- task 1 (renewal of an expiring hardship award filed in the portal; renewal case needs documents), root = response window:
  assist_ext_renewal_debt_claim (U) -> assist_ext_response_window (A, root).
Headroom: task 0 claims supplement / own-charge documentation / other-cost documentation / cap; task 1 keeps the renewal's
signed claim and the missing-information notice (documents_requested), disjoint events and tools.

### Factor plan (final ids after rework round 3; every factor reads history / a date span / another category)
A1 holds: no factor binding reads another factor's binding (mechanical check, 0 violations in all six policies).
- assist_ext_supplement_debt_claim (U, 4): appeal_holdout (P), hold_holdout (M), coverage_gap (P; designated
  coverage-terminated account, AGB only when emergency / medically necessary), gfe_dispute (P).
- assist_ext_qualifying_debt (A, 6; Riverbend's own charges at the FAP charge basis, gated on a complete application):
  selfpay_basis (M), gfe_account_basis, gfe_undisputed, unbilled_selfpay, package_rendered, course_in_progress.
- assist_ext_other_costs_debt (A, 5; other medical costs of the window): rendered_care (M), insured_pending,
  coprovider_rendered, appeal_overdue, hold_restore.
- assist_ext_hardship_cap (A, 6, root T0): household_points, plan_burden_points, fixed_income_points, coverage_points,
  burden_share, savings_increment (M). Base asset test unchanged.
- assist_ext_renewal_debt_claim (U, 4, T1): renewal_appeal_holdout, renewal_hold_holdout, renewal_coverage_gap,
  renewal_gfe_dispute (same schedule as the supplement, worded for renewals).
- assist_ext_response_window (A, 6, root T1): period_reach (M), outside_bills_days, pending_claim_days, treatment_days,
  appeal_days, account_count_days.
BLUEPRINT-KNOWN realism note: the cap/assets/qualifying/window ladders are Riverbend-own published schedules
(no federal rule sets those figures); federal figures (HHS guideline, 240/120-day periods, AGB) are used as is.

## Task 0 — build log
- Charter fragments drafted (claim 4 / qualifying 6 / assets 5 / cap 6; renewal claim 4 / window 6); compute_basis and
  baseline sentences verified verbatim against each rule by a scratch checker (B11).
- task_tools.py written (6 tools); check_task_tools: TASK TOOL CONTRACT OK. Docstrings carry no ordering words and no
  example values (E21); no clock/random tokens; date arithmetic in a class static helper (E18).
- T0 world seeded (scratch generator): 10 hospital accounts priced per the encounter/claim charters, 7 claims, the
  Riverbend Hardship Payment Plan with add-on recomputation, 6 estimates, the open Medical Hardship case.
- Scratch evaluation with check_compute's own engine (frozen 2025-10-21):
  claim 20772.80 (baseline 31932.30); qualifying 25247.47 (baseline 20772.80); countable assets 22660.24
  (baseline 44600.00); cap 7479.66 (baseline 11280.00). Every factor's baseline substitution moves its result.
  Revision: cap burden thresholds set to 21/35 percent (the 40/60 draft left the customer on the fall-through).
- Completeness overwrite of the cap policy re-keyed to the patient responsibility posted in the twelve months before
  the application date net of adjustments (33091.48 > 22560.00), so the T0 case is complete at the opening (the recorded
  debt is 0.00 then); cap policy now also states that the encounter charity adjustments are booked in the posting cycle,
  not on the call (BLUEPRINT-KNOWN route-around: no tool writes assist_encounter_applied).
- Read nodes added for billing inquiries, appeal authorizations and plan ledger so the closure equals the seed (161 rows);
  empty FK strings set to null (90 dangling FKs fixed).
- Skip runs: qualifying without supplement 4474.67; cap without documentation 8241.06; cap without countable assets 12964.60.
- Probes (17, table in tasks/0.json design_rationale): all decoys leave values unchanged; absent records fall through
  without exception; one decoy first mis-built (payment of another patient on this patient's account) and rebuilt.
- Task 0 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Task 1 — build log
- First draft: the renewal tool created the renewal case in-call. check_compute looks the computation's target holding
  up in initial_state only, so a computation on an in-call case cannot pass its cross-category floor. Restructured: the
  renewal is filed through the portal before the call (renewal case seeded, debt 0.00) and the patient's owner=user write
  is the renewal's signed claim of medical debt (sign_renewal_debt_claim_3b9e07c1, updates the case). The renewal rule now
  says the renewal case carries no medical debt until that claim is signed; the BadgerCare notice tier reads the renewal case.
- outside_bills_days reworked so the skipped claim (0.00) changes the window: tiers now read the claim against a quarter of
  the hardship share plus outside bills received on the renewal case (the co-provider estimate read dropped; estimate no
  longer a window cross category).
- Scope guards added so no task owes another task's write: the supplement excludes renewal applications; qualifying debt and
  countable assets apply once an application is complete (T1's renewal is incomplete); cap and countable-asset schedules
  carry the 2025-10-01 effective date (T1's 2024 award keeps the base cap 9960.00).
- World (frozen 2025-11-18 14:05:00 CST): six accounts priced per charters, five claims (provider reconsideration pending on
  the June surgery claim, PR-27 coverage-terminated May visit), Assistance-Linked plan with two add-ons, closed imaging
  package estimate for the elective MRI, approved award applied to four accounts (6118.50 of 9960.00 used), renewal reminder.
- Values: renewal claim 5094.94 (baseline 7013.50); response days 165 (baseline 30), due 2026-05-02. Skip run: without the
  claim, 171 days. Every factor's baseline substitution moves its result.
- Probes (16, table in tasks/1.json design_rationale): decoys unchanged; absent records fall through without exception;
  date edges follow the rule words (120 days -> tier 1, 14 days -> near, 4980.00 -> at least a quarter).
- Task 1 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Final gate block (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

INSTANTIATE round 1: gates 7/7 green

## Rework round 2 — response to audits/policy_task/financial_assistance_screening (item → change → where)
Values now: T0 claim 27248.02 → documented debt 34979.79 → countable assets 13060.24 → cap 5579.66 (award 2024-08-26..2026-10-21, English);
T1 renewal claim 5195.68 → notice 155 days (due 2026-04-22), Spanish, four documents REQUESTED. Skip runs: T0 7731.77 / 6341.06 / 8514.60; T1 161.
- C1 (undeclared debt-window / incurred-debt override) → declared overwrite of assist_tier_determination's debt clause in
  assist_ext_qualifying_debt; replaced_by scopes applications recorded under Riverbend's hardship schedules (supplement, renewal
  claim, documentation) and restates "incurred in the last hardship_debt_window_months before the application date" for every
  other application; the documentation rule names what it counts (older balances, scheduled/prepaid/planned care, co-provider
  charges, overdue-appeal cost sharing). Class closed: every policy's figure that the hardship test reads is covered by that scope.
- C2 (asset test) → declared overwrite of "where liquid_asset_test_applies is true, liquid assets do not exceed
  liquid_asset_limit_usd" in assist_ext_countable_assets (scoped; out-of-scope restates documented liquid assets); world: T0
  documented assets 24800.00 (under the 25000.00 limit), so the base clause does not bite either way.
- C3 (renewal FPL) → renewal rule recomputes the household percent on the HHS guideline in force on the renewal's application
  date; T1 renewal case 470.9 (99600.00/21150.00).
- C4 (effective-date clause without compute) → countable-assets and cap schedules carry schedule_effective_date with an
  on_schedule compute binding on the recording/determination day (pre-date recordings = documented assets / base cap); the
  "recorded on a case before that date" wording removed. T1's 2024 award (base cap 9960.00, documented 14300.00) is consistent.
- C5 ("payments made since it") → spending adjustment worded only as the whole-month span ("no more whole months before the
  recording day than the statement's acceptance date is, so a payment dated earlier in that span is included").
- C6 (outside bills status) → window counts OUTSIDE_MEDICAL_BILLS rows with status RECEIVED ("logged as received"); QD likewise.
- C7 (edge inputs) → course_planned: no scheduled first visit → nothing (rule + compute, no DAYS(None)); package pick within a
  variant = estimate listed first; insurer_waiting (multi-match pend_est, AGB-of-gross O3) removed.
- C8 (month-end convention) → every whole-month read site states "a whole month running from a day of one month to the same day
  of the next month or, when the next month has no such day, to the first day of the month after it" (supplement, renewal, QD
  older balances and overdue appeal, assets span, cap coverage points, kept share, completeness overwrite, window account count).
- C9 (assembly sentences naming factor quantities) → generic assembly sentences with generic order in all six rules.
- C10 (shared convention sentence) → cap coverage points and kept share each state their own whole-month sentence.
- C11 (dependency restated on the depended-on side) → "Before a Medical Hardship determination" removed from QD and assets.
- C12 / O1 / O5 (QD prerequisite) → state form: "The qualifying medical debt is documented only once the case records a medical
  debt the patient claims (a case showing 0.00 records none)"; condition and effect restated generally.
- C13 (paused plan framing) → plan factor removed from the window; replaced by pending_claim_days (claims in submitted/accepted
  status). S1-1: the 2025-11-15 installment is no longer drawn (paused while the renewal is submitted); plan re-priced.
- F1 (period_reach one formula) → tier 1 = days left of the application period + the standard 30; tier 2 = MX(30, days left);
  tier 3 = 30 (they differ on tier 1's own domain); C14 table in tasks/1.json.
- F2 (autopay reserve) → plan_reserve keyed on remaining balance vs reserve_months installments (3 installments / remaining
  balance / none); autopay no longer read.
- F3 (AGB on co-provider bills) → coprovider_charges replaced by coprovider_procedure (completed estimate, no outside bills
  received → co-provider lines; issued estimate for a scheduled procedure → Riverbend's convening lines; else 0).
- F4 (plan tier as income-loss evidence) → income_loss_points replaced by plan_burden_points (active plan installment as a
  percent of monthly income: above 5 → 2.0, above 2 → 1.0).
- F5 (patient-wide elective switch) → selfpay_basis / renewal_selfpay_basis removed; method factor now hold_holdout (charge
  dispute: MN(disputed line charge, held liabilities); itemization: coinsurance; none) and a new parameter factor gfe_dispute
  (No Surprises Act patient-provider dispute: in dispute → billed charges off; completed with excess >= $400 inside 120 days →
  excess off). QD gains appeal_overdue (ACA 60-day post-service internal-appeal decision time).
- S0-1 → T0 co-provider estimate total = sum of its lines (12500 + 400 + 1180 + 360 = 14440.00).
- S1-2 → T1 coverage-terminated May visit: financial class SELF_PAY, coded elective (so the award does not charity-adjust it).
- Seed re-pricing (C3/S-class): T1 ED and surgery remits, plan installments/add-ons, the MRI moved to a disputed self-pay GFE
  (elective imaging discount 25%), award applications on the three insured accounts (5738.50 of 9960.00); T0 member appeal and
  authorization dated 2025-08-21.
- O2/O3/O4/O6: anticipated_care kept (C14 table); insurer_waiting removed; retirement/disability protections re-set as
  Riverbend's own amounts (5000/2500); provider reconsideration on an adjudicated underpaid claim kept (claim charter allows).
- Rationale "earliest row 2024-04" corrected (2024-09-03). Stale-text sweep of every proof/trace/necessity/objective string done.
- Probes re-run for every read (25 in task 0, 20 in task 1; tables in each design_rationale); XF points A1–F27 re-applied to all
  six policies (A1 checked mechanically: no factor binding reads another factor's binding; compute_basis/baseline/policy_source/
  replaced_by verbatim sweep: 0 problems).
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

REWORK round 2: gates 7/7 green

## Rework round 3 — response to revision_2 (C14, C15, F6)
- C14 (rule defers to a clause its own overwrite retires) → CLOSED. QD overwrite scope now excludes cases with an outside
  medical bills document accepted, and both the replaced_by and the rule restate the in-force content for them ("the
  documented medical bills, Riverbend and outside, incurred in the last hardship_debt_window_months before the application
  date") instead of "documented under the base rule". Class sweep: the cap's completeness overwrite no longer says "stays
  under the base completeness rule" (it points to its own restated last clause); the cap and countable-assets overwrites
  already restate base content; the window overwrite restates the base due date. One stale tracing line in tasks/1.json
  updated. No gold moves.
- C15 (frozen field meanings) → BLOCKED, coordinator decision needed. Analysis:
  * liquid_assets_usd = "documented liquid assets". The records hold no holdings breakdown (document rows carry no amounts,
    by schema "0.00 for documents"; no table holds account balances or account types), so no record-based ladder can decide
    which documented holdings count as liquid. A semantics-correct countable-assets computation can carry at most the
    documented balance brought forward by documented Riverbend payments (one method factor) plus definitional exclusions
    such as current-period income: 2-3 record-based factors, not the 4-6 the draw requires.
  * qualifying_medical_debt_usd = "documented medical bills ... incurred in the hardship debt window". Removing future care
    and older balances leaves QD with the overdue-appeal and rendered co-provider items (plus a pending insured account):
    about 3 factors with genuine three-way ladders.
  * Task 0's draw is fixed at 3 prerequisites and factor counts [4, 6, 5, 6]. With the cap at 6 and the supplement at 4-5,
    QD and the asset write would have to carry 5 and 6 factors under the frozen meanings. The category has no other field a
    task tool may write (assist_encounter_applied and assist_adjustment_reversed trigger encounter events, XF E.23), so no
    other prerequisite can replace them.
  * Options: (a) the coordinator rules that the declared overwrites (QD debt clause, asset-limit clause) govern how those
    fields are filled in scope; (b) a blueprint change adding document amounts or a holdings record (the blueprint is
    frozen); (c) a redraw of task 0 to fewer prerequisites.
  Nothing was changed for C15 this round, so that no passing material regresses while the decision is pending.
- F6 (AGB valuation regardless of classification) → BLOCKED with C15. Analysis:
  * The compute DSL cannot sum per account by service classification (no iteration over holdings; XSUM filters only on
    event-row fields, and liability rows carry no classification), so "AGB for emergency/medically necessary accounts,
    as posted for elective accounts" can only be written for a single designated account.
  * Task 1's coverage-terminated account is elective by design (S1-2, so the expiring award does not charity-adjust it).
    Under F6 its debt is valued as posted, so renewal_coverage_gap no longer bears weight there.
  * Recoding the account as medically necessary brings the award's charity adjustment, which double-counts against an AGB
    take-off.
  * Replacement factors considered all conflict with an owning charter:
    - coverage-update rebill: the payer timely-filing limits (120/180 days) have passed in both worlds;
    - pending replacement claim: a replacement is filed only from adjudicated, and claims close at zero payer balance;
    - BadgerCare retro: the rebill transfer already removes the debt.
  * course_planned tier 2 (QD) is also an F6 member; it falls away with the C15 rework of QD.
  * Proposed, pending the C15 decision:
    - Supplement: coverage_gap keyed on the account of the first PR-27 claim, applying the AGB share only when that account
      is coded emergency or medically necessary, otherwise as posted. Task 0 stays on the same tier and value.
    - Renewal: a replacement fourth factor agreed together with the C15 route.
- Gates re-run after the C14 edit: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK. Gold unchanged (T0 27248.02 / 34979.79 / 13060.24 / 5579.66; T1 5195.68 / 155).
- (superseded below) Interim status at that point: C14 closed; C15 and F6 open pending coordinator decision.

## Rework round 3 (continued) — coordinator rulings applied ((a)(b)(c) rejected; Route 1 and Route 2 accepted; Route 3 rejected)
- C15 (frozen field meanings) → CLOSED via Route 1. Every write stores its frozen meaning:
  * assist_ext_countable_assets and record_countable_assets_effcaeaa removed. The cap applies the base asset test
    unchanged; the cap rule says "documented liquid assets".
  * qualifying_medical_debt_usd is written by a documentation chain. Every tier is a documented medical bill incurred in the
    hardship debt window, and every tier is a schedule a real hospital could publish. No tier adds back prompt-pay or
    goodwill reductions.
    - supplement (signed claim)
    - -> record_qualifying_debt_da5f54be: Riverbend's own charges at the FAP charge basis (AGB only for emergency /
      medically necessary care; 501(r)(5)). Completeness-gated: income document + residency + bank statement accepted.
    - -> record_documented_costs_4c71e2b9 (new assist_ext_other_costs_debt): co-provider, insured-pending, overdue-appeal
      and released-hold items. Action-form prerequisite with a fallback_reason.
    - -> approve_hardship_award_afb08b0b. The cap prerequisite is now a single action edge on the completed documentation.
  * Task 0 world: new pending accounts E11–E14 (elective lesion removal, imaging package with X3 completed, rehab course
    with X6 from 10-06 and issued 09-30, Holter with single-service GFE X7). Further edits:
    - X2 is in dispute since 10-14 and E4 is held on GFE_DISPUTE_PENDING;
    - the E6 inquiry was resolved with no change;
    - the E2 stay moved to 06-26/27, and the plan installments were re-priced.
    Seeded cross-category rows re-checked against the encounter, claim and plan charters.
- F6 (AGB regardless of classification) → CLOSED. coverage_gap and renewal_coverage_gap read one designated account (the
  most recent COVERAGE_TERMINATED liability, ties keep the first row). They apply the AGB share only when that account is
  not ELECTIVE_NON_COVERED; liabilities on other accounts stand as posted.
  * Task 0 stays on the same tier and value (274.68).
  * Task 1 (Route 2): new medically necessary SELF_PAY account E8 (May 2 clinic, 830.00). The NH claim's PR-27 posted
    2025-11-17, after the expiring award's last posting cycle, so no award adjustment applies. Touched rows were re-priced;
    the window factors were re-checked (155 unchanged).
- C14 stays closed. The class sweep was repeated on the new overwrites:
  * the QD debt clause's replaced_by restates the base for every application outside its scope;
  * the cap completeness parenthetical restates its own last clause.
- Probes were run on the touched reads (decoy / absent-record / incomplete-application). Pairwise method tables are in both
  rationales. A stale-text sweep found no "countable assets" or old gold figures left in either task.
- Gold moves:
  * T0: claim 27248.02 → 14348.02; own-charge documentation 34979.79 → 23627.80; completed documentation (new) 29828.98;
    countable assets 13060.24 (removed); cap 5579.66 → 8514.60 (award 2024-08-26..2026-10-21, English).
  * T1: renewal claim 5195.68 → 6254.58; response window 155 unchanged.
  * Skip runs: T0 9279.78 / 20549.20 / 9276.00; T1 161.
- Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: C14, C15, F6.
REWORK round 3: gates 7/7 green

## Rework round 4 — response to revision_3 (C16, C17, F7, F8, S3-1, S3-2; O7–O14)
- S3-1 and F8 (seed rows the encounter charter cannot produce; tier reachable only through them) → CLOSED.
  * World (task 0): the August imaging account no longer carries a charge dispute.
    - The patient asked for an itemized statement on 2025-10-06 (ITEMIZED_STATEMENT_REQUEST, IN_REVIEW).
    - An ITEMIZATION_REVIEW hold was placed the same day. Its length is itemized_statement_collection_pause_days = 30, so it runs to 2025-11-05.
    - The itemized statement was issued 2025-10-09, within 5 business days.
    - Line ec218082 is recoded as a creatinine test (cdm 3010565, CPT 82565, rev 0301, 240.00), so no exact duplicate remains on the account.
  * Charter (assist_ext_other_costs_debt, hold_restore): tier 2 is re-cut to a reachable state.
    - Condition: a self-pay held account on an open charge-dispute hold whose latest inquiry names a charge line.
    - Value: the uninsured-discount part of that line, MN(line charge, held liabilities of the hold window) × the account's uninsured discounts / self-pay final-bill liabilities.
    - Basis: the encounter charter's CHARGE_CORRECTION_ADJUSTMENT lowers the balance only by the credit less the discount.
  * The "resolved with no change" tier is gone.
  * Supplement hold_holdout: definition unchanged; task 0 now takes T2 (coinsurance 28.70).
  * hold_restore: task 0 now takes T1 (+28.70).
- S3-2 (task 1 PR-27 posted on day 196) → CLOSED.
  * The coverage-gap account E8 is re-timed honestly within Route 2:
    - medically necessary clinic visit 2025-10-28, billed to Quartz 2025-10-31 (bill-hold 3 days);
    - PR-27 denial on 2025-11-17, day 17 of the 30 clean-claim days; claim closed with 830.00 released to the patient;
    - Quartz coverage had ended before that date of service (the earlier CT of 2025-10-20 was paid);
    - no award application yet (the last application ran 2025-11-13); no statement yet.
  * The factor still bears weight through a real date (renewal claim 6254.58 unchanged). Window inputs were re-checked: the latest date of service is still 11-09, first statements are unchanged, E8's claim is closed, so 155 is unchanged.
  * Same class swept: the May 14 Network Health PR-27 was day 34 → re-dated 2025-06-13 (day 27). Its first statement moves 06-24 → 06-17; values unchanged.
- F7 (insured pending account valued at a share of gross charges) → CLOSED.
  * insured_pending tier 2 is now "no tied insured estimate, and point-of-service payments posted on the pending insured account → those payments" (the cost sharing collected at the visit). The rule says the addition is the patient's expected share, never an amount the payer is expected to pay.
  * Task 0 stays on T1. Its tied estimate is re-priced by the estimate charter: 20% × 1035.50 = 207.10, see the seeded-row table.
- C16 (one convention sentence serving several factors) → CLOSED in both policies.
  * QD: the shared "For these adjustments …" sentence is removed. Each of selfpay_basis, gfe_account_basis and gfe_undisputed states its own window postings (whole-month and month-end convention), its own bill and AGB share, and its own rounding. unbilled_selfpay and course_in_progress each state their own unbilled charges and rounding.
  * Other costs: rendered_care states its unbilled charges and rounding. appeal_overdue states its appeal window, and hold_restore its hold window, each with the whole-month convention.
  * Every compute_basis quote was re-swept as a substring of its rule (0 misses).
- C17 (pick order and multi-match) → CLOSED, with the class swept over every pick:
  * QD ga_id: "within one variant, an estimate whose service has been completed before a closed one; and among estimates of one variant and status, the estimate listed first among the patient's estimates". This matches the compute order.
  * other_costs cp_id: "an estimate whose service has been completed before one in dispute and, among several of the same status, the estimate listed first".
  * ip_est and sg_id: "the estimate listed first among the patient's estimates when several are".
  * gu_id, rc_id, pk_id and cs_id are restated with "listed first". Probes show the stated order wins (see rationale tables).
- O13 → CLOSED. The record_documented_costs_4c71e2b9 docstring and receipt no longer say "completes/completed"; they read "records … the qualifying medical debt documented with …". The tool has no ordering words.
- O14 → CLOSED. "Complete" now has one meaning: the base completeness and the cap's scoped overwrite of it.
  * QD: "This schedule documents a case once an income document …, a proof of residency and a bank statement have each been accepted on it; a case lacking any of the three keeps the medical debt claimed on it."
  * other_costs: scoped to the same three accepted documents. The word "complete" is no longer used for this gate.
- O12 → CLOSED. The other_costs framing now reads "amounts the claim set aside that Riverbend's records show the patient still owes". This covers overdue-appeal cost sharing and the hold add-backs.
- O7 (answered). On a renewal case, the state the QD edge waits on is brought by the renewal claim. Per case the records select exactly one writer: the supplement excludes renewals, and the renewal claim exists only on renewals. The task-0 tree's edge declares the writer used on its world; the resolved_by field holds one tool.
- O8 (answered, kept). appeal_overdue exists for an insurer past its post-service decision time. Under the ACA, a missed deadline is a real event: the claimant may treat internal appeals as exhausted. The earliest such state is day 61, so the world sits on it. The claim charter states the 60 days as the payer's obligation, not as a lifecycle transition; the rule calls the tier overdue and the probe shows day 60 adds nothing.
- O9 (answered). The debt-test departure for every Riverbend schedule is declared once, in QD's overwrite, naming the supplement, renewal-claim and both documentation schedules. Sibling overwrites of the same clause would each have to exclude the others (D.16); one scoped overwrite keeps a single merged reading.
- O10 (answered). The BadgerCare tier takes off only the designated account's coverage-terminated liabilities. The rule says so ("Coverage-terminated liabilities on any other account stand as posted"). The DSL cannot iterate per account, and the merged semantics are unique.
- O11: not issued in revision_3.
- Exhaustive seeded-row pass (both worlds, every cross-category row, each owning charter as of its posting date). Payer figures are claim-charter parameters: expected allowed % of charges, 30 clean-claim days, 60 appeal-decision days, timely filing 180/120.

| world | row(s) | owning-charter check | result |
|---|---|---|---|
| T0 | Anthem PPO 61b88df9 (2024 knee surgery) | billed +5d ≤180; paid +23 ≤30; allowed 5639.40 = 58.5% exp; ded 2000 + 20% coins 727.88 | fixed: underpayment appeal + 0.00 remit removed (no shortfall), closed 2024-10-15, appeal_level 0 |
| T0 | Anthem PPO 6e2673cb (Jan inpatient) | +10 / +27; allowed 37586.25 = exp; ded 3000 + coins capped at OOP 8000 | OK |
| T0 | Anthem PPO b08fc67e (Mar clinic) | PR-27 +19 ≤30; class SELF_PAY at correction; no uninsured discount (not self-pay at final bill) | OK |
| T0 | Marketplace d9335c73 (Jul obs stay) | +24; allowed 4674.00 = 47.5% exp; ded 3000 + 40% facility coins 669.60; AOR signed 08-21 before member appeal 08-21 | fixed: denial_date cleared (never denied, carc NONE); appeal pending day 61 of 60 (O8) |
| T0 | Marketplace a9b7b552 (Aug imaging) | +25; allowed 1643.50 = exp; ded 1500 (4500 met) + 20% imaging coins 28.70 | OK |
| T0 | Marketplace 5a3da2c7 (Sep clinic) | +12; allowed 135.38 = exp; copay 40.00 = POS payment; account closed at 0 | OK |
| T0 | Marketplace 41bfae54 (Sep echo) | accepted, pending day 17 ≤30 | OK |
| T0 | encounter accounts (14) | bill-hold days per type (3/4/5) all exact; charges = gross; balances = liabilities − adjustments − payments; uninsured discount 50/45/50% std on self-pay; statements every 30 d while patient_due and not on plan or hold (2024 surgery 3 summaries + final notice) | OK |
| T0 | Aug imaging b9497b5b hold/inquiry/lines | ITEMIZATION_REVIEW 10-06 (30 d), itemized statement 10-09 (≤5 bd), no duplicate line | fixed (S3-1) |
| T0 | catheterization fa2bc102 | GFE_DISPUTE_PENDING 10-14, estimate in_dispute (day 104 ≤120, excess 500 ≥400) | OK |
| T0 | Hardship plan 3d0a5ecb | installments 180.80/180.80/196.73/501.11/501.11 (balance over remaining term); paused 09-15/10-15 (FAP pending ≤90 d); 4 add-ons in 12 months (cap 4) | fixed: BALANCE_WITHDRAWN_FOR_DISPUTE 13400.00 on 10-14 (plan charter), balance 27561.33 → 14161.33, installment unchanged |
| T0 | estimates (7) | GFE issue timing (3 bd for ≥10 bd scheduling, 1 bd for 3–9); totals = lines; self-pay lines = gross less type discount; package 72148 = 895 at 100% deposit; course closed 120 d after initial bill | OK |
| T0 | insured estimate bf4424a0 (echo) | contracted rate on remaining benefits: 47.5% × 2180 = 1035.50, deductible met → 20% = 207.10 | fixed: 412.50 → 207.10 (total and line) |
| T1 | NH HMO 5cb3978f (Jan ED) | +4 / +23; allowed 3062 ≥ exp 2537.60; ded 2000 + 20% 212.40 | OK |
| T1 | NH HMO 61b6437f (May 14 clinic, elective) | PR-27 was +34 > 30 | fixed: 06-13 (+27); liability 06-13, first statement 06-17 |
| T1 | Quartz 518e636d (Jun surgery) | +23; allowed 6182.50 vs exp 7727.20 (−20%) → underpayment route | fixed: appeal type UNDERPAYMENT_APPEAL, filed 09-24 (≤90 d), pending day 55 of 60 |
| T1 | Quartz 54a95a9f (Oct CT) | allowed 1148.00 was −25% short with no appeal and the claim closed | fixed: allowed = exp 1539.20; copay 75 + 20% × 1464.20 = 292.84; paid 1171.36, contractual 1420.80; account balance 367.84 |
| T1 | Quartz e0fdbe47 (Oct 28 clinic, E8) | PR-27 +17 ≤30 | fixed (S3-2) |
| T1 | Quartz a5665ddb (Nov ED) | accepted, pending day 5 | OK |
| T1 | encounter accounts (7) | bill-hold days exact; elective MRI discount 25%; holds GFE 09-29 (estimate in_dispute) and itemization 11-13 (request RECEIVED, turnaround to 11-20) | OK |
| T1 | Assistance-Linked plan 7496ef5b | 2212.40/48 = 46.09; add-ons 3254.13/45 = 72.31, 6418.32/44 = 145.87; 11-15 paused (renewal submitted) | OK |
| T1 | award applications (assist) | amounts 0 within cap: 2212.40 + 3236.50 + 367.84 = 5816.74 ≤ 9960 | text updated |
| T1 | estimate 6e5edc50 | issued 09-04 (≤3 bd); line 1800 = total; dispute day 3, excess 540 | OK |

- Method factors: no method-factor definition changed. hold_holdout (supplement) now takes T2 on task 0; its all-pairs table is in the task-0 rationale (T1 240.00 on the open-dispute probe vs T2 28.70 vs T3 0). Changed parameter tiers (insured_pending T2, hold_restore T2) are probed in the rationale tables.
- Probes on touched reads are in both rationales:
  * held account itemization vs open dispute, itemized statement absent, decoys;
  * F7 none and POS tiers, F8 insured and self-pay disputes;
  * C17 picks (completed after closed, second tied insured estimate, completed co-provider after disputed);
  * task 1 coverage-gap with no October liability, ties, decoys.
- Mechanical checks: A1 walk 0 violations in all six policies; every compute_basis, baseline sentence and policy_source is in its rule; no factor id is inside a tool name; identifier band 44 kept (QZ44H2510313, EFT44Q1117512, EFT44N0613308).
- Stale-text sweep: no "resolved with no change", duplicate contrast, provider reconsideration, May 2 visit or old figures remain outside the deliberate gold-move notes and probe rows.
- Gold moves:
  * T0: supplement 14348.02 → 14559.32 (hold take-off 240.00 → 28.70); own-charge documentation 23627.80 → 23839.10; completed documentation 29828.98 → 29623.58 (echo estimate 412.50 → 207.10, hold add-back 240.00 → 28.70); cap 8514.60 unchanged (burden 26.26%, same 0.85 tier). Skips 9279.78 / 20343.80 / 9276.00.
  * T1: renewal claim 6254.58 and response days 155 unchanged (standard figure 10088.50 → 10166.74 and hold take-off 214.60 → 292.84 cancel); skip 161.
- Gates (replay with --check; db_closure refreshed through a scratch copy): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: C16, C17, F7, F8, S3-1, S3-2, O12, O13, O14.
REWORK round 4: gates 7/7 green

## Rework round 5 — response to revision_4 (S4-1, S4-2, O8, O15); seed-only
assist.extended.yaml and task_tools.py are byte-identical to round 4 (sha256 96e77a673343…, 912186a017e8…). No seed fix forced a rule change.
- S4-1 (task 0: claim d9335c73 appealed with no denial and no underpayment) → CLOSED with a real, charter-producible path.
  * The Marketplace remit of 2025-08-20 now allowed 4424.00, which is 250.00 (5.3%) below the expected 47.5% × 9840.00 = 4674.00. Both underpayment thresholds are met (25.00 and 2%), so the claim charter routes it to an UNDERPAYMENT_APPEAL.
  * Remit lines: paid 854.40, CO-45 5416.00, PR-1 3000.00, PR-2 569.60 (40% facility coinsurance on allowed 4424.00 less deductible 3000.00).
  * Riverbend filed the underpayment appeal (level 1) on 2025-08-28, inside the 180-day provider window. The claim moved adjudicated → appealed, and denial_date stays empty because the claim was never denied.
  * The observation account's coinsurance liability and balance are re-posted to 569.60 and 3569.60.
  * The authorized-representative form 21362e79 is removed: no member-level appeal exists. Gold read step 9 now records that no form is on file.
- O8 → SETTLED with the same fix. No appeal in either world is past the payer's decision time:
  * Task 0: the underpayment appeal is pending 54 of 60 days. appeal_overdue now takes its tier 2 (an appeal of another type pending more than Riverbend's own other_appeal_review_days 45), so it bears weight without a payer-late date.
  * Task 1: the underpayment appeal is pending 55 of 60 days.
  * Probes: day 45 adds nothing, day 46 adds the coinsurance, and a member appeal on day 54 adds nothing.
- S4-2 (task 1: award application row e7b0d5bd) → CLOSED.
  * charge_basis_usd and fap_liability_usd changed 289.60 → 367.84, equal to the CT's posted responsibility (copay 75.00 + coinsurance 292.84) under the insured charge basis.
  * Derived figures: the award's cap use is now 5816.74 of 9960.00 in the rows and in the text; obligation ≤ liability, so the application amount stays 0.00; charity_applied_total stays 0.00.
- O15 (Quartz termination unexplained) → CLOSED in the records.
  * The household's employer group plan ran with Quartz in coverage months from the 26th (group effective 2025-05-26). The employer ended that contract after the 2025-09-26..10-25 month and moved the group to Security Health Plan of Wisconsin, whose groups start on the 1st (2025-11-01).
  * The November 9 ED claim a5665ddb is now billed to Security Health Plan (member SH44620934, group SHG44113058, claim SH44E2511137) and is still accepted, so the pending-claim days are unchanged.
  * No coverage was active on 2025-10-28, so the coverage-update rebill cannot apply to the October 28 visit. The PR-27 is a real gap, and the persona's "same jobs" stays true.
- Seed table updates (other round-4 rows unchanged):

| world | row(s) | owning-charter check | result |
|---|---|---|---|
| T0 | Marketplace d9335c73 (Jul obs stay) | +24 ≤30; allowed 4424.00 vs expected 4674.00 (−250.00, −5.3%) → underpayment route; appeal filed 08-28 (≤180), pending 54 ≤60; deductible 3000 + 40% × 1424 = 569.60 | fixed (S4-1, O8) |
| T0 | encounter acf05bc0 | coinsurance 569.60, balance 3569.60; statements 08-24 and 09-23 (cycle 3 due 10-23) | fixed |
| T0 | claim_appeal_authorizations | no member appeal, so no AOR | removed 21362e79 |
| T0 | Marketplace deductible chain | 3000 (obs, 08-20) + 1500 (imaging, 09-10) = 4500 met; echo estimate 207.10 unchanged | OK |
| T1 | award application e7b0d5bd (CT) | insured charge basis = posted 367.84; cap use 5816.74 ≤ 9960; amount 0.00 | fixed (S4-2) |
| T1 | ED claim a5665ddb | billed to the new carrier 11-13, accepted, pending day 5 ≤30 | fixed (O15) |
| T1 | Quartz e0fdbe47 (Oct 28) | PR-27 +17 ≤30; no coverage active on the date of service, so no rebill | OK (O15 explained) |

- Probes on touched reads are in the task-0 rationale: appeal decided, member-appeal variant, 45/46-day edges, decoy appeal, plus the round-4 probes re-run on the new world.
- Stale-text sweep: no member-appeal, AOR, day-61, 3669.60 or old gold figures remain in either task outside the probe rows that test those variants.
- Gold moves:
  * T0: supplement 14559.32 → 17559.32 (standard 31932.30 → 31832.30; appeal take-off 3669.60 → 569.60); own-charge documentation 23839.10 → 26839.10; completed documentation 29623.58 → 29523.58 (overdue-appeal add 3669.60 → 569.60); cap 8514.60 unchanged (burden 26.17%, with own charges only 23.79%). Skips 9279.78 / 20243.80 / 9276.00.
  * T1: renewal claim 6254.58 and response days 155 unchanged; skip 161.
- Gates (replay with --check; db_closure refreshed through a scratch copy): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: S4-1, S4-2, O8, O15.
REWORK round 5: gates 7/7 green

## Rework round 6 — response to revision_5 (F9, O17)
- F9 (the other-costs appeal factor called a non-member appeal "overdue" after Riverbend's own 45 days, inside the payer's 60) → CLOSED by re-cutting the factor in assist_ext_other_costs_debt. This is the only charter change; task_tools.py is untouched and task 1 is byte-identical.
  * Rename: factor appeal_overdue → appeal_held_share; binding overdue_add → appeal_add. No factor id is inside a tool name.
  * Params: member_appeal_decision_days and other_appeal_review_days are removed. The member tier now reads the payer's own decision time, CPARAM('claim','payer_appeal_decision_days', claim_id=appeal_claim): 60 for commercial and Marketplace, 30 for BadgerCare Plus.
  * T1: a member appeal under the patient's authorization, claim still appealed, with more days than its payer's post-service decision time passed (the payer let its time run out) → deductible, coinsurance and copay of the appeal window.
  * T2: an underpayment appeal or a recoupment dispute, claim still appealed → the appeal window's coinsurance. These appeals contest only the payer's payment, so the patient's posted share stands whatever the payer decides (an underpayment win can only raise the allowed amount). The tier reads no date, so no tier calls an appeal overdue inside the payer's time.
  * T3 / fall-through: everything else adds nothing and the held cost sharing stays out. This covers a member appeal still within its payer's time, any other appeal type, a decided appeal and no appeal.
  * Rule and compute agree, and every compute_basis quote is re-swept (0 misses).
  * XF re-applied to the touched policy: A1 walk clean; baseline sentence and policy_source are in the rule; B.6 edges hold (no appeal → appeal_due not read); B.7 tie rule unchanged (XLATEST, first listed); B.12 every read field exists (claim variant_name added to the reads list).
  * Task 0 honestly reaches T2. Riverbend's underpayment appeal of 2025-08-28 is on day 54 of 60, and the factor bears weight: baseline 28953.98 against gold 29523.58.
- O17 (authorization read decides nothing) → CLOSED by dropping find_claim_appeal_authorizations from task-0 gold.
  * The closure gate allows it: replay reports 21 actions, closure 173 = initial 173.
  * Later steps are renumbered: computation and solvability steps 15/17/19/21 → 14/16/18/20, and the prior_step references with them.
- Probes (task-0 rationale) on the other-costs appeal tiers:
  * member appeal on day 59 and on day 60 add nothing; day 61 adds 3000.00 + 569.60;
  * a BadgerCare Plus member appeal on day 36 (payer time 30) adds;
  * a recoupment dispute adds the coinsurance; a provider reconsideration adds nothing;
  * a decided appeal and no appeal add nothing; a decoy appeal leaves the figure unchanged.
- Method factors: none changed (appeal_held_share is a parameter factor), so no pairwise table is needed.
- Seed table: no seeded row changed this round.
- Gold moves: none. T0 stays 17559.32 / 26839.10 / 29523.58 / 8514.60 (skips 9279.78 / 20243.80 / 9276.00); T1 stays 6254.58 / 155.
- Gates (replay with --check; task-0 db_closure refreshed through a scratch copy): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: F9, O17.
REWORK round 6: gates 7/7 green

## Rework round 7 — response to revision_6 (O18 plus a framing sweep; text only)
Only rule text and the compute_basis quotes of those sentences changed in assist.extended.yaml. Every compute, factor, ladder, param, prerequisite and base key is unchanged (checked by a parsed dict compare against the round-6 file). task_tools.py, tasks/0.json and tasks/1.json are byte-identical (912186a017e8, a3facb85d52b, 90acac465eb2). No task file quotes a changed clause.
- O18 → CLOSED (assist_ext_other_costs_debt, appeal_held_share tier 2).
  * Old: "the patient's share standing as posted whatever the payer decides".
  * New: "the posted coinsurance being the least the patient owes in any outcome, since an underpayment appeal can only raise the allowed amount the coinsurance is a share of and a recoupment dispute concerns only the payer's takeback".
- Framing sweep: every reason or participle clause in all six rules was checked. Three more overstated what the records or real rules support and were trimmed; none changes a figure.
  * other_costs lead: "added back where the appeal can no longer keep it from the patient" → "added back as follows". A member appeal past its payer's decision time can still be decided for the patient, so the old lead overstated tier 1.
  * supplement and renewal, BadgerCare tier: ", those dates being billed to BadgerCare Plus" removed. Holding a BadgerCare Plus claim does not show that the coverage-gap account's dates are billed to it.
  * qualifying debt, awaiting self-pay account: ", that care being documented under its estimate" removed. An awaiting account with an issued, not completed, single-service estimate is documented under no schedule.
  * The clauses kept were checked as true: PR-27 meaning; "never at amounts the payer is expected to pay"; "the payer having let that time run out"; "contests only the payer's payment"; the charge-correction discount (encounter charter); the response-window reason clauses.
- Every compute_basis quote is re-swept as a substring of its rule (0 misses); baseline sentences and policy_source are present. Gold moves: none.
- Gates (replay with --check): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: O18.
REWORK round 7: gates 7/7 green

## Rework round 8 — response to audits/render_source/financial_assistance_screening/render_r1.md (renderer scan-first STOP)
- (1) Held-account selection used by only one factor → CLOSED in all three policies.
  * dispute_acct, review_acct and held_acct are now bindings of the factor that uses them: hold_holdout (supplement), renewal_hold_holdout (renewal) and hold_restore (other costs).
  * The defining sentence "The held account is …" now sits directly before that factor's hold sentence.
- (2) Hardship cap order and rounding → CLOSED. The generic order sentence now places every adjustment kind and the rounding exactly as compute does, RND(MX(0, RND(income × cap_pct/100 × debt_keep, 2) + asset_raise − std_cap), 2):
  * "every reduction of the cap percent applies first (the cap percent never going below zero); the annual household income is then scaled at the resulting percent and every kept share is applied to that scaled figure, the product being rounded half-up to the cent; every addition applies last, and the cap is rounded half-up to the cent and is never below zero."
  * The kept-share tiers now say "… of the scaled figure is kept" and "the whole scaled figure is kept".
  * Compute is unchanged.
- (3) Factors pointing at other factors, and framing without a record test → CLOSED.
  * QD selfpay_basis now states its own record test: "When a self-pay good faith estimate (single scheduled service, procedure with co-providers or recurring course of care) whose service has been completed, which is closed or which is in dispute is linked to the self-pay account, its bill stands as posted under this adjustment".
    - New binding sp_gfe (9 exact CFIELD tests) replaces "sp_acct == ga_acct or sp_acct == gu_acct".
    - The tier-3 ladder text includes the linked case.
    - ga_id/ga_acct and gu_id/gu_acct were then used by one factor each, so they moved into gfe_account_basis and gfe_undisputed, with each definition placed before its factor's sentence.
    - "is added back" → "is added" for the undisputed part.
  * Other costs, framing:
    - The opening now reads "adding medical costs that Riverbend's records show: care given whose bill or payer decision is still pending, co-providers' charges for procedures performed at Riverbend, cost sharing posted from a claim under appeal, and cost sharing posted on an account on a billing hold".
    - The appeal sentence now reads "Cost sharing posted from the claim under appeal is added as follows …"; the clause "any cost sharing the claim held out stays out" is gone.
    - The hold sentence now reads "Cost sharing posted on the held account is added as follows …", and "added back" became "added" throughout.
    - No sentence refers to another policy's claim.
- (4) The notice tool could not list MEDICAID_DETERMINATION_NOTICE → CLOSED by extending the tool contract.
  * send_missing_information_notice_7f5665e5 gains one enumerated arg, medicaid_notice_request (REQUESTED / NOT_REQUESTED). REQUESTED applies when the tier requires a Medicaid determination notice and none has been accepted on the case.
  * The docstring has no examples and no ordering words; the body logs the REQUESTED row like the other four document types; the tool name and uuid8 are unchanged.
  * The percent-pointed tiers' required documents are now all requestable: INCOME_PROOF, PROOF_OF_RESIDENCY, MEDICAID_DETERMINATION_NOTICE, OUTSIDE_MEDICAL_BILLS, BANK_STATEMENT. The presumptive tier is never pointed to by a percent.
  * Task 1 gold call gains medicaid_notice_request = NOT_REQUESTED (Medical Hardship does not require it, and it is already accepted), with a tracing entry. Response days stay 155.
- Sweeps, once per class over all six policies:
  * Plain bindings or defining sentences used by one factor: mechanical walk. The only remaining one is response_window base_days, which is the standard figure itself (baseline sentence "The standard response days are missing_information_response_days calendar days"), not a factor quantity.
  * Factor sentences referencing other factors: none left ("described above" gone). The shared "claim under appeal" selection stays a plain binding read by two factors (A.2).
  * Framing without record support: other_costs and QD reworded as above; the round-7 sweep stands for the rest.
  * Rule vs tool capability: every write the rules require is expressible. Supplement, own charges, other costs and renewal claim write qualifying debt; approve writes cap, dates and letter language; the notice now covers every percent-tier document.
  * Order and rounding sentences vs compute: supplement, renewal (RND(MX(0,…))), QD (RND(MX(0,…)) or the claimed figure), other costs (RND of the sum), window (whole days) and cap (fixed above) all match.
  * A1 walk: 0 violations. compute_basis quotes, baseline sentences and policy_source are all present.
- Probes on the touched read (QD sp_gfe, task 0 handling world, gold 26839.10):

| probe | result |
|---|---|
| self-pay account linked to an issued single-service estimate (not excluded) | 26839.10 |
| linked to a completed single-service estimate (excluded, as posted) | 28055.70 |
| linked to a closed recurring-course estimate (excluded) | 28055.70 |
| linked to an insured estimate (not a self-pay GFE) | 26839.10 |

  The held-account, cap and other-costs edits change no compute value; every gold, all-baseline and per-factor figure re-evaluated is identical.
- Stale-text sweep: "added back", "held out" and "set aside" are reworded in tasks/0.json where they described the other-costs additions; the notice objective and rationale in tasks/1.json now name the fifth document flag.
- Gold moves: none (T0 17559.32 / 26839.10 / 29523.58 / 8514.60; T1 6254.58 / 155). The T1 notice call adds one argument, NOT_REQUESTED.
- check_traceability (outside the gate block) still reports the six discoverable tool names as having no published source. They are published by the KB at render time; this is expected before rendering.
- Gates (replay with --check; db_closure re-derived via a scratch copy, unchanged): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: render_r1 items 1, 2, 3, 4.
REWORK round 8: gates 7/7 green

## Rework round 9 — response to audits/policy_kb/financial_assistance_screening (_difficulty.md revision_2, src-1)
- src-1 (the "package price" was computed as the estimate total, which counted an Outpatient Surgery package's co-provider lines twice) → CLOSED in assist_ext_qualifying_debt, factor package_rendered.
  * Rule: the rendered-package sentence now defines the term as the estimate product's published docs do (surgery and maternity balance and late-move docs): "its package price is the sum of the Riverbend facility line and the Riverbend professional line that carry the principal service code on its current version, co-provider lines not being part of it".
  * Compute: new factor binding pk_price sums the estimate lines with roles CONVENING_FACILITY and CONVENING_PROFESSIONAL, service_code = the estimate's primary_service_code, current version. pk_add reads pk_price instead of estimate_total_usd, and the reads list now has primary_service_code and estimate_transactions.service_code in place of estimate_total_usd.
  * Co-provider lines are now counted only by the other-costs co-provider addition; the own-charges documentation never adds them.
  * Probes on the touched read (task 0 handling world):
    - a completed Outpatient Surgery package (29881, facility 5875.00) with an anesthesia line 980.00: own charges add 5875.00 only (26839.10 → 31819.10);
    - in that world with the co-provider GFE closed: other costs add the package's anesthesia line once (1540.00 → 980.00, 28963.58);
    - a Riverbend professional line on the principal code is added (+150.00);
    - a Riverbend professional line on another code is not added.
  * Gold: unchanged. Task 0's rendered package is the Imaging & Diagnostics package, one facility line 895.00 on 72148, equal to its total.
- Same-class sweep: every read of another product's figures in all six policies, checked against docs/estimate, docs/encounter and docs/plan; the claim docs are unpublished, so the claim charter was used.
  * GFE expected charges and "Riverbend lines" (convening facility + convening professional lines of the current version) match the estimate docs' "sum of the Riverbend facility and Riverbend professional lines of that version". Used in the supplement and renewal estimate factors, QD gfe_account_basis and gfe_undisputed, and other-costs rendered_care.
  * GFE billed charges (self-pay final bill less uninsured discount) match the docs' "self-pay final bill less the uninsured discount".
  * Insured estimate "total" (other-costs insured_pending) is the estimate total the docs compare actual liability with: the patient's expected share.
  * Co-provider lines (other-costs coprovider_rendered: anesthesia, pathology, radiology roles of the current version) match the docs' co-provider roles.
  * Package upgrade differential: CPARAM package_upgrade_differential_usd of its tier, the published figure.
  * Encounter terms match: uninsured / elective discount percent of the account type, PACKAGE_PRICE_ADJUSTMENT, self-pay final bill, point-of-service payment.
  * Plan: the cap's "installment … on the patient's active Riverbend payment plan" reads monthly_payment_usd, the plan's installment.
  * Claim: payer_appeal_decision_days and appeal types follow the claim charter.
  * No other term differs in meaning from what compute reads.
- KB note: the rendered assist doc rendered_package_price_estimates ("The package price is the estimate's total") now trails the source and needs a re-render of that doc.
- assist.extended.yaml is the only file changed. task_tools.py and tasks/0.json and 1.json are byte-identical, and replay --check passes with the existing db_closure. Gold moves: none.
- Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: src-1.
REWORK round 9: gates 7/7 green

## Rework round 10 — response to audits/policy_kb/financial_assistance_screening revision_3 (src-2..src-5); seed-only
assist.extended.yaml and task_tools.py are byte-identical (b0470d6bbda6 / fe7e3790cf06).
- src-5 (task 0: estimate 03633924 issued past its 1-business-day deadline) → CLOSED.
  * The course was scheduled Wed 2025-04-09 for 2025-04-21 (8 business days ahead, so furnishing is due 1 business day after scheduling).
  * issued_date and its line 05b3f0db are re-dated 2025-04-14 → 2025-04-10.
  * No assist read uses the issue date; gold unchanged.
- src-4 (task 1: estimate 6e5edc50 typed as a single-service GFE for 72148, which is on the imaging package schedule) → CLOSED.
  * The September elective MRI is re-coded to 72141 (MRI cervical spine without contrast, cdm 6100141). 72141 is not on the Imaging & Diagnostics package schedule (70553, 72148, 74177, 77067, 93306), so the published types table makes a self-pay-elected single scheduled service furnished by Riverbend alone a "Self-Pay Good Faith Estimate - Single Scheduled Service".
  * Re-coded rows: estimate primary_service_code, line 481ab021 service_code, and charge 25ea6449 (CPT and cdm).
  * All figures stand: GFE 1800.00, billed 3120.00 less the 25% elective imaging discount = 2340.00, excess 540.00 ≥ 400, dispute day 3, GFE_DISPUTE_PENDING hold.
  * Gold unchanged (renewal claim 6254.58, notice 155). Rationale, objective and trace text updated ("cervical-spine MRI").
- src-2 (task 0) / src-3 (task 1), owed encounter writes → NOT closed. STOPPED: honest seeding needs a rule change. Analysis below for the coordinator.
  * Honest history, each write posted on its own date with the published encounter rules:
    - T0 E2 8bdb031d coverage-terminated discount on 2025-03-27 (before the 04-01 statement, so no courtesy is owed): clinic 40% + 0 points (size < 2500, no 0450 line, no hardship denial, no other PR-27) = 168.00.
    - T0 E3 c88c4cb6 observation-rate discount on 2025-07-01 (with the final bill, before the 07-04 statement): 0762 charges 4840.00; 1 day; day rate 1250 + 250 (Appleton, 0450 line) = 1500; (4840 − 1500) × 0.5 = 1670.00 (floor 242.00; no 0350/0480 carve-out).
    - T1 E2 15c52208 coverage-terminated discount on 2025-06-13 (before the 06-17 statement): elective 20% + 0 = 236.00.
    - T1 E6 bd2c77fb coverage-terminated discount on 2025-11-17: 40% + 2.5 (one other PR-27 release, on 61b6437f) = 42.5% × 830.00 = 352.75.
    - Derived rows that would move: T0 plan enrollments 04-10 (252.00) and 07-08 (2280.00), the plan installments and payments, and the E0 balance; T1 plan enrollment 07-01 (944.00), installments 67.07 / 140.63, the E0 balance and the plan balance.
  * Why the frozen rules cannot absorb that history honestly:
    1. Coverage-gap take-off. Supplement coverage_gap and renewal renewal_coverage_gap take off "the part of [the coverage-terminated liabilities] above their amounts-generally-billed share" (ct_liab − AGB(ct_liab)), measured on the posted liabilities. Once the published uninsured discount stands against the same postings, the standard figure already nets it, so the account is reduced twice.
       - T0 E2: 168.00 + 274.68 = 442.68 off a 420.00 debt.
       - T1 E6: 352.75 + 542.82 = 895.57 off 830.00.
       - Fixing this changes compute: the take-off would have to be measured on the coverage-terminated liabilities net of their uninsured discount (MX(0, ct_liab − ct_disc − AGB(ct_liab))) — a rule change.
    2. Own-charges self-pay revaluation. QD selfpay_basis tier 2 replaces the self-pay bill by its AGB share. With the observation-rate discount posted, E3's bill becomes 7900 − 3950 − 1670 = 2280.00, below its AGB share 2733.40. The tier would then raise documented debt above what is posted (QD 26839.10 → about 28509.10 on a scratch re-run), which no 501(r) schedule does.
       - Fixing this needs "the smaller of the bill and its AGB share" on tier 2, but tier 1 already has that shape, so the method ladder would have to be re-cut — a rule change.
  * Scratch re-run of the honest history, frozen rules, for illustration: supplement 17559.32 → 15721.32; QD 26839.10 → 28509.10; renewal claim 6254.58 → 5665.83. Not written to any task.
  * Proposed route, for decision:
    - (a) supplement and renewal coverage-gap tier 2: take off MX(0, CT liabilities − their posted uninsured discount − AGB share of the CT liabilities). Tier wording "the part of the coverage-terminated balance net of its uninsured discount that is above its amounts-generally-billed share".
    - (b) QD selfpay_basis re-cut so no tier raises a bill:
      - T1: package-priced, MN(bill, AGB);
      - T2: emergency or medically necessary with no package, MN(bill, AGB) on the bill net of every uninsured discount, with an added input the observation-rate discount already granted;
      - or replace the tier with another real method.
    - (c) then seed the four writes on their own dates as above, re-price the derived plan rows, and recompute both tasks.
    - Alternatively the coordinator may rule that writes another product calls owed but not yet posted at the frozen time are acceptable seed state. The encounter docs fix no posting deadline, and the xcheck table did not count them as misses.
- Bounded pass over every row touched this round:
  * 03633924: issue 1 business day after scheduling ✓; line date = issue ✓; closed 120 days after the 05-08 initial bill unchanged ✓.
  * 6e5edc50 / 481ab021 / 25ea6449: type matches scope and code ✓; line = gross 2400 × 0.75 (elective imaging 25%) basis unchanged ✓; account discount 25% ✓; dispute figures ✓; claim activity unaffected (self-pay account) ✓.
  * No other row derives from them.
- Gates (replay with --check; db_closure re-derived through a scratch copy): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Round-10 status: src-4 and src-5 closed; src-2 and src-3 open pending a coordinator decision on a rule change. The round-10 sentinel is withheld.

## Rework round 10 (continued) — coordinator ruling: route (a) for src-2 / src-3
- Rule change (the freeze lifted for exactly this), assist.extended.yaml only. task_tools.py is byte-identical (fe7e3790cf06).
  * Coverage gap (supplement coverage_gap, renewal renewal_coverage_gap):
    - The take-off is measured on the coverage-terminated balance, which is the CT liabilities of the window less every uninsured discount of the window posted on the coverage-gap account (new factor binding ct_disc).
    - BadgerCare tier: the whole balance comes off.
    - Notice + emergency/MN tier: MX(0, balance − AGB share of the CT liabilities). Nothing comes off a balance already at or below that share.
    - Elective / otherwise: nothing.
  * QD selfpay_basis:
    - The bill is net of every uninsured discount (the observation-rate discount included).
    - No tier raises a bill: emergency/MN with the bill above its AGB share → reduced to that share; emergency/MN at or below → stands; otherwise → stands.
    - The package split is gone (sp_pkg removed), because the bill already nets the package price adjustment.
    - The factor is now effect=parameter: the honest AGB cap has one shape, so it cannot be a method factor.
  * QD gfe_account_basis:
    - Emergency/MN tier is now the smallest of the bill, the Riverbend lines and the AGB share (it could raise a bill before).
    - It is now QD's method factor. T1 MN(bill, lines, AGB) | T2 MN(bill, lines) | T3 nothing. Pairs: T1 vs T2 differ by the added AGB input (this world 581.28 vs 924.00); T1/T2 vs T3 differ for any completed or closed estimate whose lines are below the bill.
  * Other costs, hold_restore tier 2 (discount-measure sweep): the uninsured discount rate is now the discount posted on the account's most recent self-pay final-bill liability divided by that liability (bindings dispute_fb, dispute_bill, dispute_disc), so an observation-rate discount on another line is not counted.
  * QD framing: "amounts generally billed for emergency and medically necessary care, never above the bill as posted".
  * Every combination sentence keeps its order. All compute_basis quotes are in their rules; A1 walk 0 violations; each computation keeps one method factor (QD: gfe_account_basis).
- Seeded encounter writes, each posted on its own date per docs/encounter (calculation sheets and allowance docs re-checked):
  * T0 March clinic (8bdb031d): coverage-terminated discount 168.00 on 2025-03-27. Clinic uninsured 40%; size < 2500, no 0450 line, no hardship denial, no other PR-27 → +0 points. Posted before the 04-01 statement, so no courtesy is owed. Balance 252.00; plan enrollment 04-10 at 252.00.
  * T0 June observation stay (c88c4cb6) re-dated to a 2-day stay 06-26 → 06-28, 22 observation hours (so selfpay_basis keeps bearing weight). Final bill 07-02 (bill-hold 4); uninsured discount 3950.00 and observation-rate discount 920.00 on 07-02, sourced to the 0762 line. The 920.00 is 2 days, day rate 1250 + 250 Appleton campus (0450 line), length-of-stay 0 (22 h), no 0350/0480 carve-out: (4840 − 3000) × 0.5 = 920.00, floor 242.00. First statement 07-05; balance 3030.00; plan enrollment 07-08 at 3030.00.
  * T0 plan re-priced: 178.00, 178.00, 193.93, 482.17, 482.17; balance 26519.61 → 13119.61 after the 13400.00 dispute withdrawal; E0 (2024 surgery) balance 913.61. Plan-burden points stay 2.0 (482.17 = 5.13% of monthly income > 5).
  * T1 May 14 clinic (15c52208): coverage-terminated discount 236.00 on 2025-06-13 (elective 20%, +0). Posted before the 06-17 statement, so no courtesy. Balance 944.00; plan enrollment 07-01 at 944.00.
  * T1 October 28 clinic (bd2c77fb): coverage-terminated discount 352.75 on 2025-11-17. Clinic 40% + 2.5 points for one other PR-27 release (61b6437f) = 42.5%. No statement yet, so no courtesy. Balance 477.25.
  * T1 plan re-priced: 46.09 × 3, 67.07, 140.63 × 3; balance 5765.67; E0 (ED) balance 1585.17. Award application rows are unchanged (E2 elective-excluded; E6 not yet applied).
  * No encounter write is owed at the opening of either world:
    - every coverage-terminated account carries its discount, posted before its first statement;
    - the observation stay carries its observation-rate discount;
    - no non-covered liability, prompt-pay payoff or small balance is due.
- Bounded pass over touched and derived rows:
  * Each account's balance equals its liabilities less adjustments and payments.
  * Final-bill dates equal service end plus the bill-hold days.
  * First statements come after the discounts.
  * Plan balance equals enrolled less installments less withdrawal (both worlds).
  * Plan payments equal the encounter payments (same references).
  * Completeness (cap overwrite): 12-month patient responsibility net of adjustments 32003.48 > 22560.00.
- Factor weight (T1 test: baseline alone; T2 test: producible world):
  * coverage_gap 16639.32 vs 16746.00; renewal_coverage_gap 6018.58 vs 6208.65.
  * selfpay_basis 26839.10 vs 27135.70; gfe_account_basis vs 27181.82.
  * Every other factor still bears weight (computations.factor_sensitivity).
- Probes: the task-0 table was fully re-run on the new world, including:
  * discount absent (same claim: no double count);
  * a further discount below the AGB share (nothing more comes off);
  * the observation-rate discount absent;
  * a self-pay bill below its AGB share (never raised);
  * the three-way minimum picking lines or keeping the bill.
  The task-1 table was re-run likewise.
- Gold moves:
  * T0: supplement 17559.32 → 16639.32 (standard 31832.30 → 30744.30; coverage-gap take-off 274.68 → 106.68); own charges 26839.10 unchanged (self-pay reduction −1216.60 → −296.60 offsets); other costs 29523.58 unchanged; cap 8514.60 unchanged. Skips 9279.78 → 10199.78, 20243.80 → 19323.80, 9276.00.
  * T1: renewal claim 6254.58 → 6018.58 (standard 10166.74 → 9577.99; coverage-gap take-off 542.82 → 190.07); response days 155 unchanged (6018.58 is still between 4980.00 and 19920.00); skip 161.
- src-4 and src-5 fixes are kept (72141 single-service GFE; 03633924 issued 2025-04-10).
- Stale-text sweep: rationale, traces, objectives, solvability and closure text updated in both tasks; persona untouched (no affected figure).
- Gates (replay with --check; db_closure re-derived through a scratch copy, 175 / 107 rows): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: src-2, src-3, src-4, src-5.
REWORK round 10: gates 7/7 green

## Rework round 11 — response to revision_10 (F11, C18)
- F11 (selfpay_basis tiers 2 and 3 both "the bill as posted") → CLOSED. The ladder is re-cut to three distinct, real outcomes, none raising a bill or a share (501(r)(5): a patient eligible for financial assistance is charged no more than AGB for emergency or medically necessary care, the amount charged being what the patient is personally responsible for):
  * T1: the self-pay account is coded emergency or medically necessary and no completed, closed or disputed self-pay GFE is linked → MN(bill, AGB share of its self-pay final-bill liabilities) − bill. Task 0 takes it: 3030.00 → 2733.40, −296.60.
  * T2: no such self-pay account, and an insured account exists → MN(patient share, AGB share of gross charges) − patient share.
    - The insured account is the account of the claim carrying the patient's most recent payer payment (tie: listed first), with the claim not appealed, the account not on a billing hold, coded emergency or medically necessary.
    - Its patient share is the liabilities of the window posted from that claim.
    - Holds and appeals are excluded so this never overlaps the supplement's take-offs.
    - New bindings ins_claim, ins_acct, ins_ok, ins_share, ins_agb; QD cross_category gains claim, and encounter reads gain gross_charges_total, billing_hold_reason and claim_id.
  * T3: otherwise → nothing revalued.
  * Rule sentence: "One account is revalued in one of three ways, none ever raising a bill or a share above what is posted …".
  * T1 test (task 0): baseline alone 27135.70 ≠ 26839.10.
  * T2 test (producible world: E3 coded elective, the most recent paid clinic account's share 200.00 above its AGB share 98.61): 27135.70 → 27034.31. The same world with that account held gives 27135.70.
  * Counts: QD 6 factors, 5 parameter + 1 method (gfe_account_basis).
- C18 (coverage-gap ladder text described the gross liabilities) → CLOSED. Supplement coverage_gap and renewal renewal_coverage_gap tiers now read:
  * T1: "the coverage-gap account's coverage-terminated balance (its coverage-terminated liabilities of the twelve months less every uninsured discount of the twelve months posted on that account), taken off".
  * T2: "the part of that balance above the amounts-generally-billed share (agb_pct percent) of those liabilities, taken off, nothing when the balance is at or below that share".
  * These match ct_off = (ct_liab − ct_disc) | MX(0, ct_liab − ct_disc − AGB(ct_liab)) | 0.
- Ladder sweep: every tier of the 31 factors in all six policies was read against its decides binding.
  * Fixed besides C18: other_costs hold_restore T2 now says "times the uninsured discount rate of the account's most recent self-pay final bill" (compute dispute_fb since round 10).
  * Checked equal, no change:
    - supplement and renewal: appeal_holdout, hold_holdout, gfe_dispute;
    - QD: gfe_account_basis (MN of three / two / nothing), gfe_undisputed (MN(expected, AGB) / expected / 0), unbilled_selfpay, package_rendered (package price = facility + professional lines on the principal code; + upgrade differential), course_in_progress;
    - other_costs: rendered_care, insured_pending, coprovider_rendered, appeal_held_share, hold_restore T1;
    - cap: all six;
    - response window: all six.
- A1 walk: 0 violations; every compute_basis quote is in its rule; each computation keeps exactly one method factor.
- Gold moves: none (T0 16639.32 / 26839.10 / 29523.58 / 8514.60; T1 6018.58 / 155). tasks/1.json is unchanged. tasks/0.json changed in text only: the selfpay tier label and trace, rationale probe rows for T2, and the rationale note.
- Gates (replay with --check): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Closed this round: F11, C18.
REWORK round 11: gates 7/7 green
