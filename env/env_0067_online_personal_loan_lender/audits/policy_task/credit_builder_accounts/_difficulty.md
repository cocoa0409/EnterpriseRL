# Policy-task audit — credit_builder_accounts / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-16, auditor = independent erl-task-policy-audit agent (not the instantiator). Written before any task GT was revealed; nothing below is derived from `evaluation_criteria`, `computations` or any other masked field.
- Inputs and hashes: `tasks/credit_builder_accounts/builder.extended.yaml` sha256=088bb0f3a620946f4d1f9fdfad04d3c7b84273a54bce6d69f3c22d230bf8c936; `tasks/credit_builder_accounts/task_tools.py` sha256=b6a7ac630d06b0e1f3fbced056f85247a916b12be1f0bccfa0708e50aa97b0e8 (both match the coordinator's gate snapshot). Also read: `blueprint/products/builder.yaml` (and hardship/line/loan charters for cross-category states), `blueprint/blueprint.yaml` difficulty entry, `blueprint/share_tools.py`, `audits/render_source/XF_recipe.md`, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py`.
- Masked / unread at freeze: `tasks/credit_builder_accounts/tasks/*.json`, `worklog.md`, `plan.md`, every masked key of the views (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`).
- Entry conditions (Step 0): gate snapshot supplied (`.audit_views/policy/credit_builder_accounts/r1/gate_snapshot.txt`): EXTENDED / TASK TOOL CONTRACT / REPLAY(--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK pre-publication with only `unlock_*_discoverable_tool:tool_name` misses (KB not rendered) — accepted as the documented pre-publication state. Masked views supplied with matching hashes. Entry conditions met.
- Base copy: lines 1–1112 of the extended file are byte-identical to `blueprint/products/builder.yaml` (diff empty).

### policy_conflict_scan
Eight extended policies; subject claims are pairwise disjoint except `builder_fee_waived`, shared by `builder_ext_returned_fee_relief` (returned-payment fees, automatic once made good) and `builder_ext_goodwill_late_fee_credit` (late fees, on request); each overwrite names the other by kind, so the object decides the policy. Both draw on one resource, the plan's courtesy waivers per 12 months; the order relief → goodwill is fixed by the goodwill rule's own prerequisite sentence, so no parallel-edge ambiguity. Other overlaps:
- Early closure vs closing-month dividend: the closure is gated on the dividend while the dividend policy can credit nothing — see finding CG-2.
- AutoPay: base `builder_evt_payments` "AutoPay is available with no rate discount" vs AutoPay-driven interest reductions in two extended policies — see CG-1.
- Cross-category reads: hardship (status, variant_name, plan_interest_rate), loan (status, autopay_enrolled, payment_due_day, loan_transactions late fees), line (status, payment_due_day, amount_past_due, line_transactions payments/returns) — all declared in `cross_category`; read-only; no extended policy writes another category.
- Scopes: task 0 = {early_closure_settlement (root), late_fee_charge, returned_payment_fee_charge, closing_month_dividend}; task 1 = {goodwill_late_fee_credit (root), payment_interest_split, returned_fee_relief, autopay_reenrollment} (derived from the prerequisite graph; the masked `charter_scope` is not read). Pairwise disjoint, jointly complete over the 8 extended policies.

### rule_compute_equivalence
Scratch sweep (`/tmp/audit_credit_builder_accounts_0067/mech.py`, deleted at close): every `compute_basis` quotation of every policy is verbatim in its own `rule` (sentence-wise; `ad_ap_returns` quotes two non-adjacent rule sentences, each verbatim); every `baseline.rule` sentence is in the rule; every `prerequisite.policy_source` and every `overwrite.replaced_by` is verbatim in the rule. Every factor ladder tier is a rule sentence and a branch of its `decides` binding, and vice versa. Rounding (XF 6): every rule's rounding sentence matches its RND/MN placement (late fee: round then cap; returned fee, dividend, relief: round once at end; closing interest rounded once, then total rounded and capped at savings; payment interest round once; goodwill round then cap at the late fee; due day integer, clamped 1–28).
Divergences found (all charter-wide; see CG-7):
- `builder_ext_returned_fee_relief`: the rule ties the timing and reason tiers to "the returned payment" of "the account's most recent returned-payment fee"; `rr_ret_amount`, `rr_ret_date`, `rr_code` read `LATEST(builder_payment_returned)` independently of the fee's `related_txn_id`. No same-day tie rule is stated for returned payments (only for fees).
- `builder_ext_autopay_reenrollment`: `ad_code` = "the most recent return code" with no same-day tie rule; `ad_line_past_due` = `CFIELD('line','amount_past_due')` with no status filter, while the rule's anchor sentence restricts "the FlexLine" to active or frozen status.
- `builder_ext_late_fee_charge.lf_dc_credit` and `builder_ext_early_closure_settlement.cc_dc_count`: the rule counts debit card payments "credited toward" the due date; compute sums/counts every posted debit card row with no exclusion of a returned one (base: "A returned payment is reversed in full and its installment is unpaid again").
Sweep back: no compute binding lacks a rule sentence; no rule sentence makes an empty promise except the release-timing sentence of the early-closure rule ("released on a business day after the closing date, never on the closing date itself"), which governs a base event with no task tool (observation O-3).

### action_binding_and_uuids
`(target_tool, computes)` pairs: assess_late_fee_fbf509e1/late_fee_amount, assess_returned_payment_fee_1f748b6c/returned_payment_fee_amount, credit_closing_dividend_02dff71e/dividend_amount, confirm_early_closure_8372931d/savings_applied_amount, apply_payment_interest_8aeaa3c8/interest_portion, relieve_returned_payment_fee_d8e21ef6/relief_amount, credit_goodwill_late_fee_43fbbd15/credit_amount, reenroll_autopay_5af065e7/payment_due_day — each claimed once. uuid8s fbf509e1, 1f748b6c, 02dff71e, 8372931d, 8aeaa3c8, d8e21ef6, 43fbbd15, 5af065e7: no shared prefix/suffix, no sequence, no reuse. Owners: confirm_early_closure and reenroll_autopay are `owner="user"`, the rest `agent`. Docstrings: no other tool named, no ordering word used as sequence ("after the split", "next due date", "first due date on the new day" are field/effect descriptions), no example values (XF 7). Bodies (XF 13): no imports beyond erlbench, each write calls ctx.create/update in its own body, no tool refuses, validates or hints on any prerequisite; effects match docstrings (confirm_early_closure books only the savings-applied line and the status change — consistent with its docstring).

### prerequisite_graph
Every policy fills `prerequisite` (six `[]`, two non-empty). Edges: early_closure_settlement → {late_fee_charge (value_input, cc_fees), returned_payment_fee_charge (value_input, cc_fees), closing_month_dividend (state_gate)}; goodwill_late_fee_credit → {payment_interest_split (state_gate), returned_fee_relief (value_input, gw_base), autopay_reenrollment (value_input, gw_autopay)}. All `problem`s are extended ids in this file, none self, none base; graph acyclic (two depth-1 stars). All `form: state`, no `fallback_reason` (correct). Every `policy_source` verbatim in the blocked rule. `resolved_by` = the depended-on policy's `target_tool` in all six. `kind`/`gate` bindings exist (`cc_fees`, `gw_base`, `gw_autopay`). Conditions match the sentences' strength. No authoring-viewpoint phrasing. The value_input claim of goodwill → autopay_reenrollment rests on a tier the goodwill gate makes unreachable — see CG-3 (consequence in task_1.md).

### prerequisite_sentences
| edge | sentence (blocked rule) | connective | waited-on state | single resolving write |
| --- | --- | --- | --- | --- |
| closure ← late fee | "The savings applied at an early closing are fixed only after the account carries a late fee for every due date whose grace period has ended with the installment still unpaid." | only after | late-fee line per lapsed unpaid due date | assess_late_fee (only tool booking `builder_late_fee_assessed`); the late-fee rule "A late fee is owed for a due date once its grace period has ended with the installment still unpaid." matches |
| closure ← returned fee | "The early-closure settlement is not figured until every returned payment whose return code carries a fee shows its returned-payment fee on the account." | not … until | returned-fee line per fee-bearing return | assess_returned_payment_fee |
| closure ← dividend | "An early closure is booked only once the savings certificate shows its dividend for the closing month." | only once | dividend line for the closing month | credit_closing_dividend |
| goodwill ← split | "A goodwill credit is granted only after every payment posted to the account shows its interest and principal split." | only after | split on every posted payment | apply_payment_interest |
| goodwill ← relief | "The goodwill credit is figured only after every returned payment that a later payment has made good carries its returned-payment fee relief." | only after | courtesy waiver on the made-good return's fee | relieve_returned_payment_fee (the goodwill tool's object is a late fee) |
| goodwill ← AutoPay | "A goodwill credit is not granted until the account is enrolled in AutoPay." | not … until | `autopay_enrolled` true | reenroll_autopay (only write setting it) |
All six pass the four-point test (connective, record-visible state in table/finder words, no tool/policy id/snake_case/row id, strength = condition). No rule restates another problem's sentence; depended-on rules do not restate them. Derivation for each: sentence → records show the state false → the one rule whose own text produces that state → its tool; single reading each. Undeclared cross-problem order sweep: none grounds a missing edge; two sentences noted as observations (O-3 release timing; O-4 "made good … credited").

### override_declarations
Sentence-by-sentence over each `base_policy_refs`:
- late_fee_charge ← builder_evt_late_and_returned_fees: S1 grace (followed), S2 counting (inherited), S3 amount/cap/once/active (declared overwrite), S4 returned fee (sibling's overwrite), S5 bureau reporting (n/a).
- returned_payment_fee_charge ← same: S4 declared; others n/a/inherited.
- closing_month_dividend ← builder_evt_savings: S1 monthly dividend (declared, self-scoped to the closing month), S2 "Dividends are credited only while the account is active." (inherited), S3–S4 withdrawal (n/a).
- early_closure_settlement ← builder_evt_closing_and_release: S1 maturity (n/a); S2 "A borrower may close early at any time: …" (NOT overwritten — conflicts with the dividend gate in one reachable case, CG-2); S3–S4 delinquency (n/a); S5 savings order (declared, self-scoped); S6 "Savings leave the certificate only once …" (inherited); S7 release (inherited, narrowed compatibly); ← builder_evt_early_closure_request: S1–S5 inherited; S6 "closing interest is counted through that date" (declared).
- payment_interest_split ← builder_evt_payments: S1 active (inherited); S2 allocation/interest (declared, self-scoped); S3 reversal (inherited); S4 limits (inherited); S5 "AutoPay is available with no rate discount; …" (NOT overwritten — departs, CG-1); S6 maturity (n/a).
- returned_fee_relief, goodwill_late_fee_credit ← builder_evt_fee_waiver: S1 once (inherited); S2 courtesy count (retired by both, each naming the sibling); S3 request window "A courtesy waiver must be requested no later than the fee waiver request window after the fee's assessment date." (inherited; unclear for a relief granted "without a request", O-2); S4 counting (inherited); S5 error bases (inherited); S6 admin fee (inherited).
- autopay_reenrollment ← builder_evt_payments (`overwrite: []`): S5 due-day change restated faithfully; no AutoPay discount taken. Pass.
Undeclared departures: CG-1 (AutoPay discount), CG-2 (close early at any time vs dividend gate). Variant parameter texts that restate retired methods (`closing_interest_method`, `interest_method`, `savings_dividend_method`) remain in force as plan terms — observation O-1.

### factor_ladders
Counts as declared (P = parameter, M = method, X = cross_difficulty, MS = multi-source):
| policy | factors | P/M | X | MS |
| --- | --- | --- | --- | --- |
| late_fee_charge | lf_base(M), lf_pct, lf_hardship(X hardship), lf_return_share | 3/1 | 1 | lf_pct (late-fee rows ∧ open_date) |
| returned_payment_fee_charge | rf_base(M), rf_history, rf_other_line(X line), rf_reason, rf_seasoning | 4/1 | 1 | rf_seasoning (open_date ∧ posted−returned) |
| closing_month_dividend | dv_rate(X loan), dv_autopay, dv_tenure, dv_fraction(M) | 3/1 | 1 | dv_rate (loan holding ∧ loan ledger) |
| early_closure_settlement | cc_lead(M), cc_tail(M), cc_rate, cc_hardship(X hardship), cc_autopay, cc_tenure | 4/2 | 1 | cc_rate, cc_autopay (enrolled ∧ returns) |
| payment_interest_split | al_days(M), al_rate(X hardship), al_free, al_loan(X loan), al_ap_hist | 4/1 | 2 | al_free (open_date ∧ late fees) |
| returned_fee_relief | rr_timing(M), rr_first, rr_season, rr_line(X line), rr_reason, rr_age | 5/1 | 1 | rr_season |
| goodwill_late_fee_credit | gw_base(M), gw_tenure, gw_loan(X loan), gw_history, gw_autopay, gw_speed | 5/1 | 1 | gw_loan, gw_base |
| autopay_reenrollment | ad_anchor(M, X line), ad_return_buf, ad_reason_buf, ad_history, ad_line_buf(X line) | 4/1 | 2 | none (task 1 has others) |
Structure checks: every factor's bindings disjoint; `decides` is an input, never `result`; every ladder has three pairwise-disjoint tiers stated in full in the rule and implemented in compute; every fall-through equals the factor's `baseline`, which equals what `baseline.rule` states; no factor binding reads another factor's binding (only `gw_base` reads the plain shared selection `gw_fee`) — XF 1 passes; assembly sentences are generic with the order fixed (XF 2 passes); no factor id is a substring of a tool name (XF 10); no cross-record date pairing outside the DSL (XF 11).
Failures: CG-3 (fall-through unreachable within the policy's own scope), CG-4 and CG-8 (realism), CG-5 (mislabelled method / coinciding tiers), CG-6 (XF 3). Counts that survive the strikes are given per finding below; whether each surviving factor bears weight is in the task files.

### findings
**CG-1 — SOURCE-POLICY RED (undeclared override; XF 4).**
Symptom: two extended policies cut Credit Builder interest for AutoPay. Base `builder_evt_payments` (in force, cited by `payment_interest_split.base_policy_refs`, not named by any overwrite): "AutoPay is available with no rate discount" (plan parameter `autopay_rate_discount_percent: 0.0`, "APR reduction for AutoPay"). Members of the class:
- `builder_ext_early_closure_settlement.cc_autopay`: "When the account is enrolled in AutoPay and no payment on it was returned in the 3 whole months before today, the closing interest is multiplied by the clean AutoPay share." (0.85; 0.95 with returns).
- `builder_ext_payment_interest_split.al_ap_hist`: "When 12 or more AutoPay debits were posted to the account in the 12 months before today, the interest is multiplied by the long AutoPay share; when 6 to 11 were, by the mid AutoPay share" (0.97/0.99).
- `builder_ext_payment_interest_split.al_loan` tier 1 vs tier 2: the only difference is the personal loan's AutoPay enrollment (0.95 vs 0.98) — an AutoPay-linked cut to Credit Builder interest.
Consequence: an agent following the base sentence computes those multipliers at 1.00 (and 0.98) and gets a second defensible scored value. Demonstrated in task_0.md (closure) and task_1.md (payment interest). Artifact: both policies' `rule`/`compute`/`overwrite`.

**CG-2 — SOURCE-POLICY RED (contradiction; the depended-on state can't be produced).**
Passage A (closure rule, prerequisite sentence): "An early closure is booked only once the savings certificate shows its dividend for the closing month." Passage B (dividend rule): "a month closed before its last day counts as no fraction of a month, so no closing-month dividend is credited" and "When it has had fewer than 3 monthly dividends credited, the closing month counts as no fraction of a month." Passage C (base, not overwritten): "A borrower may close early at any time". Situation: an active account with 0–2 dividends credited whose borrower confirms a pending request mid-month. B says no dividend is credited (and the dividend tool takes "a positive amount"), so A can never be met and the account can never close early; C says it closes on confirmation. Same situation, two conclusions. The same holds on any world for a reader of the dividend computation document alone (baseline gives 0.00). Bears on task 0 (its baseline demonstration). Artifact: closure `rule`/`prerequisite[2]`, dividend `rule` fall-through tier and `baseline.rule`.

**CG-3 — SOURCE-FACTOR RED (unreal ladder: the fall-through is unreachable inside the policy's own scope; the remaining tiers' shared condition restates the scope).**
- `cc_tail` fall-through "When there is no pending early-closure request on the account, the interest days end on the closing date." — base inherited: "The account closes early only when the borrower confirms a pending early-closure request". Every customer reaching `confirm_early_closure` has a pending request.
- `al_days` fall-through "Any other such payment pays interest for one twelfth of 365 days." — scope: "For a one-time payment of at least the monthly payment posted after the grace period of the due date it is credited toward, and only for such a payment" (grace = 15 days), so every in-scope payment is ≥16 days late and falls in tier 1 or 2.
- `gw_autopay` fall-through "when it is not enrolled, nothing is added for AutoPay" — the rule's own gate "A goodwill credit is not granted until the account is enrolled in AutoPay." makes "enrolled" true for every customer at the goodwill write.
Consequence: each ladder has two reachable tiers (< 3); the factor's baseline describes a case no customer at that write can be in. Struck from the counts. Demonstrations in task_0.md (cc_tail) and task_1.md (al_days, gw_autopay; and the effect on the goodwill → AutoPay value_input edge).

**CG-4 — SOURCE-FACTOR RED (realism, XF 12: leaving the schedule is priced better than keeping it).** Tier values no US credit-builder (savings-secured installment) lender would publish:
- Closing-month dividend: `dv_rate` tiers 1–2 (1.00 % / 0.50 % APY), `dv_autopay` tiers 1–2 (+0.25 / +0.10), `dv_tenure` tiers 1–2 (+0.10 / +0.05), `dv_fraction` tier 1 (a whole month, 1/12 year, for a part month). By the overwrite, every other month, maturity included, still earns the plan's 0.10 % APY: the certificate pays up to 13.5× its rate, for days it no longer holds the money, only to a borrower who breaks it early. Certificate issuers forfeit or penalise on early termination; none pays a bonus rate for it.
- Early-closure closing interest: `cc_rate` tiers 1–2 (APR − 4 / − 2 points), `cc_tenure` tiers 1–2 (× 0.8 / × 0.9), `cc_autopay` tiers 1–2 (× 0.85 / × 0.95): interest owed at payoff is charged at a lower effective rate than every on-schedule payment, which pays the full APR (base `interest_method`).
- Late payment interest: `al_days` tier 2 ("A payment posted 16 to 30 days after that due date pays interest for exactly 30 days", fewer than the 365/12 = 30.42 days an on-time payment pays) and `al_free` tiers 1–2 (10 / 5 interest-free days, granted only to payments in this policy's scope, i.e. late ones). On task 1's balance at the APR: on time 24.72; the same seasoned borrower paying 18 days late 16.26.
Struck: dividend 0 of 4 factors survive; early closure keeps cc_lead and cc_hardship (cc_tail struck by CG-3); payment split keeps al_rate, al_loan, al_ap_hist (0 method). Count failures follow (< 4 factors; < 1 method in the dividend and the payment split).

**CG-5 — SOURCE-FACTOR RED (mislabelled method / coinciding tiers; XF 9).**
- `cc_tail` (method): the three tiers only substitute an end date (request date / request date + 3 / closing date) into one day count DAYS(oldest unpaid due date, end) — a window length.
- `ad_anchor` (method): the three tiers only substitute a day number (FlexLine due day / loan due day / own due day) into one formula, anchor + buffers.
- `cc_lead`: tier 2 ("30 days for each whole monthly payment past due") gives the fall-through's 30 days whenever amount past due is between one and two monthly payments — two tiers coincide on a reachable domain.
Consequence: reenrollment has 0 honest method factors; early closure keeps cc_lead as its one method (coincidence noted). Bears on task 0 (cc_tail, cc_lead) and task 1 (ad_anchor).

**CG-6 — SOURCE-POLICY RED (XF 3: factor-only quantity defined outside that factor's own sentence, in a sentence mixing other factors' conventions).** Members:
- late_fee_charge: "The 12-month and 3-month windows run back from the assessment date by whole calendar months: …" (12-month only lf_pct, 3-month only lf_return_share).
- returned_payment_fee_charge: "Payments credited are the payments posted to the account less the payments returned, and the windows run back from today …" (payments credited only rf_seasoning).
- early_closure_settlement: "Payments credited are … and the 3-month window runs back from today …" (payments credited only cc_rate; 3-month window only cc_autopay).
- returned_fee_relief: "Payments credited are … and the month windows run back …" (payments credited only rr_season).
- goodwill_late_fee_credit: "The 12-month, 3-month and one-month windows run back from today …" (3-month only gw_autopay; one-month only gw_base).
- autopay_reenrollment: "An AutoPay debit returned is a returned payment whose amount equals the monthly payment, and the 12-month windows …" (definition only ad_return_buf).
Non-members: closing_month_dividend and payment_interest_split (their window sentences serve two factors each and define nothing factor-only).
Consequence: the KB has no lossless place for these sentences. In the computation document they describe a factor quantity. In one factor document they carry another factor's convention. Without them each factor document leaves its tier term undefined. No scored value moves on either task world (the posted vs credited counts land in the same tiers), so the cost is the render's one-way correspondence. Recorded as RED per the coordinator's XF rule.

**CG-7 — SOURCE-POLICY RED (rule ≠ compute on decoy rows; XF 8).** Members:
- relief `rr_ret_amount`/`rr_ret_date`/`rr_code` read the latest return, not the fee's own return. On task 1's world with an added later one-time 50.00 payment returned R10 (no fee), the rule gives 4.00 × 0.80 × 0.75 = 2.40 (the fee's AutoPay R01 return), compute gives 1.50 (halved, no reason add). No same-day tie rule for returns.
- reenrollment `ad_code`: no same-day tie rule for "the most recent return code".
- reenrollment `ad_line_past_due`: no status filter (a closed or charged-off FlexLine's past-due amount is read).
- `lf_dc_credit` and `cc_dc_count`: a returned debit card payment is still counted as "credited".
Neither task world contains such a decoy, so no scored value moves on task 0 or task 1. Charter-wide.

**CG-8 — SOURCE-FACTOR RED (realism: conditions no lender weighs for the due day).** `ad_history` (12+ / 6–11 AutoPay debits move the reset due day 2 / 1 days earlier; AutoPay history says nothing about when the borrower's funds arrive) and `ad_reason_buf` tier 2 (R08 stop payment, R16 account frozen, R20 non-transaction account add a 1-day buffer; a one-day shift does nothing for any of these). Funds-timing tiers (R01/R09, returned-AutoPay count, FlexLine returns/past due) are kept. With CG-5: reenrollment keeps ad_return_buf and ad_line_buf (2 factors, 0 method). Bears on task 1.

Observations (not grounds for rework):
- O-1: plan parameters `closing_interest_method`, `interest_method`, `savings_dividend_method` still state the retired base methods as plan terms. The overwrites retire the policy sentences, not these texts.
- O-2: relief is "granted without a request", but the inherited 60-day request window reads "must be requested no later than …"; it's unclear whether a relief made good after day 60 is barred. Not reached on task 1 (fee 15 days old).
- O-3: early-closure rule "The remaining savings are released on a business day after the closing date, never on the closing date itself." states an order against a base event with no task tool. It grounds no edge and steers no write.
- O-4: relief "made good once a later payment has been credited toward the due date" could be read as waiting on the payment's split. Nothing in the charter ties "credited" to the split, and the posted row already carries `installment_due_date`.
- O-5: "AutoPay debits posted" (al_ap_hist, ad_history) counts a later-returned debit. The charter's own "A posted payment is returned unpaid and reversed" and the dividend rule's explicit "less the payments returned" settle the gross reading. The task 1 world sits on that boundary (12 gross, 11 net).

## closing_checklist
Written after both reveals (everything above this heading was written before either reveal and is unchanged). **The difficulty is not closed: neither task has all four relationships at PASS.**
- Audit files: `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; each has a frozen derivation, a comparison and findings; revision_1 is the first revision.
- Coverage and scope: the 8 extended policies are covered. GT `charter_scope` (task 0: late fee, returned fee, dividend, closure; task 1: split, relief, AutoPay, goodwill) equals the partition derived pre-reveal: disjoint and complete. The task tools are each claimed once, with independent uuid8s.
- Trees: task 0 has 3 prerequisite problems, 2 value_input edges, a user-owned root, acyclic: PASS. Task 1 has 3 prerequisite problems, 1 genuine value_input edge (goodwill ← AutoPay is a gate in substance), a user-owned leaf: SOURCE-CHAIN RED (1.md finding 1). The union graph is acyclic.
- Factors: every scored value equals the auditor's blind figure, and every factor_sensitivity / baseline_result figure matches the auditor's recomputation figure for figure. But after the charter-wide strikes (CG-3, CG-4, CG-5, CG-8) these computations fall below the bounds: dividend 0/4, closure 2/6, payment split 3/5 (0 method), due day 3/5 (0 method). Late fee, returned fee, relief and goodwill keep their counts.
- Proof text (XF 14), per-task members (full list in the task files): task 0 has one stale scope sentence (design_rationale [0]). Task 1 has (a) "never mentions … AutoPay" against the persona's "you turned the automatic payments off", (b) skipped-effect 1.02 the gate forbids, (c) the wrong intermediate 4.8327 (correct 4.8261), (d) "no late fee" on a loan ledger that has one (2025-07-06), and (e) the seeded TRR plan payment 206.68 against the charter's 206.60.
- Gate re-run on the final form: not applicable. There is no final form until the REDs are reworked; the auditor runs no gates (Step 0).
- Open charter-wide REDs: CG-1, CG-2, CG-3, CG-4, CG-5, CG-6, CG-7, CG-8.

VERDICT revision_1: task0=RED SOURCE-POLICY+SOURCE-FACTOR task1=RED SOURCE-CHAIN+SOURCE-POLICY+SOURCE-FACTOR+SOURCE-TASK charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-16 (after 14:51 snapshot) before any revision-2 GT was revealed; same independent auditor. Nothing below is derived from any masked field of the reworked tasks.
- Gate entry: last line of `tasks/credit_builder_accounts/worklog.md` is exactly `REWORK round 2: gates 7/7 green` (only that line read). Gate snapshot = output of `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 2` (2026-10-16T14:51:28): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; TRACEABILITY NOT OK. The snapshot printed only `[FAIL]` for traceability, not the miss categories. Round 1's "unlock tool names only" line is absent, so the pre-publication explanation is taken on the coordinator's word and not verified (observation O-6). No other gate is red.
- Hashes (snapshot = sha256sum here): `builder.extended.yaml` 24610681f5643fedea54b6c23bd19f827b980066152e87f021450448a7ff9c94; `task_tools.py` 1ba148f6ab1d3aecd33a341ddbb19fa0312948e356655ec606341ad9dc98cc50; views r2/task_0.json d65215dfff1882c89373d1f0b67a41a174ca98dc691d82dfcfc1fe42ad9cfe85, r2/task_1.json fcfcb3c614bad12b1b3f2067a2a5bae37092d0641d09a7d2a7a7d997e0ecf5e9. Both source hashes changed, so every charter-global section is re-derived in full below (nothing is carried forward by reference).
- Rework claims read by item id only (`rework_r2_claims.md`). Masked and unread: tasks/*.json, plan.md, the worklog body.
- Base copy: lines 1–1112 still byte-identical to `blueprint/products/builder.yaml`.

### policy_conflict_scan (r2)
Eight extended policies. Removed: closing_month_dividend, payment_interest_split. New: closing_late_fee_relief (`relieve_late_fee_at_closing_c21c573e`) and closing_returned_fee_relief (`relieve_returned_fee_at_closing_90cd40e1`). Reworked: settlement, goodwill, autopay_reenrollment. Edits: late_fee_charge (chargeback netting, windows), returned_payment_fee_charge and returned_fee_relief (window sentences, tie rules, guards).
Inferred scopes: task 0 = {settlement (root), late_fee_charge, closing_late_fee_relief, closing_returned_fee_relief}; task 1 = {goodwill (root), returned_payment_fee_charge, returned_fee_relief, autopay_reenrollment}. Disjoint as claims, complete.
`builder_fee_waived` is now claimed by **four** policies, which all retire the same base courtesy-count clause and each name the others by kind. Their triggers overlap on one fee, and base "A fee may be waived once." admits only one of them — finding R2-2. Courtesy count is a shared resource of all four (R2-1). Cross-category reads: hardship (status, variant_name, plan_interest_rate), loan (status, amount_past_due, ledger), line (status, amount_past_due, ledger), pos (ledger) — declared, read-only.

### rule_compute_equivalence (r2)
Scratch sweep `mech.py` (re-created; deleted at close): every compute_basis quote is verbatim in its rule (two multi-sentence quotes, `cc_addback` and `cc_interest`, have every sentence present). Every baseline sentence, every prerequisite `policy_source` and every `replaced_by` is in its rule. Every ladder tier is a rule sentence and a compute branch. Rounding (XF 6): settlement total `MN(savings, RND(interest + balance + addback + fees))` matches "an amount added back below joins the total before it is rounded … not more than the savings balance"; closing late-fee relief `MN(fee, RND(…))` matches "rounded … once, at the end and never more than the fee"; closing returned-fee relief, relief, goodwill and late fee also match. No rule anywhere fixes a half-cent convention ("rounded to the cent"); see the task 1 demonstration. Divergences: R2-4.

### action_binding_and_uuids (r2)
Pairs claimed once each: assess_late_fee/late_fee_amount, confirm_early_closure/savings_applied_amount, relieve_late_fee_at_closing_c21c573e/relief_amount, relieve_returned_fee_at_closing_90cd40e1/relief_amount, assess_returned_payment_fee/returned_payment_fee_amount, relieve_returned_payment_fee/relief_amount, credit_goodwill_late_fee/credit_amount, reenroll_autopay/payment_due_day. New uuid8s c21c573e and 90cd40e1 are independent of the six kept ones. Docstrings: no ordering words, other tool names or example values. Bodies validate nothing; imports are erlbench only. Four tools (`relieve_late_fee_at_closing`, `relieve_returned_fee_at_closing`, `relieve_returned_payment_fee`, `credit_goodwill_late_fee`) write the **identical** row shape: `builder_fee_waived`, `waiver_reason="courtesy"`, `related_txn_id` = the fee. The only difference is the make_id prefix (bcl_/bcr_/brl_/bgw_), which is not a business field — finding R2-3.

### prerequisite_graph (r2)
Edges:
- settlement → late_fee_charge (value_input cc_fees), closing_late_fee_relief (value_input cc_fees), closing_returned_fee_relief (value_input cc_fees);
- closing_late_fee_relief → late_fee_charge (value_input hl_fee);
- returned_fee_relief → returned_payment_fee_charge (value_input rr_fee);
- goodwill → returned_payment_fee_charge (value_input gw_base), returned_fee_relief (value_input gw_base), autopay_reenrollment (state_gate `builder_accounts.autopay_enrolled`).
All problems are extended ids; acyclic (two DAGs of depth 2); all form state, no fallback; every policy_source is verbatim; resolved_by = the depended-on target_tool; gate bindings exist. The goodwill → AutoPay edge is now honestly a state_gate (r1 SOURCE-CHAIN cause removed).

### prerequisite_sentences (r2)
- Settlement ← late fee: "…fixed only after the account carries a late fee for every due date whose grace period has ended with the installment still unpaid." Passes.
- Settlement ← closing late-fee relief: "The early-closure settlement is not figured until the most recent late fee shows its early-closure relief." Settlement ← closing returned-fee relief: "…fixed only once the most recent returned-payment fee shows its early-closure relief." **Both fail point 2:** "its early-closure relief" is not a record-visible state. The record shows a courtesy fee waiver against the fee, a row two (late fee) or two (returned fee) tools produce identically (R2-3). Their strength also over-reaches the depended-on rules: neither relief is always owed (R2-1).
- Closing late-fee relief ← late fee: "The early-closure late-fee relief is not figured until every lapsed unpaid due date carries its late fee on the account." Passes.
- Relief ← returned fee: "The made-good relief is not figured until every returned payment whose return code carries a fee shows that fee on the account." Passes.
- Goodwill ← returned fee: "The goodwill credit is figured only once every returned payment whose return code carries a fee shows its returned-payment fee on the account." Passes.
- Goodwill ← relief: "…figured only after every returned payment that a later payment has made good carries its returned-payment fee relief." **Fails point 2** for the same reason: the made-good relief and the closing returned-fee relief leave the same row (R2-3).
- Goodwill ← AutoPay: "A goodwill credit for a borrower whose AutoPay debit was returned in the 3 whole calendar months before today is not granted until the account is enrolled in AutoPay." Passes; the scope is now in the sentence.
No undeclared cross-problem order found. The release-timing sentence is still observation O-3.

### override_declarations (r2)
- late_fee_charge, returned_payment_fee_charge: as r1 (declared).
- settlement ← closing_and_release: S5 declared and self-scoped. "A borrower may close early at any time" is NOT overwritten, and it conflicts with the relief gates in reachable cases (R2-1). ← early_closure_request: no overwrite now; the rule restates "closing interest is counted through that date" faithfully.
- Four fee-waiver policies ← builder_evt_fee_waiver: S2 is retired by all four, each naming the others (XF 4 sibling form passes). S1 "A fee may be waived once." is inherited, and the four now collide on it (R2-2). S3 request window is inherited, and is ambiguous for the three request-less reliefs (O-2 widened; it also feeds R2-1).
- autopay_reenrollment (`overwrite: []`): restates the due-day change; no AutoPay discount.
- CG-1 check: no extended policy now ties an interest reduction to AutoPay. Closed.

### factor_ladders (r2)
| policy | factors (M = method, X = cross) | P/M | X | MS |
| --- | --- | --- | --- | --- |
| late_fee_charge | lf_base M, lf_pct, lf_hardship X, lf_return_share | 3/1 | 1 | lf_pct |
| settlement | cc_lead M, cc_rate X hardship, cc_hardship X hardship, cc_hold | 3/1 | 2 | cc_rate (SCRA/TRR rows) |
| closing_late_fee_relief | hl_paid M, hl_program X, hl_first, hl_season, hl_loan X loan, hl_age | 5/1 | 2 | hl_season, hl_paid |
| closing_returned_fee_relief | hr_timing M, hr_reason, hr_line X line, hr_request, hr_first | 4/1 | 1 | hr_request (return ∧ request) |
| returned_payment_fee_charge | unchanged structure | 4/1 | 1 | rf_seasoning |
| returned_fee_relief | unchanged structure | 5/1 | 1 | rr_season |
| goodwill | gw_base M, gw_tenure, gw_loan X, gw_history, gw_autopay, gw_speed | 5/1 | 1 | gw_loan |
| autopay_reenrollment | ad_return_buf M (2n / flat 3 / none), ad_reason_buf, ad_line_buf X, ad_loan_buf X, ad_pos_buf X | 4/1 | 3 | ad_line_buf tier 2 |
Every ladder has three disjoint tiers stated in the rule. The fall-through equals the factor baseline, which equals `baseline.rule`. Fall-throughs are reachable inside each policy's scope (CG-3 class re-checked over all 41 factors; none found). Method tiers change shape: cc_lead tier 2 now needs ≥2 whole payments (≥60 days ≠ 30); ad_return_buf 2n (n≥2) ≠ 3 ≠ 0; hl_paid scaled/half/full; hr_timing decay/half/full. No factor id is in a tool name. Realism: CG-4/CG-8 members are gone. The closing reliefs mirror the in-life reliefs (goodwill, made-good relief), so early closers get no relief that continuing borrowers lack. New realism member: R2-6. XF 1 re-checked: R2-5.

### findings (r2)
Round-1 REDs:
- **CG-1 closed.**
- **CG-2: dividend gate removed, but the class recurs** (closure gated on a state the depended-on policy may not produce) — R2-1.
- **CG-3 closed.**
- **CG-4 closed.**
- **CG-5 closed.**
- **CG-6 closed** (each factor-only window, credited-payment and AutoPay-return convention now sits in its factor's sentence).
- **CG-7 closed for its listed members**; new edge members in R2-4.
- **CG-8 closed.**

**R2-1 — SOURCE-POLICY RED (closure deadlock class).**
Passage A: "The early-closure settlement is not figured until the most recent late fee shows its early-closure relief." / "…fixed only once the most recent returned-payment fee shows its early-closure relief." Passage B (in force): "A borrower may close early at any time". Passage C: the relief rules grant only when owed and while the courtesy count allows. Members, each a reachable situation in which no write can bring A about, so B and A disagree:
- (a) Credit Builder 600/1000/1200/1800 plans allow 1 courtesy waiver per 12 months. A borrower owing a late fee and a returned-payment fee gets one relief; the other is "granted only while fewer than that number have been granted". The same happens on any plan whose waivers were already used (e.g. a goodwill credit and a made-good relief earlier in the year).
- (b) The most recent late fee was already paid: the relief is granted only when the borrower "still owes the account's most recent late fee".
- (c) The most recent late or returned fee was already waived once (goodwill credit or made-good relief): "A fee may be waived once."
- (d) The most recent returned payment carries no fee (R07/R10/R29/CB) while an older returned-payment fee exists: the relief "is owed only when the account's most recent returned payment carries a returned-payment fee", yet A waits on "the most recent returned-payment fee".
- (e) An account with no late fee or no returned fee ever: A names a fee that does not exist (vacuous or unsatisfiable; the text does not say which).
- (f) A late or returned fee assessed more than 60 days before the request, if the inherited window "must be requested no later than the fee waiver request window" applies to request-less reliefs.
Bears on task 0 only as the class's consequence; task 0's world (2400 plan, 2 waivers, both fees owed and recent) is outside (a)–(f), except for the R2-2 interaction.

**R2-2 — SOURCE-POLICY RED (overlapping waiver claims on one fee, no priority).**
- Pair 1: closing_returned_fee_relief ("granted without a request when a borrower with a pending early-closure request still owes the account's most recent returned-payment fee") vs returned_fee_relief ("granted without a request once its returned payment has been made good … a later payment has been credited toward the due date that returned payment was meant to pay"). Both are owed on the same fee whenever a made-good returned payment meets a pending request. Base "A fee may be waived once." admits one, and no sentence says which. Demonstrated on task 0's world in 0.md.
- Pair 2: closing_late_fee_relief vs goodwill_late_fee_credit on the most recent late fee when a borrower with a pending request asks for the late fee off.
Also: both pairs draw on the same courtesy count.

**R2-3 — SOURCE-POLICY RED (check 6: waited-on state not record-visible; two writes produce it).** Members:
- settlement ← closing late-fee relief: `relieve_late_fee_at_closing` vs `credit_goodwill_late_fee` both leave a courtesy waiver on the late fee.
- settlement ← closing returned-fee relief: `relieve_returned_fee_at_closing` vs `relieve_returned_payment_fee`.
- goodwill ← relief: `relieve_returned_payment_fee` vs `relieve_returned_fee_at_closing`.
The records cannot tell a reader whether the state "shows its early-closure relief" / "carries its returned-payment fee relief" already holds.

**R2-4 — SOURCE-POLICY RED (rule ≠ compute on edges; XF 8).** Members:
- `cc_addback` with cc_hold = 0: an online ACH posted today with no return in 3 months satisfies `DAYS ≤ 0` and is added back. The rule says "When no payment was returned in those 3 months, nothing is added back."
- `hl_paid`: amount past due above zero and below the monthly payment with no payment posted toward the oldest unpaid due date (e.g. a smaller final installment). Compute gives full; no rule tier covers the case.
- `hr_timing` / `hr_request`: a pending request registered before the return date (an AutoPay debit returned after the in-app request). `DAYS` is negative, so timing = 1 + d/60 > 1 with no cap at the fee, and the prompt-request addition fires for a request not "registered … after the return date".

**R2-5 — SOURCE-POLICY RED (XF 1: record selection shared by several factors, not one plain binding).** Members:
- closing_returned_fee_relief: most recent return read separately in hr_timing (hr_ret_amount, hr_ret_date), hr_reason (hr_code) and hr_request (a duplicate binding hr_ret_date2); pending request duplicated as hr_req_date / hr_request_date.
- returned_fee_relief: rr_ret_amount/rr_ret_date (rr_timing) and rr_code (rr_reason).
- returned_payment_fee_charge: rf_amount (rf_base) and rf_code (rf_reason).
- goodwill: gw_fee_due (gw_base) and gw_fee_date (gw_speed), alongside the plain gw_fee.
Relation to revision_1: the rf/rr/gw members existed in round 1 and the r1 audit passed XF 1 — an r1 audit miss, recorded here. No scored value moves on either world.

**R2-6 — SOURCE-FACTOR RED (realism, XF 12).** Settlement `cc_hold`/`cc_addback`: "an online ACH payment posted 10 or fewer days before today … is still clearing and its amount is added back to the total". The payment has already reduced the loan balance; adding it back takes the same money a second time from the savings. No rule returns it when it clears, and the base release window ("within the plan's release business days") already lets a lender hold the release until funds clear. A lender holds funds; it does not re-collect them. Struck: cc_hold; settlement keeps 3 factors (< 4).

Observations:
- O-2 widened: the request window vs three request-less reliefs.
- O-6: traceability detail lines not printed by the snapshot.
- O-7: no half-cent tie convention anywhere in the charter (consequence in task 1).
- O-1 and O-3 persist.

## closing_checklist (revision_2)
Written after both revision-2 reveals. Everything above under revision_2 was written before either reveal and is unchanged. **Not closed:** neither task has all four relationships at PASS.
- Files: `0.md` and `1.md` each carry revision_1 (untouched) and revision_2 (frozen derivation, comparison, findings).
- Scope: GT `charter_scope` of tasks 0 and 1 equals the partition inferred pre-reveal; disjoint and complete over the 8 policies. Tools: each claimed once; new uuid8s independent.
- Trees: task 0 has 3 prerequisite problems, 4 value_input edges, user-owned root: PASS. Task 1 has 3 prerequisite problems, 3 value_input edges plus 1 honest state_gate, user-owned leaf: PASS. The union graph is acyclic.
- Factors: every scored value and every factor_sensitivity / baseline_result figure in both tasks equals the auditor's blind figure. Counts:
  - meet the bounds: late fee 4, closing late-fee relief 6, closing returned-fee relief 5, returned fee 5, relief 6, goodwill 6, due day 5;
  - below the bounds: settlement 3 after the R2-6 strike.
- Round-1 charter REDs: CG-1, CG-3, CG-4, CG-5, CG-6, CG-7 (listed members), CG-8 closed; CG-2 closed as worded, but its class recurs as R2-1. No round-1 per-task finding regressed.
- New this round: R2-1, R2-2 (shown on task 0), R2-3, R2-4, R2-5 (includes members the r1 audit missed), R2-6 (shown on task 0), and the task 1 rounding tie (SOURCE-TASK).
- Gate re-run: the coordinator's snapshot (cited above) is the re-run on this form. Seven gates OK; traceability NOT OK, details not shown (O-6).
- Open charter-wide REDs: R2-1, R2-2, R2-3, R2-4, R2-5, R2-6.

VERDICT revision_2: task0=RED SOURCE-POLICY+SOURCE-FACTOR task1=RED SOURCE-TASK+SOURCE-POLICY charter=R2-1,R2-2,R2-3,R2-4,R2-5,R2-6

## revision_3

## charter_global_frozen (revision_3)
- Frozen 2026-10-16 (after the 22:47 snapshot) before any revision-3 GT was revealed; same auditor. Nothing below is derived from any masked field.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 3: gates 7/7 green` (only that line read).
- Gate snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 3` (2026-10-16T22:47:43): EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (detail suppressed, O-6).
- Hashes:
  - `builder.extended.yaml` 298f016bdb12f376ff618f23c90b375228211c4bc78ab800c5d6504b58c12f84: changed, so every charter-global section below is re-derived in full;
  - `task_tools.py` 1ba148f6ab1d3aecd33a341ddbb19fa0312948e356655ec606341ad9dc98cc50: unchanged, so the r2 tool findings (uuid8s, docstrings, bodies) carry forward by reference;
  - views r3/task_0.json d65215df…fe85: identical to r2, but the charter moved, so task 0 is re-derived;
  - r3/task_1.json 0bd1a280…b68a: changed, with one diff, the 10-05 online payment and its 10-08 return now 62.00 instead of 60.00.
- Claims read by item id only. Masked/unread as before.
- Base copy still byte-identical.

### policy_conflict_scan (r3)
Same eight policies and the same partition (task 0: late fee, closing late-fee relief, closing returned-fee relief, settlement; task 1: returned fee, made-good relief, AutoPay re-enrollment, goodwill).
The four `builder_fee_waived` claimants now carry priority sentences:
- while an early-closure request is pending, the early-closure late-fee relief displaces the goodwill credit, and the early-closure returned-fee relief displaces the made-good relief;
- the two closing reliefs ignore the courtesy count (declared);
- the three request-less reliefs are freed from the request window by three sibling overwrites, each naming the other two (XF 4 passes);
- goodwill keeps the window, and its compute enforces it.
No overlapping claim remains: the made-good relief and the goodwill credit compute to nothing when a request is pending. Cross-category reads are as in r2.

### rule_compute_equivalence (r3)
- `mech.py` sweep is clean: all compute_basis quotes, baselines, prerequisite sources and replaced_by texts are verbatim, and action-form edges carry `fallback_reason` exactly.
- Every money policy now states "Every rounding to the cent in this policy goes to the nearest cent, a half cent or more rounding up" and computes `int(x*100 + 0.500001)/100` at the stated points (XF 6 passes).
- Each policy states its not-owed / 0.00 cases and its compute returns 0 for them.
- Edges re-probed:
  - cc_lead now reads the chargeback of that very payment;
  - hl_paid covers past due with no payment toward the due date (halved);
  - hr_timing and hr_request floor and exclude a request made before the return;
  - rr reads "made good" by the date of the latest payment toward the returned payment's due date;
  - goodwill computes its window, count, pending and AutoPay gate.
- Remaining divergences: R3-2 and R3-3.

### prerequisite_graph and prerequisite_sentences (r3)
Edges as in r2. settlement ← closing late-fee relief, settlement ← closing returned-fee relief and goodwill ← made-good relief are now **action form** ("…the early-closure late-fee relief owed on the account, if any, has been granted", etc.). Each has a fallback_reason: the relief's row is the same courtesy-waiver row another policy leaves, and a relief not owed leaves no row. Tested and justified: no record-visible state singles out the write.
The state-form edges each have a single writer:
- settlement ← late fee and closing late-fee relief ← late fee ("…carries its late fee, unless that late fee comes to 0.00");
- made-good relief ← returned fee and goodwill ← returned fee (most recent return only, "unless that fee comes to 0.00");
- goodwill ← AutoPay.
All pass the four-point test, and every "if any" / "unless 0.00" clause matches its `condition`. Acyclic. No undeclared cross-problem order.

### override_declarations (r3)
As in r2, plus four sibling overwrites:
- two sibling overwrites retire "A courtesy waiver is granted on request…", now "granted however many have already been granted" for the closing reliefs;
- three sibling overwrites retire "A courtesy waiver must be requested no later than the fee waiver request window…" for the three request-less reliefs.
- autopay_reenrollment (`overwrite: []`) now writes a case the base does not provide for — R3-2.

### factor_ladders (r3)
Counts (P/M; X = cross-difficulty):
- late fee 3/1 (X 1);
- settlement cc_lead M, cc_rate X, cc_hardship X, **cc_record** (12+ / 6–11 credited payments → closing interest ×0.9 / ×0.95);
- closing late-fee relief 5/1;
- closing returned-fee relief 4/1;
- returned fee 4/1;
- made-good relief 5/1;
- goodwill 5/1;
- re-enrollment 4/1 (X 3).
No cross-factor reads. Every shared record selection is a plain binding (hl_fee_id, hr_ret_id/hr_ret_date/hr_req_date, rf_ret_id, rr_ret_id/rr_good_date/rr_fee_id, gw_fee_id/gw_fee/gw_fee_due/gw_fee_date); R2-5 closed. All fall-throughs are reachable; method tiers change shape; no factor id is in a tool name. Realism: R3-1.

### findings (r3)
Round-2 REDs:
- **R2-1 closed.** Every wait is now met in every reachable world. Each relief or fee states its not-owed cases. Waits say "if any" / "unless 0.00". The closing reliefs ignore the count and the window. Members (a)–(f) all re-probed.
- **R2-2 closed.** Priority sentences exist and computes return nothing.
- **R2-3 closed.** Justified action form.
- **R2-4 closed.** All three members re-probed.
- **R2-5 closed.**
- **R2-6 closed as worded** (the add-back is gone), but its replacement factor recreates the round-1 CG-4 class — R3-1.
- **T1 rounding tie closed.** Half-up is stated; the task 1 fee is now 2.0925, not a tie.

**R3-1 — SOURCE-FACTOR RED (realism, XF 12; regression of the CG-4 class).** The rule says: "When 12 or more payments have been credited to the account …, the closing interest is multiplied by the twelve-payment share. When 6 to 11 payments have been credited …, the six-payment share."
- The discount exists only at early closure. Every scheduled payment still pays the full APR (base interest APR/1200), so a borrower who breaks the plan early pays a lower effective rate than one who keeps it.
- It is the same treatment as round-1 cc_rate seasoning and cc_tenure, which were struck as unreal. The hardship-based cc_rate and cc_hardship are kept, as in r1/r2.
- Only member: cc_record. Struck, so the settlement keeps 3 factors (< 4).

**R3-2 — SOURCE-POLICY RED (undeclared departure + realism: re-enrollment can defer an installment by a month).** Rule: "When the buffers add to 0 days, the due day stays the current due day …, the first new due date again being the first date on that day later than the current next due date." With a next due date of 10-15 and day 15, the "first new due date" is 11-15: the 10-15 installment's due date is pushed back a month with no due-day change.
- The base gives Credit Builder no deferral (`payment_deferral_available: false`, "Credit Builder has no hardship programs"), and its due-day sentence governs a changed day. No overwrite is declared, and no lender defers an installment because AutoPay was turned back on.
- Members:
  - (i) buffers sum to 0;
  - (ii) current due day 28, where the 28-day cap leaves the day unchanged whatever the buffers.
- Neither task's world reaches it (task 1's buffers total 12).

**R3-3 — SOURCE-POLICY RED (owed fee with no amount; rule gap).** Members:
- late_fee_charge: "A late fee is owed for a due date once its grace period has ended with the installment still unpaid", but "The late due date is the account's oldest unpaid due date …, and the late fee is figured for it". An account two installments behind whose oldest due date already carries its fee owes a fee for the second lapsed due date. No sentence figures it, and "at most once per due date" bars re-using the oldest.
- returned_payment_fee_charge: "A returned-payment fee is owed for a returned payment whose return code carries a fee as soon as the return is booked", but "The fee is figured for the account's most recent returned payment". Two fee-bearing returns booked before either is charged leave the older one owed with no amount.
No task world reaches either case. Relation: the returned-fee member existed since round 1 — an audit miss in r1/r2. The late-fee member became explicit with r3's new "late due date" sentence.

Observations: O-1, O-3, O-6 persist. O-2 is resolved by the declared window overwrites. O-7 is resolved.

## closing_checklist (revision_3)
Written after both revision-3 reveals. Everything above under revision_3 is pre-reveal and unchanged. **Not closed.**
- Files: `0.md` and `1.md` carry revision_1 … revision_3. Scope: GT `charter_scope` equals the inferred partition; disjoint and complete. Tools unchanged (r2 conclusions carried by hash).
- Trees: task 0 has 3 prerequisite problems, 4 value_input edges, user root; task 1 has 3 prerequisite problems, 3 value_input edges plus 1 state_gate, user leaf. Both PASS; the union is acyclic.
- Factors: every scored value and every sensitivity / baseline figure of both tasks equals the auditor's blind figure. Counts are within bounds except the settlement: 3 after the R3-1 strike.
- Round-2 REDs: R2-1, R2-2, R2-3, R2-4, R2-5 and the task 1 rounding tie are closed. R2-6 is closed as worded but re-opened in class as R3-1.
- New: R3-1 (regression of the CG-4 class), R3-2 (re-enrollment month skip), R3-3 (owed fees with no amount: late-fee and returned-fee members, the latter an r1/r2 audit miss).
- XF recipe re-checked on all 8 policies: points 1–7 and 9–11 pass, 13 (tools) passes unchanged, 14 (proof text) passes. Point 8 has members R3-2 (ii) and R3-3; point 12 has members R3-1 and R3-2.
- Gate re-run = the coordinator's r3 snapshot (7 OK; traceability detail suppressed, O-6).
- Open charter-wide REDs: R3-1, R3-2, R3-3.

VERDICT revision_3: task0=RED SOURCE-FACTOR+SOURCE-POLICY task1=RED SOURCE-POLICY charter=R3-1,R3-2,R3-3

## revision_4

## charter_global_frozen (revision_4)
- Frozen 2026-10-16 (after the 23:25 snapshot) before any revision-4 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 4: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 4` (2026-10-16T23:25:16): EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK. Per the coordinator, every miss is pre-publication and an unlock tool name, re-checked after rendering (O-6).
- Hashes:
  - `builder.extended.yaml` 1306a7483ee18b4dc090bc81d98dd4787308cad65fa6ec736720609b37c482ea: changed;
  - `task_tools.py` 1ba148f6…cc50: unchanged, so the r2 tool conclusions carry forward;
  - views r4/task_0.json d65215df…fe85 and r4/task_1.json 0bd1a280…b68a: byte-identical to r3.
- Claims read by id only. Base copy still byte-identical.
- What moved (re-derived in full): late_fee_charge (overwrite and narrowing), returned_payment_fee_charge (overwrite and narrowing), settlement (cc_record → cc_cause), autopay_reenrollment (new declared overwrite, no-change cases). The other four policies were re-swept mechanically and against every XF point.

### charter checks (r4)
- `mech.py` sweep clean on all 8 policies: quotes, baselines, prerequisite sources, replaced_by texts and fallback pairing; no cross-factor reads; no factor id in a tool name. Factor counts 4/4/6/5/5/6/6/5, each with exactly one method factor.
- Override declarations:
  - late fee: "charged at most once per due date, only for the account's oldest unpaid due date …", plus "A later due date that lapses while an older installment is still unpaid carries no late fee of its own …; once the older installment is paid, the later due date becomes the oldest unpaid due date and its late fee is figured then";
  - returned fee: "…only for the account's most recent returned payment …", plus "a run of returns booked before the fee is charged costs one returned-payment fee";
  - re-enrollment: a new self-scoped overwrite of the base due-day clause, restating it for every other account (XF 4 form passes).
- The settlement and goodwill fee waits ("oldest unpaid due date … carries its late fee"; "most recent returned payment … shows its returned-payment fee") match the narrowed fee rules exactly.
- Realism:
  - `cc_cause`: closing interest × 0.8 for an active plan granted for death of a household earner / natural disaster / medical hardship, × 0.9 for job loss / reduced income / divorce. It is hardship-only, and grounded in the base's own text (`payment_deferral_available`: "Credit Builder has no hardship programs; a borrower in hardship may close early instead"), so it is not the CG-4 / R3-1 class. Every tier is reachable: the reasons "other" and the servicemember / charged-off reasons and the no-plan case fall through.
  - Observation O-8: three of the four settlement factors read the borrower's hardship plans and compound.
- Re-enrollment edges probed:
  - zero buffers / the 28 cap → unchanged day and next due date;
  - an amount past due → unchanged, compute `F('payment_due_day') if amount_past_due > 0`;
  - a moved day falls in the same month as the current next due date, since buffers are ≥ 0.
- No new XF member found on any policy (points 1–14).

### findings (r4)
Round-3 REDs:
- **R3-1 closed.** cc_record is struck. The settlement has four honest factors: cc_lead M, cc_rate, cc_hardship, cc_cause. No closing-interest tier now favours an early exit over the schedule except through hardship, which the base names as the Credit Builder hardship route.
- **R3-2 closed.** The reset is a declared, scoped overwrite. No-change cases keep the next due date. Past-due accounts keep their oldest unpaid due date. No installment can be deferred.
- **R3-3 closed, both members.** Each fee is owed only for the one record its policy prices, the narrowing is declared, and the narrowing is realistic (a late fee is not charged only because an earlier installment is unpaid; one fee per run of returns).
New charter REDs: none.
Observations:
- O-1: the variant method texts persist.
- O-3: the release-timing sentence.
- O-6: traceability, pre-publication.
- O-8: compounding hardship reductions in the settlement.

## closing_checklist (revision_4)
Written after both revision-4 reveals; the revision_4 charter section above is pre-reveal and unchanged. **All four relationships PASS for both tasks.**
- Audit files: `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json, alongside this file. Revisions 1–4 are preserved in order, and every revision-4 comparison section carries PASS.
- Coverage and scope:
  - all 8 extended policies are covered;
  - GT `charter_scope`: task 0 {late fee, closing late-fee relief, closing returned-fee relief, settlement}, task 1 {returned fee, made-good relief, AutoPay re-enrollment, goodwill}, pairwise disjoint over each whole tree and jointly complete;
  - the task tools and GT are closed; each tool is claimed once with an independently generated, frozen uuid8 (fbf509e1, 8372931d, c21c573e, 90cd40e1, 1f748b6c, d8e21ef6, 43fbbd15, 5af065e7).
- Trees:
  - task 0: 3 prerequisite problems, 4 value_input edges, user-owned root (confirm_early_closure);
  - task 1: 3 prerequisite problems, 3 value_input edges plus 1 state_gate, user-owned leaf (reenroll_autopay);
  - no cycles; the union of both difficulties' edges is acyclic. Every edge is unmet at frozen_time and bears weight; no waits; the tools judge nothing.
- Factors:
  - every computation declares a self-sufficient baseline and 4–6 factors with exactly one method (late fee 4, settlement 4, closing late-fee relief 6, closing returned-fee relief 5, returned fee 5, made-good relief 6, goodwill 6, re-enrollment 5);
  - each task has multi-source factors (lf_pct, hl_season / rf_seasoning, rr_season, gw_loan) and cross-difficulty factors (hardship, loan, line, pos);
  - every ladder has 3 disjoint, reachable tiers stated in full in its rule;
  - every factor bears weight against an honest baseline on its task's world, and the all-baseline figure differs from gold in every computation (5.86 / 0.17 / 0.35 / 1177.86; 10.00 / 0.63 / 15 / 0.28);
  - scored values and sensitivities match the auditor's blind figures in every revision-4 computation.
- XF recipe points 1–14 re-checked on all 8 policies; no member remains.
- Gate re-run on the final form: the coordinator's r4 snapshot. EXTENDED, TASK TOOL CONTRACT, REPLAY (--check), SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK. TRACEABILITY NOT OK pre-publication only (unlock tool names, per the coordinator; re-checked after rendering; O-6).
- Open REDs: none. Observations carried: O-1, O-3, O-6, O-8.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Frozen 2026-10-17 (after the 03:06 snapshot) before any revision-5 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 5: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 5` (2026-10-17T03:06:57): EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK (pre-publication, O-6).
- Hashes:
  - `builder.extended.yaml` 042bb7afbdfc663177dda0657a393f41af12450a0460034439faca00fc9d84d4: changed;
  - `task_tools.py` f8707267e656aa979baa7577f81f4cad01bbc69e7eb51847feb2c1bf22dc9346: changed, docstrings only; bodies, names, uuid8s and imports are as before;
  - views r5/task_0.json d65215df…fe85 and r5/task_1.json 0bd1a280…b68a: byte-identical to r4.
- Inputs: the renderer's source scan `audits/render_source/credit_builder_accounts/render_r1.md` (S1–S7) and `rework_r5_claims.md`, both read by id. Every rule sentence carrying a window, a month count, a day count or the defined terms was re-read across all 8 policies. `mech.py` sweep clean: quotes, baselines, prerequisite sources, replaced_by texts, fallback pairing, binding order, no cross-factor reads; factor counts 4/4/6/5/5/6/6/5, one method each.

### S1–S7 closure check (whole class each)
- **S1 closed.** Rule "Where one or more debit card payments have been credited … that net never counted below zero" matches `lf_base` (`lf_dc_count >= 1` branch) and `lf_dc_credit = MX(0, …)`. The chargeback scope of that net is a separate defect — R5-2.
- **S2 closed.** All five "no … other than this one" counts (`hl_first`, `hr_first`, `rf_history`, `rr_first`, `gw_history`) now compare `<= 0`.
- **S3 closed.** Every whole-calendar-month window states both ends in the sentence that uses it ("a … dated today [the assessment date] counts, and one dated on the same day of the month N months earlier falls outside"). Swept: lf_prior_late, lf_returns, hl_other_late, hr_line (1 and 3 months), hr_other, rf_other_returns, rf_line (1 and 3), rr_used, rr_other, rr_line_n, gw_used, the gw AutoPay gate, gw_recent_return, gw_base tier 2, gw_loan_late, gw_other_late, gw_returns_3m, ad_ap_returns, ad_line_returns, ad_loan_returns/late, ad_pos_returns/late. All match `within_months` (0 ≤ MONTHS < N).
  - Far-end month-end probe: when today's day does not exist in the earlier month (e.g. today 03-31, row 02-28), every row of that shorter month is outside under any reading and under `MONTHS`. No divergence.
- **S4 closed.** All five months-open tests (lf_pct, hl_season, rf_seasoning, rr_season, gw_tenure) state "whole calendar months from the open date, each complete on the day of the month matching the opening day or, in a month too short for that day, on the first day of the following month". Probed against `MONTHS`: open 2025-08-31 completes month 1 on 10-01 and month 2 on 10-31; open 2024-02-29 completes month 12 on 2025-03-01. Matches.
- **S5 closed as worded.** gw_base tier 2 now carries its own boundary. "AutoPay debit" now has one meaning everywhere (amount = monthly payment). That meaning is itself a defect — R5-1.
- **S6 closed.** `confirm_early_closure` now says "an amount of 0.00 or more". `reenroll_autopay` says "(the current due day when it does not change)" and "the current next due date when the due day does not change". Every other money docstring says "positive", which matches its rule's "a … that comes to 0.00 is not charged / not booked". Docstring-vs-rule-branch class swept over all 8 tools.
- **S7 closed.** Every day count states its convention as computed:
  - settlement interest days: "the closing date less that due date";
  - hr_timing / rr_timing: "each calendar day after the return date up to and including …";
  - hr_request: "on the return date or 1 to 7 calendar days after";
  - hl_age / rr_age: "today less the fee's date";
  - gw_speed: "the request date … less the fee's date";
  - goodwill window: "from the day after it, a request on the last day being in time";
  - cc_lead tier 2: "the amount past due divided by the monthly payment, rounded down, the oldest unpaid installment included", which matches `int(pd/mp)*30`.
- **Round-4:** no REDs were open. The r4 closures (R3-1, R3-2, R3-3) are intact: cc_cause is unchanged, the re-enrollment overwrite and no-change cases are unchanged, the fee narrowings are unchanged.

### findings (r5)
**R5-1 — SOURCE-POLICY RED (term definition contradicts the records; realism, XF 12).** "AutoPay debit" is defined by amount ("a payment whose amount equals the monthly payment"), not by the channel the ledger records (`payment_channel='autopay_ach'`). A borrower's own one-time payment of exactly the monthly amount becomes an "AutoPay debit". Every member of the class, at once:
- goodwill AutoPay gate (`gw_ap_returned`): "A goodwill credit for a borrower whose AutoPay debit (a payment whose amount equals the monthly payment) was returned in the 3 whole calendar months before today … is not granted until the account is enrolled in AutoPay";
- goodwill `gw_base` tier 2 (`gw_autopay_toward`, `amount=monthly_payment_amount`);
- autopay_reenrollment scope ("a borrower whose AutoPay debit was returned turns AutoPay on again") and `ad_ap_returns`;
- closing_returned_fee_relief `hr_timing` tier 1;
- returned_fee_relief `rr_timing` tier 1.

Demonstration: a borrower never enrolled in AutoPay whose one-time online payment of exactly the monthly amount was returned last month asks for goodwill on a late fee. The rule refuses the credit until he enrols in AutoPay, and then resets his due day as a re-enrolment ("turns AutoPay on again") though he never had AutoPay. A real lender keys AutoPay treatment to AutoPay debits; Larkspur's own ledger records which debits were AutoPay. On task 1's world, `gw_autopay_toward` counts Andre's manual 2026-10-09 online payment (104.72) as an AutoPay debit. It changes no value there because gw_base tier 1 fires first. Relation: the hr/rr members carried the amount proxy since r1 (accepted as a proxy then); the r5 rework spread it to the goodwill gate and base and the re-enrolment count to close S5(a). The class is open as a whole.

**R5-2 — SOURCE-POLICY RED (one term, two readings across policies; realism).** "debit card payment credited toward the due date, net of chargebacks":
- late_fee_charge nets "every debit card chargeback (return code CB) booked on the account" (`lf_dc_credit` subtracts every CB row);
- the settlement's cc_lead asks whether "the most recent debit card payment credited toward the oldest unpaid due date has not been charged back" (`cc_dc_cb`, the chargeback of that very payment).

Demonstration on task 0's world plus one old row (a 50.00 debit card payment toward 2026-02-28, charged back 2026-03-05): the late fee treats the current 40.00 debit card credit as wiped out (base 117.16 instead of 77.16), while the settlement treats the same 40.00 payment as standing and paying the installment's interest (lead 0). No lender nets an unrelated old chargeback against this installment's credit. Members: `lf_dc_credit` (the defective one) against the `cc_dc_cb` reading. The r3 rework introduced the account-wide netting; no task world carries a CB row.

Observations: O-1, O-3, O-6, O-8 persist.

## closing_checklist (revision_5)
Written after both revision-5 reveals; the revision_5 charter section above is pre-reveal and unchanged. **Not closed.**
- Files: `0.md` and `1.md` carry revisions 1–5. Scope and tools are unchanged: same partition, same uuid8s, docstrings now consistent with every rule branch (S6).
- Trees: task 0 has 3 prerequisite problems, 4 value_input edges, user root; task 1 has 3 prerequisite problems, 3 value_input edges plus 1 state_gate, user leaf. Both PASS; the union is acyclic.
- Factors: every scored value and every sensitivity / baseline figure equals the auditor's blind figure in both tasks. Counts are within bounds, with one honest method each.
- Renderer scan: S1, S2, S3, S4, S6 and S7 are closed with their whole classes (members listed above). S5(b) is closed. S5(a) is closed as worded, but the chosen definition is R5-1.
- New: R5-1 (AutoPay debit defined by amount; 5 members) and R5-2 (chargeback netting read two ways; late fee vs settlement).
- The XF recipe was re-checked on all 8 policies; point 12 (realism / records) has members R5-1 and R5-2, and the other points pass.
- Gate re-run = the coordinator's r5 snapshot (7 OK; traceability pre-publication, O-6).
- Open charter-wide REDs: R5-1, R5-2.

VERDICT revision_5: task0=RED SOURCE-POLICY task1=RED SOURCE-POLICY charter=R5-1,R5-2

## revision_6

## charter_global_frozen (revision_6)
- Frozen 2026-10-17 (after the 03:50 snapshot) before any revision-6 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 6: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 6` (2026-10-17T03:50:18): 7 gates OK; TRACEABILITY NOT OK (pre-publication, O-6).
- Hashes:
  - `builder.extended.yaml` 016fe35032bd09b0684b36b8c7a1f7efc0bb093fc0768bda4ebfa7036f3b310a: changed;
  - `task_tools.py` f8707267…9346: unchanged since r5, so the tool conclusions carry forward;
  - views r6/task_0.json bdd505a401a07c9846ea49ca84e900753af61534d3e12bf4933fd6714e68d2ba and r6/task_1.json 1785b22f094438004183f6bab80b261620476dbf8adf04795099d12b902921d5: changed.
- Seed diff r5 → r6 is exactly four rows: each task's two `builder_payment_returned` lines gained `payment_channel` and `installment_due_date` copied from the reversed payment (task 0: b2a9795b autopay_ach / 41d9e490 online_ach; task 1: 8c21ba81 autopay_ach / 6dac29a8 online_ach). Frozen time and personas are unchanged.
- Claims read by id. `mech.py` sweep clean on all 8 policies; factor counts 4/4/6/5/5/6/6/5, one method each.
- S1–S7 regression sweep:
  - S1: lf branch on count ≥ 1, net floored;
  - S2: all five `<= 0`;
  - S3: all 22 whole-month window sentences carry today/far-end boundaries or back-reference one that does;
  - S4: all months-open tests carry the short-month convention or follow the sentence that states it;
  - S6: docstrings unchanged since r5;
  - S7: day-count phrases present.
  Nothing regressed.

### R5-1 / R5-2 closure check
- **R5-1 closed in definition.** "AutoPay debit" is now "a payment made through the AutoPay channel" in every sentence that uses it. gw_base tier 2 (`gw_autopay_toward`) reads the posted payment's `payment_channel='autopay_ach'`, a field the base event `builder_payment_posted` records ("payment_channel: How paid"). The timing ladders now read AutoPay / any other < monthly / any other ≥ monthly, complete with no gap. But the *returned* AutoPay debit is identified by the return line "carrying that AutoPay channel" — R6-1.
- **R5-2 closed in wording, not in substance.** Both rules now say a debit card payment is netted only of "its own chargeback". The settlement identifies it by `related_txn_id` (`cc_dc_cb`). The late fee identifies it by a CB line "carrying its debit card channel and due date" (`lf_dc_credit` sums CB lines with `payment_channel='debit_card', installment_due_date=next_due_date`). The unrelated-chargeback probe now passes: lf_base 77.16, cc_lead 0. The two readings still diverge on a chargeback recorded as the charter writes it — R6-1.

### findings (r6)
**R6-1 — SOURCE-POLICY RED (undeclared extension of the base event; one term read two ways; XF 8/12).** The base event `builder_payment_returned` (verbatim, not overwritten) records `txn_date, amount, related_txn_id, return_code, interest_portion, principal_portion` — no `payment_channel`, no `installment_due_date`. The r6 rules define a return by its return line "carr[ying] that AutoPay channel" / "carr[ying] its debit card channel and due date", the computes read those fields off the return row, and the r6 seed adds them to the four return rows. The reversed payment's own fields, reached through `related_txn_id` (as `cc_dc_cb` and `rr_ret_pay` already do), are what the charter's records actually carry. Every member, at once:
- `lf_dc_credit` (late fee: own chargeback by return-row channel and due date);
- `gw_ap_returned` (goodwill AutoPay gate: return-row channel);
- `ad_ap_returns` (re-enrollment return count / scope: return-row channel);
- `hr_ap` (early-closure returned-fee relief, timing tier 1);
- `rr_ap` (made-good relief, timing tier 1).
Demonstrations, with return lines written as the base event writes them:
- **Task 0 world + a CB line reversing the 40.00 debit card payment b1a58719 (`related_txn_id` set, no channel or due date):** the late fee still credits the 40.00 (lf_base 77.16, where its own rule says 117.16), while the settlement says it was charged back (cc_lead 30). The same payment and the same term give two answers.
- **Task 1 world with the two added fields absent (the r5 seed):** the goodwill AutoPay gate does not fire (the credit is 1.06 without enrolment), and the re-enrolment due day is 24 instead of 27. Task 1's AutoPay edge and `ad_return_buf` tier rest on seed fields the charter's return event never writes.
Relation: R5-1/R5-2's fix introduced this. The class is open as a whole.

Observations: O-1, O-3, O-6, O-8 persist.

## closing_checklist (revision_6)
Written after both revision-6 reveals; the revision_6 charter section above is pre-reveal and unchanged. **Not closed.**
- Files: revisions 1–6 present in `0.md` and `1.md`. Scope and tools unchanged.
- Trees and factor counts as in r5. Every scored value and sensitivity / baseline figure equals the auditor's blind figure in both tasks.
- Task 1's AutoPay edge and `ad_return_buf` tier rest on seed-only return-line fields (R6-1).
- Round-5 REDs:
  - R5-1: closed in definition ("AutoPay debit" = AutoPay channel), but the *returned* debit is read off a return-line field the charter does not record;
  - R5-2: closed for unrelated chargebacks, but the late fee and the settlement still identify "own chargeback" differently.
  Both recur as R6-1.
- S1–S7: no regression (swept).
- XF recipe: point 8 (decoy-row probe) and point 12 (seeded rows the owning charter can produce) have members, all five listed under R6-1; the other points pass.
- Gate re-run = the coordinator's r6 snapshot (7 OK; traceability pre-publication).
- Open charter-wide REDs: R6-1.

VERDICT revision_6: task0=RED SOURCE-POLICY task1=RED SOURCE-POLICY+SOURCE-FACTOR+SOURCE-CHAIN charter=R6-1

## revision_7

## charter_global_frozen (revision_7)
- Frozen 2026-10-17 (after the 04:19 snapshot) before any revision-7 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 7: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 7` (2026-10-17T04:19:55): 7 gates OK; TRACEABILITY NOT OK (pre-publication, O-6).
- Hashes:
  - `builder.extended.yaml` 39e37e1f3b8163852a9cfc6c933f4c06b4e4c07c93b6646b5edc61094476975e: changed;
  - `task_tools.py` f8707267…9346: unchanged since r5;
  - views r7/task_0.json d65215df…fe85 and r7/task_1.json 0bd1a280…b68a: byte-identical to r5 (the four r6 return-line fields are reverted).
- Claims read by id. `mech.py` sweep clean on all 8 policies; factor counts 4/4/6/5/5/6/6/5, one method each, every ladder ≥ 3 tiers.
- Field-provenance scan: no event-typed read in any compute filters on or reads a field its base event does not write. Every channel or due-date read on a returned payment goes through the posted payment its `related_txn_id` names.
- S1–S7 regression sweep:
  - S1: lf branch on count ≥ 1, never below zero;
  - S2: all `<= 0`;
  - S3: all 22 window sentences carry their boundaries;
  - S4: months-open conventions present;
  - S6: docstrings unchanged since r5;
  - S7: day-count phrases present, plus the new "(the return date less the debit date) plus one".
  No regression.

### R6-1 closure check (every member)
`lf_dc_cb`, `gw_ap_returned` (now: the latest AutoPay-channel payment, returned in 3 months via `related_txn_id`), `ad_ap_returns` / `ad_ap_ret_date` (same), `hr_ap`, `rr_ap` (the reversed payment's `payment_channel`). The late fee and the settlement now read "own chargeback" identically (a CB return pointing at the most recent debit card payment toward the due date). Probe re-run on task 0's world with a charter-shaped CB of the 40.00 payment: lf_base 117.16 and cc_lead 30, now consistent. Task 1's AutoPay edge and buffer hold on the charter-shaped (r5) seed: gate 1, buffer 3. **R6-1 closed.**

### findings (r7)
**R7-1 — SOURCE-FACTOR RED (realism, XF 12; introduced by the R6-1 fix).** `lf_base` tier 1 became "the fee is figured on the monthly payment less the most recent such debit card payment, which is not counted when a chargeback has reversed it". Every other debit card payment credited toward the same late due date is ignored.
- Demonstration on task 0's world plus a 30.00 card payment toward 2026-09-28 on 10-01: base 77.16, although 70.00 was paid by card (the r6 rule gave 47.16).
- If the 40.00 is then charged back, the base is the full 117.16 while the 30.00 card payment still stands (87.16 by that payment).
- No lender figuring a late fee on what card payments left unpaid would count only the latest card payment.
- Only member. Observation O-9 (not raised): the base has always ignored ACH credits toward the due date; a good-funds rationale (card payments cannot be returned NSF) makes that tier defensible.

**R7-2 — SOURCE-FACTOR RED (realism: a condition no lender weighs for the due day; introduced with the R6-1 fix).** `ad_return_buf` became "the buffer is those days (the return date less the debit date) plus one" (2 days when returned the same or next day).
- The gap between an AutoPay debit and its return is set by the ACH return timeline: NSF returns come back within two banking days, so the gap tracks weekends and holidays, and R07/R10 returns can come up to 60 days later. It says nothing about when the borrower's funds arrive.
- Demonstration on task 1's world: the same R07 return one calendar day earlier (09-16) gives due day 26 instead of 27; a weekend between debit and return would add days. An R07 return 30 days after the debit pushes any due day to the 28 cap.
- Struck: `ad_return_buf` is the re-enrollment's only method factor, so the re-enrollment keeps 4 parameter factors (0 method; count RED).
- Only member: the other buffers read return codes, counts and other-product returns, which are funds-timing evidence, as accepted since r3.

Observations: O-1, O-3, O-6, O-8, and the new O-9 (the late-fee base ignores ACH credits; tolerated under the good-funds reading).

## closing_checklist (revision_7)
Written after both revision-7 reveals; the revision_7 charter section above is pre-reveal and unchanged. **Not closed.**
- Files: revisions 1–7 present in `0.md` and `1.md`. Scope and tools unchanged.
- Trees: both PASS on charter-shaped seeds, acyclic.
- Values: every scored value and every sensitivity / baseline figure equals the auditor's blind figure.
- R6-1 closed with every member. S1–S7: no regression.
- New:
  - R7-1: the late-fee base counts only the most recent card payment;
  - R7-2: the re-enrollment buffer from the ACH return lag; the re-enrollment's only method factor is struck.
  Both were introduced by the R6-1 rework.
- XF recipe: point 12 (realism) has members R7-1 and R7-2; point 9 is affected by the R7-2 strike (re-enrollment 0 honest method factors); the other points pass.
- Gate re-run = the coordinator's r7 snapshot (7 OK; traceability pre-publication).
- Open charter-wide REDs: R7-1, R7-2.

VERDICT revision_7: task0=RED SOURCE-FACTOR task1=RED SOURCE-FACTOR charter=R7-1,R7-2

## revision_8

## charter_global_frozen (revision_8)
- Frozen 2026-10-17 (after the 13:08 snapshot) before any revision-8 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 8: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 8` (2026-10-17T13:08:09): 7 gates OK; TRACEABILITY NOT OK (pre-publication, O-6).
- Hashes:
  - `builder.extended.yaml` db3999dcc113d8134bc7d40ef891f21a77364a087bd0dca14dc96c6480894115: changed;
  - `task_tools.py` f8707267…9346: unchanged;
  - views r8/task_0.json d65215df…fe85 and r8/task_1.json 0bd1a280…b68a: unchanged since r5.
- Claims read by id. `mech.py` sweep clean; factor counts 4/4/6/5/5/6/6/5, one method each, every ladder ≥ 3.
- S1–S7 regression: 22/22 window sentences bounded; months-open, day-count and rounding conventions present; docstrings unchanged. No regression.
- Sibling-renderer classes swept over all 8 policies:
  - (a) convention sentence serving several factors: none. No compute_basis sentence is quoted by bindings of two factors; the shared most-recent-record selections are plain-binding sentences.
  - (b) factor taking effect only through another factor: none. No factor binding reads another factor's binding.
  - (c) non-factor binding defined only by one factor's sentence: two members, R8-2.

### R7-1 closure check (the coordinator's route)
- Overwrite replaced_by: "…for a late due date with no more than one debit card payment credited toward it, and only for such a due date, its amount is figured as this policy sets out …; every other late due date remains under the base clause: The late fee is late_fee_percent of the monthly payment, rounded to the cent and not more than late_fee_max_usd, at most max_late_fees_per_due_date per due date, and only on an account in active status."
  - The scope is stated exactly and self-named (XF 4/11 form).
  - The out-of-scope content is the superseded clause verbatim.
  - The rule carries the same sentence. Inside the scope, tier 1 reads "Where one debit card payment has been credited … less that payment, which is not counted when a chargeback has reversed it (a return with code CB whose line points at that payment)", the same reading as the settlement's `cc_dc_cb`.
- Compute: `result` takes `MN(late_fee_max, half-up(monthly × late_fee_percent / 100))` when `lf_dc_count >= 2`, i.e. the base clause. Probe on task 0's world plus a second card payment: 5.86 = 5 % × 117.16. The once-per-due-date and active limits are kept by `lf_charged` and the shared sentence.
- Out-of-scope cases really stay under the in-force base content. **R7-1 closed.**
- Observation O-10: the scope boundary is not monotone. A second card payment toward the same installment moves the fee from the extended figure (0.87 on task 0's world) to the flat base fee (5.86). This is inherent in the XF 11 route-around (the DSL cannot net each of several payments against its own chargeback), and the coordinator decided this route; it is recorded, not raised.

### R7-2 closure check
`ad_return_buf` now reads when the borrower made the returned AutoPay debit good:
- made good within the late-fee grace period → buffer = (make-good date less the debit's due date) + 1, "so the new due day falls the day after the borrower's funds arrived";
- made good later, or not yet → flat 3;
- no returned AutoPay debit in 12 months → none.
This is genuine funds-timing evidence. All tiers are reachable, it is honestly a method (computed lag vs flat vs none), and the re-enrollment keeps one method factor. **R7-2 closed**, subject to R8-1.

### findings (r8)
**R8-1 — SOURCE-POLICY RED (decoy row; XF 8; contradicts base "A returned payment is reversed in full and its installment is unpaid again").**
- The make-good test is "the latest payment posted toward that due date is dated after the return and no more than the plan's late-fee grace days after the due date". `ad_good_date` takes the latest posted payment toward the due date whether or not that payment was itself returned.
- A make-good payment that bounced therefore counts as "the borrower's funds arrived".
- Probe on task 1's world: the 10-05 / 10-08 / 10-09 rows replaced by a 104.72 online payment on 09-25 toward 09-15 that is returned R10 on 09-29. Lag 10 ≤ 15, so buffer 11. By the policy's own words the debit "has not been made good", so the flat 3.
- Only member. The made-good relief's `rr_good_date` is not a member: a bounced make-good payment becomes the account's most recent return, so the relief then concerns that return.

**R8-2 — SOURCE-POLICY RED (sibling-renderer class (c): a non-factor binding read by one factor only and defined only in that factor's sentence).** Members, every one:
- closing_returned_fee_relief `hr_ret_pay`: "the payment its return line points at", appearing only in hr_timing's tier-1 sentence; read only by `hr_ap`, a hr_timing binding.
- goodwill_late_fee_credit `gw_fee_due`: "the due date the late fee is for", appearing only in gw_base's tier-2 sentence; read only by `gw_autopay_toward`, a gw_base binding.
Consequence: the KB places these bindings in the computation document while their only definition lives in one factor document. This is the render STOP class the coordinator names. No scored value moves.
Non-members: `rr_ret_pay` (read by the plain `rr_due` and by rr_timing); all other plain bindings are read by plain bindings or by two or more factors.

Observations: O-1, O-3, O-6, O-8, O-9, O-10.

## closing_checklist (revision_8)
Written after both revision-8 reveals; the revision_8 charter section above is pre-reveal and unchanged. **Not closed.**
- Files: revisions 1–8 present in `0.md` and `1.md`. Scope and tools unchanged.
- Trees: both PASS, acyclic.
- Factors: within bounds, all bear weight, every figure equal to the auditor's blind figure in both tasks.
- Round-7 REDs:
  - R7-1 closed via the coordinator's scoped overwrite: the scope is stated exactly and out-of-scope late due dates stay under the base clause verbatim, in rule and compute;
  - R7-2 closed: the make-good timing is a funds-timing signal.
- S1–S7: no regression. Sibling classes: (a) none, (b) none, (c) two members (R8-2).
- XF recipe: point 1 (record selection / plain-binding placement, sibling class (c)) has members `hr_ret_pay` and `gw_fee_due`; point 8 (decoy rows) has the member R8-1; the other points pass.
- Gate re-run = the coordinator's r8 snapshot (7 OK; traceability pre-publication).
- Open charter-wide REDs: R8-1, R8-2.

VERDICT revision_8: task0=RED SOURCE-POLICY task1=RED SOURCE-POLICY charter=R8-1,R8-2

## revision_9

## charter_global_frozen (revision_9)
- Frozen 2026-10-17 (after the 14:05 snapshot) before any revision-9 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 9: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 9` (2026-10-17T14:05:51): 7 gates OK; TRACEABILITY NOT OK (pre-publication, O-6).
- Hashes: `builder.extended.yaml` c5a8bc417079e19097e7de4fd23c29a2e5695ccf2910208d6a0c886536962102 (changed); `task_tools.py` f8707267…9346 and both views (d65215df…, 0bd1a280…) unchanged.
- Claims read by id. `mech.py` (extended) sweep clean on all 8 policies: quotes, baselines, prerequisite sources and fallbacks, replaced_by texts, no cross-factor read, ladders ≥ 3, every window sentence bounded (22/22).
- Render-stop classes swept:
  - (a) no compute_basis sentence serves two factors;
  - (b) no factor takes effect through another;
  - (c) no plain binding is read by one factor only, and no plain binding is unused. `hr_ret_pay` is now a hr_timing binding and `gw_fee_due` a gw_base binding.
- S1–S7 phrases present. No regression.

### R8-1 / R8-2 closure check
- **R8-2 closed** (both members moved into their factors, and the sweep finds no other member).
- **R8-1 closed for the bounced make-good payment:**
  - `ad_good_ret` excludes it (probe re-run: lag None → flat 3);
  - `rr_good_ret` excludes it from the made-good relief;
  - the late fee and the settlement treat a debit card payment with any return pointing at it as not counted / not paying the interest (`lf_dc_cb`, `cc_dc_cb` now count every return, not only CB).
- Not members:
  - `gw_autopay_toward` (gw_base tier 2) counts AutoPay debits presented toward the due date whether returned or not. That is its stated meaning ("an AutoPay debit … was posted toward the due date"), and it decides which fees the credit is figured on, not whether funds arrived.
  - `hl_toward` only distinguishes a partly paid installment, alongside the account's past-due figure, which already reflects reversals.
  - The late-fee scope count `lf_dc_count` counts posted card payments. The rule uses "credited" in that gross sense ("one debit card payment has been credited … which is not counted when a return points at it"), so rule and compute agree. Observation O-11: elsewhere "payments credited" means posted less returned (the seasoning counts), so the word carries two senses across policies; not raised, because each policy fixes its own sense in its own sentences.

### findings (r9)
**R9-1 — SOURCE-POLICY RED (two readings; decoy row; XF 8; remaining member of the R8-1 class).** Re-enrollment tier 1: "the borrower's own payment made it good within the late-fee grace period … (the latest payment posted toward that due date, which no return points at, is dated after the return and no more than the plan's late-fee grace days after the due date …)".
- Reading A, the clause restrictive: the latest *unreturned* payment toward the due date.
- Reading B, the compute: the latest payment toward the due date, which must itself be unreturned (`ad_good_id` = latest posted, then `ad_good_ret == 0`).
- Probe on task 1's world: the 10-05 / 10-08 / 10-09 rows replaced by a 104.72 payment on 09-25 (cleared) and a 20.00 payment on 10-05 toward 09-15, returned 10-08. Reading A: lag 10, buffer 11, the borrower's funds having arrived on 09-25. Reading B: lag None, flat 3.
- The made-good relief is not a member. Its wording is unambiguous ("the most recent payment posted toward the due date … is dated after the return date and has not itself been returned"), and a later bounced payment becomes the account's most recent return there.
- Only member.

Observations: O-1, O-3, O-6, O-8, O-9, O-10, O-11.

## closing_checklist (revision_9)
Written after both revision-9 reveals; the revision_9 charter section above is pre-reveal and unchanged. **Not closed.** Only task 0 passes all four relationships.
- Files: revisions 1–9 present in `0.md` and `1.md`. Scope and tools unchanged.
- Trees: both PASS, acyclic.
- Factors: within bounds, all bear weight, every figure equal to the auditor's blind figure in both tasks.
- R8-1 closed for the bounced make-good payment. R8-2 closed. S1–S7 and render-stop classes (a)–(c): clean.
- Remaining: R9-1 (XF 8 point; the last member of the R8-1 class).
- Gate re-run = the coordinator's r9 snapshot (7 OK; traceability pre-publication).
- Open charter-wide REDs: R9-1.

VERDICT revision_9: task0=PASS task1=RED SOURCE-POLICY charter=R9-1

## revision_10

## charter_global_frozen (revision_10)
- Frozen 2026-10-17 (after the 14:12 snapshot) before any revision-10 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 10: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 10` (2026-10-17T14:12:02): 7 gates OK; TRACEABILITY NOT OK (pre-publication, O-6).
- Hashes: `builder.extended.yaml` 49124040e7966a9699f9ad8b7d0a1d26b30700995c28d154eeb3a0a9050ac9d0 (changed, wording only); `task_tools.py` f8707267…9346 and both views (d65215df…, 0bd1a280…) unchanged.
- Claims read by id. `mech.py` (extended) sweep clean on all 8 policies:
  - quotes, baselines, prerequisites and fallbacks, replaced_by texts;
  - no cross-factor read; ladders ≥ 3; 22/22 window sentences bounded;
  - render-stop classes (a)/(b)/(c): no members;
  - S1–S7 phrases present.
- Every computed figure on both worlds is identical to r9, so the r10 changes are textual.

### R9-1 closure check (and its class)
- The re-enrollment make-good test now reads: "the payment looked at is the latest payment posted toward that due date: it makes the debit good only when no return points at it, it is dated after the return and it is dated no more than the plan's late-fee grace days after the due date …; when a return points at that latest payment, the debit has not been made good". It selects first and tests second, which is exactly `ad_good_id` (latest) then `ad_good_ret == 0`.
- Probe re-run (cleared 09-25 payment, later 10-05 payment returned): the rule now gives only "not made good", so flat 3, the same as compute. The single reading is a reasonable treatment, since the latest attempt toward the due date bounced.
- The other select/test sentences reworded in the same shape keep compute-equivalent meaning:
  - returned fee: "only for the account's most recent returned payment and only when that payment's return code is one of the plan's fee-bearing return codes";
  - late fee: "…less that payment …; when a return points at that payment …, the payment is not netted and the fee is figured on the monthly payment". This also fixes the maturity-date case: monthly payment, matching `lf_base`.
- A sweep for remaining "latest / most recent …, which / that …" selection clauses finds none.
- **R9-1 closed.** No new member.

### findings (r10)
None. Open charter REDs: none. Observations O-1, O-3, O-6, O-8, O-9, O-10, O-11 persist (not grounds for rework).

## closing_checklist (revision_10)
Written after both revision-10 reveals; the revision_10 charter section above is pre-reveal and unchanged. **All four relationships PASS for both tasks.**
- Audit files: `0.md` and `1.md` correspond one-to-one with tasks/0.json and tasks/1.json; revisions 1–10 are preserved in order, and every revision-10 comparison section carries PASS.
- Coverage and scope:
  - all 8 extended policies are covered;
  - task 0 {late fee, closing late-fee relief, closing returned-fee relief, settlement} and task 1 {returned fee, made-good relief, AutoPay re-enrollment, goodwill} are pairwise disjoint over each whole tree and jointly complete;
  - each task tool is claimed once with an independently generated, frozen uuid8 (fbf509e1, 8372931d, c21c573e, 90cd40e1, 1f748b6c, d8e21ef6, 43fbbd15, 5af065e7); the docstrings match every rule branch (S6).
- Trees:
  - task 0: 3 prerequisite problems, 4 value_input edges, user-owned root;
  - task 1: 3 prerequisite problems, 3 value_input edges plus 1 state_gate, user-owned leaf, holding on a charter-shaped seed;
  - no cycles; the union graph is acyclic. Every edge is unmet at frozen_time and bears weight; no waits; tools judge nothing.
- Factors:
  - every computation has a self-sufficient baseline and 4–6 factors with exactly one method (4/4/6/5/5/6/6/5);
  - each task has multi-source and cross-difficulty factors (hardship, loan, line, pos);
  - every ladder has 3 disjoint, reachable tiers stated in full in its rule;
  - every factor bears weight against an honest baseline on its task's world, and the all-baseline figure differs from gold everywhere (5.86 / 0.17 / 0.35 / 1177.86; 10.00 / 0.63 / 15 / 0.28);
  - all scored values and sensitivities equal the auditor's blind figures.
- Renderer scan S1–S7 and sibling render-stop classes (a)–(c): no member remains. XF recipe points 1–14: no member remains.
- Gate re-run on the final form: the coordinator's r10 snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK pre-publication only, O-6).
- Open REDs: none. Observations carried: O-1, O-3, O-6, O-8, O-9, O-10, O-11.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN

## revision_11

## charter_global_frozen (revision_11)
- Frozen 2026-10-17 (after the 18:19 snapshot) before any revision-11 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 11: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 11` (2026-10-17T18:19:18): 7 gates OK; TRACEABILITY NOT OK (pre-publication, O-6).
- Hashes: `builder.extended.yaml` 9873a89a342f4080ac35a6d8802e8bf00aac3f60447fbff5c432ac7f37cb3f02 (changed); `task_tools.py` f8707267…9346 and both views unchanged.
- Inputs: renderer scan `render_r2.md` (N1) and `rework_r11_claims.md`, read by id.
- `mech.py` (extended) sweep clean on all 8 policies: quotes, baselines, prerequisite sources (including the reworded goodwill AutoPay sentence), fallbacks, replaced_by texts, factor reads, ladders, 22/22 window sentences, render-stop classes (a)–(c).
- Every computed figure on both worlds is identical to r10.

### N1 closure check (whole class: every "latest / most recent" selection that can tie)
All 16 LATEST lookups in the charter were enumerated:
- **Tie stated in the sentence the binding quotes:**
  - cc_dc_id, hl_fee_id, hr_ret_id, rf_ret_id, rr_ret_id, rr_good_id, gw_fee_id, ad_code;
  - hr_fee_id and rr_fee_id (also unique per return, since a fee is charged once per returned payment);
  - **gw_ap_id** (new: "the latest payment made through the AutoPay channel; when two were posted on the same day, the one booked first counts as the latest");
  - **ad_ap_id** (new, same clause);
  - **ad_good_id** (new: "and when two were posted toward it on the same day the one booked first counts as the latest").
  The tie rule matches `LATEST`, which keeps the first booked row.
- **Cannot tie:**
  - `lf_dc_id` is used only inside the overwrite's scope of one card payment toward the late due date (two or more fall to the base clause);
  - `hr_req_date` and `ad_ap_ret_date` return a date, so equal-date rows give the same value;
  - by-id lookups are unique.
- N1's example (two same-day payments toward D, the card one booked first and charged back): the rule now gives "not made good → flat 3", the same as compute, with one reading.
- The goodwill prerequisite `policy_source` is still verbatim in the rule (sweep).
- **N1 closed with its whole class.**

### findings (r11)
None. Open charter REDs: none. Observations O-1, O-3, O-6, O-8–O-11 persist.

## closing_checklist (revision_11)
Written after both revision-11 reveals; the revision_11 charter section above is pre-reveal and unchanged. **All four relationships PASS for both tasks.**
- Audit files: `0.md` and `1.md` correspond one-to-one with the tasks; revisions 1–11 are preserved, and every revision-11 comparison section carries PASS.
- Scope and tools: unchanged since r10. The 8 policies are covered; the two tasks' scopes are disjoint over whole trees and jointly complete. The uuid8s are independent and frozen; the docstrings match every rule branch.
- Trees:
  - task 0: 3 prerequisite problems, 4 value_input edges, user-owned root;
  - task 1: 3 prerequisite problems, 3 value_input edges plus 1 state_gate, user-owned leaf;
  - acyclic. Every edge is unmet at frozen_time and bears weight, and every policy_source is verbatim in its blocked rule.
- Factors:
  - 4/4/6/5/5/6/6/5, one method each;
  - multi-source and cross-difficulty factors in each task;
  - every factor bears weight against an honest baseline;
  - the all-baseline figures differ from gold everywhere;
  - every figure equals the auditor's blind figure.
- Renderer scans: render_r1 S1–S7 and render_r2 N1 are closed with their classes (all 16 LATEST lookups tie-stated or untieable). The sibling render-stop classes (a)–(c) are empty. XF recipe points 1–14: no member remains.
- Gate re-run on the final form: the coordinator's r11 snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; TRACEABILITY NOT OK pre-publication only, O-6).
- Open REDs: none. Observations carried: O-1, O-3, O-6, O-8, O-9, O-10, O-11.

VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN

## revision_12

## charter_global_frozen (revision_12)
- Frozen 2026-10-17 (after the 19:32 snapshot) before any revision-12 GT was revealed; same auditor.
- Gate entry: the last line of `worklog.md` is exactly `REWORK round 12: gates 7/7 green`.
- Snapshot `/tmp/erl0067_coord/snapshot.sh credit_builder_accounts 12` (2026-10-17T19:32:35): **all eight gates OK**, TRACEABILITY included (docs are published).
- Seed-only round:
  - `builder.extended.yaml` sha256=9873a89a342f4080ac35a6d8802e8bf00aac3f60447fbff5c432ac7f37cb3f02 and `task_tools.py` sha256=f8707267e656aa979baa7577f81f4cad01bbc69e7eb51847feb2c1bf22dc9346 are byte-identical to r11 (prefixes 9873a89a342f4080 / f8707267e656aa97 as required), so every charter-global conclusion of revision_11 carries forward by these hashes;
  - views r12/task_0.json 4561314623d1…f93c and r12/task_1.json 184caacc5b45…6cea are changed in cross-product rows only.
- Claims read by id. The KB-audit item files (`audits/policy_kb/credit_builder_accounts/`) were not opened. Read for the seed check: the published `docs/hardship`, `docs/loan`, `docs/line` and `docs/pos` documents named below, plus `blueprint/products/*.yaml`.

### cross-product seed check (every changed row recomputed from the owning product's published rules)
**Hardship plans:**
- **Task 0 Reduced Payment Plan 25386650, installment 136.54.**
  - The scheduled installment 303.42 times the percentage: the program's 50 % (no documented-hardship percentage applies, because no documents are recorded on the request) less these points (rpp_rate_grade_points, rpp_payment_record_points, rpp_loan_tenure_points, rpp_autopay_points):
    - Grade C: 1 point;
    - 12 net scheduled installments in the 12 months before the 2026-08-25 decision (2025-09-10 … 2026-08-10; 2025-08-08 is 12 whole months back, so outside): 3 points;
    - funded 2025-02-10, request 2026-08-20, so 18 months: 1 point;
    - AutoPay not enrolled: 0 points.
  - That gives 45 % → 136.539 → **136.54**, within the 50 % cap and the 25.00 floor. The payment base is the scheduled installment (nothing past due, no additional principal).
- **Task 0 Temporary Rate Reduction Plan 74bfef96, rate 4.24, installment 139.43.**
  - The program's 4.99 (no documented rate; no documents recorded) less: Grade E 0.75; tenure (funded 2026-01-12, request 2026-08-10, 6 months) none; AutoPay not enrolled, none → **4.24** (above the 1.99 floor).
  - 17 due dates left (2026-09-12 → 2028-01-12) is in the 13–36 band, so the level installment applies: 2296.66 at 4.24 %/12 over 17 = **139.43**.
- **Task 1 Temporary Rate Reduction Plan 9dd6cffd, rate 4.74, installment 200.36.**
  - 4.99 less: Grade B none; tenure (2024-09-20 → 2026-07-30, 22 months) 0.25; AutoPay none → **4.74**.
  - 14 due dates left (2026-08-20 → 2027-09-20), so the level installment: 2723.69 at 4.74 % over 14 = **200.36**.

**Loan ledgers.**
- Every installment's interest equals daily simple interest at the loan's rate from the last cleared payment (balance × rate / 365 × days). The plan rate takes over from the plan's start date. Examples:
  - task 0 Grade E 2026-10-09: 29.99 % to 09-12, then 4.24 % = 8.76;
  - task 1 2026-09-18 at 4.74 % = 9.64;
  - task 1 2026-07-24, counted from 06-18 past the returned 07-20 payment, = 51.27.
- Principal follows the allocation (accrued interest, then fees, then principal). Ledger-derived balances equal each loan record (4515.06 / 2083.17 / 2368.86), as do the next due and interest-paid-through dates.

**Loan fees** (late_fee_amount_calculation, the share documents, returned_payment_fee_amount_calculation, returned_fee_first_return_share):
- **Task 0 OH loan late fee 13.65** (schedule A, 2026-05-26 for 05-10): 5 % × 303.42 = 15.171 (≥ 15 minimum). First-late share 0.9 (no late fee in 12 months; 11 net installments). No AutoPay, tenure, FlexLine pay-cycle or term-extension share → **13.65**; paid in full 05-29.
- **Task 1 CO loan late fee 9.76** (schedule B, 2025-07-06): 5 % × 216.88 = 10.844 × 0.9 (first-late; 8 net installments) = **9.76**.
- **Task 1 CO loan returned fee 8.50** (schedule B, 2026-07-22): 10.00 × 0.85 (first return; 12 posted − 1 returned = 11 net) = **8.50**. No AutoPay share (the payment is online_ach), no bank-event form (no FlexLine return on or before that date).

**FlexLine fees** (returned_fee_figuring, returned_fee_history_share; exact half cent to even):
- **Task 0, 0.75:** 35.00 R09 < 1000 → 2.5 % = 0.875 → 0.88; × 0.85 (the only return in 24 months); late-booking, shared-event and tenure shares 1.00 → 0.748 → **0.75**. The balance 473.37 follows.
- **Task 1, 0.95:** 45.00 R01 → 1.125 → 1.12; × 0.85 → **0.95**. The make-up payment of 45.95 covers return plus fee, so the line balance is unchanged.

**PracticePay fee** (returned_item_fee_level, returned_payment_fee_amount, balance band, FlexLine and personal-loan shares, one-penalty limit, charging timing):
- **Task 1, 7.60**, booked 2026-06-22 after the 06-10 due date's grace. No late fee was owed, because the 06-15 make-up of 100.00 paid within grace.
- Level 10.00 (one return in 6 months, no late fee in 12) × 0.8 (ledger balance 900.00 < 1000) × 0.95 (active FlexLine, no FlexLine late fee or return in 12 months before 06-22) × 1 (the loan late fee of 2025-07-06 is inside 12 months) = **7.60**. Within the monthly-payment limit; paid 06-25; plan balance 600.00 unchanged.

Every changed cross-product row is what its product's published rules produce. The SOURCE-FACTOR criterion "seeded cross-category rows are states the owning charter can produce" holds.

### findings (r12)
None. Open charter REDs: none. Observations O-1, O-3, O-8–O-11 persist; O-6 is resolved (traceability OK).

## closing_checklist (revision_12)
Written after both revision-12 reveals; the revision_12 charter section above is pre-reveal and unchanged. **All four relationships PASS for both tasks.**
- `builder.extended.yaml` and `task_tools.py` are byte-identical to r11, so the r11 charter-global conclusions carry forward:
  - scope, tools and uuid8s;
  - prerequisite graph and sentences;
  - override declarations;
  - factor ladders;
  - S1–S7, N1 and render-stop classes clean;
  - XF points 1–14 with no member.
- Seed: every changed cross-product row (hardship, loan, line, PracticePay) is what its product's published rules produce, recomputed row by row above.
- Prerequisites:
  - task 0's late fee, late-fee relief and returned-fee relief are unmet at the opening;
  - task 1's returned fee, made-good relief and AutoPay enrollment are unmet at the opening;
  - every edge bears weight.
- Factors: every factor bears weight against its baseline on the new worlds.
- Values:
  - task 0's settlement is 1155.24 (closing rate 4.24 from the rebuilt TRR plan);
  - all other gold values are unchanged;
  - every recomputed gold, sensitivity, skip figure and proof sentence matches the auditor's blind figures.
- Gate re-run on the final form: the coordinator's r12 snapshot. EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE and TRACEABILITY all OK.
- Open REDs: none. Observations carried: O-1, O-3, O-8, O-9, O-10, O-11.

VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN
