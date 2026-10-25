# Policy-task audit — account_credit_and_recovery / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-22T12:19Z, before any task GT was revealed; auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes: `account.extended.yaml` 4c58aaecbacb627284df50e69c75bd9db40cf86f048a2daa44e57f8fd9c7dc1e; `task_tools.py` 76fd4b5732836c602f94f8d0b73b65b04d5247102e3b7781ffb946c5ee4bb5fd (both re-hashed by the auditor and equal to the brief).
- Read: blueprint.yaml (difficulty entry), db_schema.json, share_tools.py (finder list), products/account.yaml (base) and, for cross-category realism/seed checks, products/domain.yaml, hosting.yaml, ssl.yaml; the extended charter; task_tools.py; the coordinator's masked views 0.view.json / 1.view.json (frozen_time, user_scenario, initial_state only); audits/render_source/XF_recipe.md; the DSL evaluator in skills/erl-task-instantiate/scripts/check_compute.py (to learn RND / within_months / LATEST / CFIELD semantics).
- Masked / not read: tasks/0.json, tasks/1.json (all GT fields), plan.md, worklog.md, every sibling difficulty, every other scenario. No recursive grep touched the tasks directory.
- Entry conditions (Step 0): gate snapshot /tmp/erl0076_coord/snap_account_credit_and_recovery_r1.txt shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked-view hashes match. check_traceability deferred to step 3 by the coordinator (not run here). Inputs complete.
- Base copy: every top-level key of products/account.yaml is byte-equal (parsed) in account.extended.yaml; only `extended_policies` is added.
- Auditor scratch: /tmp/audit_account_credit_and_recovery_0076/ (sim.py re-evaluates each policy's compute with the framework DSL on the masked initial_state plus the auditor's own sequential writes).

### policy_conflict_scan
Eight extended policies:

| id | subject | trigger | target tool (owner) | posts against |
|---|---|---|---|---|
| account_ext_deposit_return (P-DR) | account_credit_withdraw | on_request | return_deposit_credit_07195348 (user) | the most recent deposit |
| account_ext_provisioning_goodwill (P-PG) | account_goodwill_credit | state_due | grant_provisioning_goodwill_e1bd747b (agent) | plan's initial-term order number, hosting |
| account_ext_recovery_review_goodwill (P-RV) | account_goodwill_credit | state_due | grant_recovery_delay_goodwill_1cc515a4 (agent) | recovery request reference, none |
| account_ext_duplicate_renewal_goodwill (P-DU) | account_goodwill_credit | state_due | grant_duplicate_charge_goodwill_d451e88f (agent) | duplicate charge order number, domain |
| account_ext_retry_topup (P-TU) | account_credit_deposit | on_request | make_topup_deposit_c7a3772f (user) | new deposit |
| account_ext_certificate_delay_goodwill (P-CD) | account_goodwill_credit | state_due | grant_certificate_delay_goodwill_7e1fd2ff (agent) | subscription purchase order number, ssl |
| account_ext_reset_delay_goodwill (P-RD) | account_goodwill_credit | state_due | grant_reset_delay_goodwill_979fb2c3 (agent) | recovery request reference, none |
| account_ext_refund_posting_goodwill (P-RP) | account_goodwill_credit | state_due | grant_refund_posting_goodwill_cac8bb9c (agent) | refunded domain charge order number, domain |

- Overlapping subject: six state_due goodwill schedules share `account_goodwill_credit`, the base dedup `one_grant_per_reference` (credit_origin goodwill, keyed on source_charge_ref) and the yearly cap. Two pairs post against the SAME reference kind: P-RV and P-RD both against "the recovery request's reference number"; P-DU and P-RP both against the refunded domain charge's order number (P-DU: "the order number of the refunded duplicate charge"; P-RP: "the refunded charge's order number"). A world in which one approved recovery request is both decided more than three calendar days after submission and reset more than one day after its waiting period, or in which a refunded same-day duplicate auto-renew charge was refunded to credit and posted more than three days late, makes both schedules due "without the customer having to ask" on one reference while base account_goodwill allows "One grant may be made per affected holding or charge reference" — no rule says which schedule takes the reference (finding C2).
- Yearly cap: all six schedules restate the same replaced cap sentence; total of grants is order-independent as long as the sum stays under the room; when the room binds, the individual scored grants depend on the order (no rule fixes it). Checked per task (neither world binds).
- Eligibility / time anchors / terminal states: every policy requires account status active (base goodwill_active, deposit_active, withdraw_active restated). P-DR's root and P-TU's root read the goodwill entries the schedules leave. No other overlap.
- Cross-category read boundaries: reads of hosting, domain, ssl are declared in each `cross_category`; no write lands outside the account category (trigger rule XF D20: every tool writes account_credit_ledger + account_holdings only; base triggers of withdraw/deposit/goodwill are account:account_balance_sync only).
- Scope exclusivity / completeness: task 0 tree {P-DR, P-PG, P-RV, P-DU}; task 1 tree {P-TU, P-CD, P-RD, P-RP}; disjoint, jointly all eight (from the prerequisite graph; the masked charter_scope is compared after reveal).

### rule_compute_equivalence
Mechanical sweep (scratch mech.py): every `compute_basis` quotation is verbatim in its rule; every baseline.rule sentence is in its rule; every prerequisite `policy_source` is verbatim in its own rule; no factor binding reads another factor's binding; no binding shared by two factors; no factor id is a substring of a tool name.
Sentence-by-sentence sweep (all eight policies), non-mechanical results:
- P-DR: window (`DAYS(dep_date, NOW) > withdrawal_window_days -> 0`) = "on or before its entry date plus withdrawal_window_days ... last day included"; "dated after the same calendar date one year before today" = `within_months=12` (DSL: `MONTHS(d,NOW) < 12`); lockouts "after the same calendar date one month before today" = `within_months=1`; combination sentence (holdbacks subtracted together, floor 0, x release share, one rounding) = dr_after_holdbacks/result. Scope test "no other deposit entry shares its entry date" is stated and not priced (coarse exact scope, acceptable). Equivalent, with the decoy/edge gaps listed in C6.
- P-PG: daily/monthly values, started weeks (`-(-d//7)`), class/term/remedy multipliers, uplifts, order "multipliers, then uplifts, then limits, then rounding" = pg_figure/result. Equivalent (C6 c).
- P-RV: "most recently decided recovery request, approved or rejected" vs `LATEST(..., date_field='decided_at')` with no outcome filter — a withdrawn request (schema outcome `withdrawn`, decided_at set because withdrawal follows an approval: base "A request withdrawn by the holder before the hold ends") is taken by compute and excluded by the rule (C6 a).
- P-DU: tiers, uplifts, "uplifts added to the compensation basis, then limits, then rounding" = du_figure/result. Refund lines carry payment_method none (schema), so `du_card_renewals` counts charges only — rule-equal. Ties on "latest refund date" unstated (C6 d).
- P-TU: estimate tiers, competing holdback, buffers, "all added together", balance = ledger sum, floor at min_deposit_amount, zero when shortfall <= 0 = compute. "no more than competing_window_days calendar days after today" is computed with `DAYS >= 0` for the holdback and without that guard for the expiry buffer (one phrase, two computations; C6 e). "refused in full" above max_deposit_per_transaction / max_credit_balance has no branch (C6 g).
- P-CD: reads `cert_issued_date` ("Issue date of the current certificate"), `subscription_years` ("Years bought in the most recent purchase or renewal") and the start/end dates, while the rule speaks of the most recent initial issuance and the new-subscription charge (C6 b). Literal 7 for "each started week" is a week, not a tier boundary — equal.
- P-RD: "the date the reset took effect is the account's last security change date" — rule and compute agree, but the sentence asserts a fact a later holder change falsifies (C6 f).
- P-RP: equal; ties on the most recent refund line unstated (C6 d).
- Rounding: every rule says half up once at the end; compute rounds once at `result` with the framework `RND` (Python round). No value in either world falls on a half cent (checked per task), so no consequence; tool bodies round half up with Decimal (XF B11 satisfied in the tools).

### action_binding_and_uuids
- (target_tool, computes) pairs are all distinct (8 tools, 8 policies, `amount` each).
- Docstrings: no ordering word other than "at once", no other tool named, no concrete example value (formats only: "HL- followed by 8 digits"), no composite argument (XF E23/E24 clean).
- uuid8s 07195348, e1bd747b, 1cc515a4, d451e88f, c7a3772f, 7e1fd2ff, 979fb2c3, cac8bb9c: distinct, no shared prefix/suffix, no sequence — independently generated.
- Tool bodies: every write calls ctx.create/ctx.update itself (XF E26); amounts positive and half-up enforced; no tool reads a prerequisite or refuses on one (no tool-layer prerequisite judgement). Contract gaps (XF B11 "tool bodies enforce the docstring's format"): the six goodwill tools accept any `source_charge_ref` (docstring: "HL- followed by 8 digits ... the empty string is not used", or "the reference number of the recovery request, character for character") and `return_deposit_credit_07195348` accepts any `original_credit_entry_id` without checking it is a deposit of this account (falls back to funding_method "none") — finding C10.
- owner=user tools: a deposit charged to the holder's own card/PayPal and a withdrawal back to the holder's own funding method are genuinely the holder's own acts. Observation: blueprint.yaml's difficulty summary says "The agent books deposits, credit spending, withdrawals ..."; the charter itself assigns no owner, so this is a wording mismatch, not a rule conflict.

### prerequisite_graph
- `prerequisite` filled on all eight (`[]` on the six schedules). Edges: P-DR <- P-PG, P-RV, P-DU; P-TU <- P-CD, P-RD, P-RP. All `kind: value_input`, `gate` = dr_remaining_deposited / tu_shortfall (bindings that exist), `form: state`, no fallback_reason (correct for state form), `resolved_by` = the depended-on target tool. Acyclic (two stars). No base policy targeted, no self-loop. No authoring-viewpoint phrasing.
- `effect` texts: P-DR edges claim the goodwill raises the remaining deposited credit "while purchases exceed non-cash credit" — true on task 0's world (see 0.md) and the mechanism of finding C1.
- `condition` vs sentence: P-RV edge condition speaks of "decision moment ... more than three calendar days after its submission moment" while the rule counts "calendar days from the request's submission date to its decision date" (observation: date vs moment wording; no world in this difficulty sits on the boundary).

### prerequisite_sentences
Four-point test, every edge:

| edge | sentence (own rule) | connective | waited-on state | candidate writes of this difficulty |
|---|---|---|---|---|
| E1 P-DR<-P-PG | "The amount returned from a deposit is fixed only after the credit ledger carries a goodwill entry for the customer's active hosting plan in its first term whenever that plan was activated two or more calendar days after its order date." | only after | ledger goodwill entry for the plan | grant_provisioning_goodwill only |
| E2 P-DR<-P-RV | "... is not fixed until the credit ledger carries a goodwill entry for the account's most recently decided recovery request whenever that request was decided more than three calendar days after it was submitted." | not until | goodwill entry on the request reference | grant_recovery_delay_goodwill AND grant_reset_delay_goodwill (both post against the recovery request reference) |
| E3 P-DR<-P-DU | "Before the amount returned from a deposit is worked out, the credit ledger must carry a goodwill entry for the most recently refunded domain auto-renew charge whenever that charge was a same-day duplicate ..." | before | goodwill entry on the refunded charge's order number | grant_duplicate_charge_goodwill AND grant_refund_posting_goodwill (both post against the refunded charge's order number) |
| E4 P-TU<-P-CD | "The top-up deposit is worked out only after the credit ledger carries a goodwill entry for the subscription of the customer's most recent initial certificate issuance whenever that certificate was issued more than five calendar days after the subscription's order date." | only after | goodwill entry for the subscription | grant_certificate_delay_goodwill only |
| E5 P-TU<-P-RD | "The top-up deposit is not fixed until the credit ledger carries a goodwill entry for the account's most recent approved recovery request whenever its reset took effect more than one day after its waiting period ended." | not until | goodwill entry on the request reference | grant_reset_delay_goodwill AND grant_recovery_delay_goodwill |
| E6 P-TU<-P-RP | "Before the top-up deposit is worked out, the credit ledger must carry a goodwill entry for the most recent domain refund returned to account credit whenever that refund's credit entry was posted more than three calendar days after the refund was issued." | before | goodwill entry on the refunded charge's order number | grant_refund_posting_goodwill AND grant_duplicate_charge_goodwill |

- All six: explicit ordering connective; record-visible state named in table words; no tool name, policy id, snake_case token or row id; the depended-on rules do not restate the sentences; no second wording.
- E2, E3, E5, E6: two writes of this difficulty can bring the waited-on state about (finding C2).
- E4: the sentence (and its `condition`) omit the depended-on schedule's scope test "whenever that subscription is active": for a subscription later revoked/cancelled/expired the sentence still demands a goodwill entry that P-CD's rule never grants (cd_order None -> figure 0, and the tool refuses 0) — broader than the depended-on rule (finding C5).
- Every edge waits on a goodwill entry whose amount is `MN(figure, goodwill_max_per_case, yearly room)`; when the yearly room is 0 (goodwill already at goodwill_max_per_365d, a producible world) the grant is 0.00, the schema says goodwill amounts are positive and every goodwill tool returns "Error" on <= 0, so the waited-on state can never hold and the root can never be computed (XF D22 zero-amount edge; finding C4).
- Derivations (reader path): E1 -> P-PG's rule names the plan "in its first term ... activation date late_days_min or more calendar days after its order date" and the grant "posted against the order number of the plan's initial-term charge" -> grant_provisioning_goodwill. E3 -> P-DU's rule: same-day twin, posted against the duplicate's order number. E4 -> P-CD. E6 -> P-RP. E2/E5 resolve to a single policy only through the depended-on rules' own scope tests in a given world, not through the sentence.

### override_declarations
Sentence-by-sentence against base_policy_refs:
- account_goodwill S1 (active only): restated by all six schedules — followed.
- S2 ("only for a Harborline service failure that is shown in the customer's records ... never for an outage already credited under a product's uptime rule, and never for the customer's own missed renewal or deadline"): not overwritten. Departures: P-RV grants for any decision more than allowed_wait_days (3) calendar days after submission, while base account_recovery publishes the review time as recovery_review_business_days business days (Personal/Business 2): a request submitted on a Friday and decided on the Tuesday is 4 calendar days, 2 business days — inside the published review time, so not a service failure — yet P-RV grants. P-CD grants whenever issuance is more than 5 calendar days after the order date, while ssl_validation targets issuance "within issuance_target_business_days business days once the documents are complete": an order whose organisation documents the customer supplies on day 10 and which issues on day 11 is late only by the customer's own delay, yet P-CD grants. Undeclared departures (finding C3).
- S3 (one grant per reference): not overwritten; collided by the sibling pairs (C2).
- S4 (caps, account_msr_goodwill_365d): overwritten by all six with the same replaced_by; the tail excludes all six schedules by name (XF C16 satisfied); the retained content for out-of-schedule grants is stated. The replacement window ("after the same calendar date one year before today") differs from "trailing 365 calendar days" only across a 29 February (observation: retires little).
- S5 ("Goodwill credit is spendable on any Harborline product but is never withdrawable"): not overwritten; P-DR departs (C1).
- account_withdrawals: active / once per deposit / window restated; amount sentence overwritten for the most recent deposit (declared, replaced_by restates the min-amount rule and the out-of-scope measure); "Credit that came from refunds, service credits or goodwill is never withdrawable (refund_credit_withdrawable, goodwill_credit_withdrawable)" not overwritten and departed from (C1). Bank-transfer return and processing days inherited.
- account_recovery (P-DR, P-RV, P-RD): "During recovery_hold the holder cannot ... withdraw credit" inherited (P-DR requires active). Review-time sentence: see S2. Hold counting: P-RD counts "recovery_hold_hours ... taken as days of 24 hours" and calendar days from the decision date — consistent with base for whole-day holds (72/96 h).
- account_chargeback_and_lock (P-DR): "While locked, no ... withdrawal" inherited.
- account_credit_spending (P-DR, P-TU): whole-charge-only and credit-first-for-auto-renew followed (the basis of P-TU and of the holdbacks); "Spending consumes refund, service and goodwill credit before deposited credit, and deposited credit oldest deposit first" — P-DR's netting of all purchases ever made against all non-cash credit ever posted treats a goodwill entry posted today as having been consumed by purchases made before it existed (C1).
- account_deposits (P-TU): every sentence restated; P-TU only sets the amount for its stated purpose (no conflict). account_refund_credit (P-DU, P-RP): followed.

### factor_ladders
40 declared factors. Per policy: P-DR 4 (3 parameter, 1 method); P-PG 6 (5/1); P-RV 5 (4/1); P-DU 5 (4/1); P-TU 4 (2/2); P-CD 6 (5/1); P-RD 5 (4/1); P-RP 5 (4/1). Every ladder has three tiers including the fall-through, stated in the rule and implemented in compute; fall-through = baseline for every factor; `decides` is never `result`; binding sets disjoint.
Method all-pairs shape table (XF A6; any aggregate of one field = one input, constant multipliers ignored):

| factor | T1 | T2 | T3 (fall-through) | failing pair |
|---|---|---|---|---|
| P-DR renewal_hold | LATEST hosting_charges.amount (renewal line, renewed plan) | XSUM hosting_charges.amount (initial_term, first-term plan) | 0 | T1/T2: same field, filter only |
| P-PG delay_basis | monthly x ceil(d/7) | monthly | daily x d | none |
| P-RV review_basis | 8 x ceil(d/7) | 6 | 2 x (d-3) | none |
| P-DU duplicate_basis | amt + 3 x ceil(lag/7) | amt | 0.25 x amt | T2/T3: constant multiplier only |
| P-TU retry_estimate | XLATEST domain_charges.amount (transfer_in) | registration amount / years | XLATEST domain_charges.amount (renewal) or 0 | T1/T3: same field, filter only |
| P-TU competing_holdback | LATEST hosting_charges.amount (renewal line) | XSUM hosting_charges.amount (initial_term) | 0 | T1/T2 |
| P-CD issuance_basis | monthly x ceil(d/7) | monthly | daily x d | none |
| P-RD reset_basis | 12 x ceil(d/7) | 7 | 1.5 x d | none |
| P-RP posting_basis | 3 x ceil(lag/7) | 4 | 0.2 x amt | none |

-> renewal_hold, duplicate_basis, retry_estimate, competing_holdback fail; P-DR, P-DU and P-TU are left with no method factor that passes (finding C7).
Multi-source factors (every non-fall-through tier a conjunction over distinct records): P-DR chargeback_reserve (charge-back entries + the withdrawn deposit's method); P-TU retry_estimate (domain charges + domain holding acquisition type) and card_failure_buffer (domain events + hosting events, but see C9); P-CD site_coverage (hosting plan + domain holding); P-PG site_outage (hosting primary domain + domain holding). Cross-difficulty factors exist in both trees (hosting, domain, ssl).
Realism (XF D18 / "unreal ladder"), all members in one pass (finding C8):
- R1 P-DR release_share: 0.6 / 0.8 of a cash withdrawal released after a recovery reset; with "each deposit may be withdrawn against only once" the withheld share can never be withdrawn from that deposit. Base already handles recovery risk by forbidding withdrawals during recovery_hold; no registrar publishes a percentage haircut on returning a customer's own deposit.
- R2 P-DR signin_reserve: a fixed 10/30 USD deduction from a cash withdrawal for temporary sign-in lockouts, which base account_security_rules describes as a lockout that "does not change the account status and ends by itself" — not a treatment a host publishes, and, with once-per-deposit, permanent.
- R3 P-DR renewal_hold and P-TU competing_holdback: hold the most recent renewal line (or the introductory initial-term line) instead of what the renewal will bill — hosting_renewal publishes the renewal as the regular rate less the current tier's hosting_discount_pct; a pre-tier-change renewal line or an introductory line is not what credit-first auto-renew will draw.
- R4 P-PG free_domain: an uplift for having the plan's free-domain registration (even under another name) — unrelated to the harm of late provisioning.
- R5 P-DU card_fallback and R6 P-DU declined_renewals: card-billed auto-renews and declined auto-renew attempts of any domain in two months raise the goodwill for a same-day duplicate of another charge — no registrar weighs these for duplicate-charge goodwill.
- R7 P-RP renewals_declined and R8 P-RP refund_kind: declined auto-renews and the refunded charge's type raise goodwill for a late refund posting — unrelated to the posting delay.
- R9 P-CD validation_failures: more goodwill for failed domain control validation checks — failures off Harborline DNS are the customer's own (base: never for "the customer's own missed ... deadline"), and on Harborline DNS ssl_validation says validation "completes automatically without customer action", so the tier rewards either the customer's own failure or a state the ssl charter does not produce.
- R10 P-TU card_failure_buffer and R11 P-TU expiry_buffer: the credit a retry needs is the renewal price (domain_renewal_pricing: renewal_price per year plus the ICANN fee, "no late surcharge applies during the grace period"); neither card declines nor the nearness of the expiry date changes it.
- R12 P-TU retry_estimate: estimates the retry from a historical transfer-in or registration line and, as its fall-through/baseline, "zero where the domain has none" — a registrar knows the renewal price it publishes; a zero estimate for a renewal that is being retried is a straw-man default.
- C9 (scope-restating condition): P-TU's scope is a declined domain auto-renew whose domain "is still active"; domain_auto_renew attempts run at most 35 days before expiry and an active domain has not expired, so "declined auto-renew attempts recorded after the same calendar date two months before today ... on the customer's domains" holds for every customer who reaches this write: the "only one of the two" tier is in practice "no hosting decline", the "both" tier "a hosting decline", and the fall-through is unreachable.
Observations (not RED): P-PG plan_class multiplies a figure already proportional to the plan's price; severity ordering of email-change vs two-factor removal is inverted between P-RV (email 1.25, 2FA 1.0) and P-RD (2FA 1.2, email 1.0); P-DU's middle tier pays the full amount of a duplicate that has already been refunded.

### findings
- **C1 SOURCE-POLICY RED — goodwill credit is cashed out by the root withdrawal formula.** Symptom: P-DR's three edges are value_input on dr_remaining_deposited and their `effect` texts say each posted goodwill raises "the deposit's withdrawable credit". Root cause: the rule's withdrawable credit nets ALL purchases ever made against ALL refund/service/goodwill credit ever posted, so a goodwill entry posted today is treated as already consumed by older purchases and passes 1:1 into the cash returned to the card. Evidence: P-DR rule "the unspent non-cash credit is the sum of all refund, service credit and goodwill entries less the sum of all purchase entries ... never below zero; the remaining deposited credit is the credit balance less the unspent non-cash credit" vs base account_goodwill "Goodwill credit is spendable on any Harborline product but is never withdrawable", base account_withdrawals "Credit that came from refunds, service credits or goodwill is never withdrawable", base account_credit_spending "Spending consumes refund, service and goodwill credit before deposited credit", base account_closure "refund, service and goodwill credit is forfeited", every goodwill tool docstring "never withdrawable", and blueprint.yaml "Requests no account rule decides, such as cashing out goodwill ... require a POLICY_NOT_COVERED handoff". Neither base sentence is in any overwrite. Consequence demonstrated in 0.md (two different returned amounts on one world). Bears on task 0.
- **C2 SOURCE-POLICY RED — sibling schedules share one dedup reference; four state-form edges have two candidate writes.** P-RV and P-RD both post "against the recovery request's reference number"; P-DU ("the order number of the refunded duplicate charge") and P-RP ("the refunded charge's order number") both post against the refunded domain charge's order number; base "One grant may be made per affected holding or charge reference" is in force and no rule says which schedule takes the reference when both are due. E2/E5 can be satisfied by grant_recovery_delay_goodwill or grant_reset_delay_goodwill, E3/E6 by grant_duplicate_charge_goodwill or grant_refund_posting_goodwill. Producible world: an approved request decided 4+ calendar days after submission and reset 2+ days after its hold ended (both schedules due, one grant allowed, two different amounts). Bears on tasks 0 and 1 (no consequence in either seeded world — see task files).
- **C3 SOURCE-POLICY RED — undeclared departures from base "only for a Harborline service failure".** P-RV (calendar-day trigger vs the business-day review time) and P-CD (calendar days from order vs issuance target counted from complete documents) grant where base forbids; demonstrated above on producible worlds; not declared in any overwrite. No consequence in task 0 or task 1 worlds (see task files).
- **C4 SOURCE-POLICY RED (XF D22) — every prerequisite waits on a goodwill entry that can be 0.00.** When goodwill_365d has reached goodwill_max_per_365d, each schedule's grant is 0, the tools refuse amounts <= 0 and the schema declares goodwill positive, so E1–E6 can never hold and neither root can be computed; no record test carves the case out. No consequence in either seeded world (rooms 100 and 80, unused).
- **C5 SOURCE-POLICY RED — E4 broader than the depended-on rule.** E4's sentence and condition omit "whenever that subscription is active"; for an inactive subscription with a late initial issuance the root waits forever. No consequence in task 1 (subscription active).
- **C6 SOURCE-POLICY RED (XF B9/B10/B13 class) — decoy, tie and edge inputs without a rule tier.** Members: (a) P-RV takes a withdrawn request as "most recently decided" (rule: approved or rejected); (b) P-CD reads the current certificate's issue date and the latest term's years/end date, which move on reissue/renewal, for a rule about the initial issuance and the new-subscription charge; (c) first-match CFIELD over several qualifying hosting plans with no rule for which plan (P-DR renewal_hold, P-TU competing_holdback, P-PG plan; hosting_agg_multi_holding allows any number of plans); (d) same-day ties unstated for P-DU's "latest refund date" and P-RP's "most recent domain refund line"; (e) "no more than N calendar days after today" computed with a >= 0 guard for P-TU's holdback and without it for the expiry buffer, and an active plan whose term end has passed (hosting_renewal: after the last declined retry "the plan follows hosting_suspension after its term ends") has no stated tier; (f) P-RD's "the date the reset took effect is the account's last security change date" is falsified by any later holder change (account_security_rules obliges re-enrolment after a two-factor removal on two_factor_required tiers); (g) P-TU prices a top-up above max_deposit_per_transaction / max_credit_balance that its own rule says is "refused in full". No member changes a scored value in either seeded world (checked in the task files).
- **C7 SOURCE-FACTOR RED (XF A6) — four method factors fail the all-pairs shape test** (table above); P-DR, P-DU and P-TU have no method factor that passes. Bears on task 0 (renewal_hold, duplicate_basis) and task 1 (retry_estimate, competing_holdback).
- **C8 SOURCE-FACTOR RED (XF D18) — unreal tiers R1–R12** (list above). Bears on task 0 (R1, R2, R3, R4, R5, R6) and task 1 (R3, R7, R8, R9, R10, R11, R12).
- **C9 SOURCE-FACTOR RED — P-TU card_failure_buffer restates the policy's scope** (domain-decline part true for every customer reaching the write; fall-through unreachable). Bears on task 1.
- **C10 SOURCE-POLICY RED (XF B11 tool-body contracts)** — goodwill tools do not enforce the declared source_charge_ref format/non-empty rule and return_deposit_credit does not check the deposit reference; a malformed reference returns a success line and leaves a ledger state that satisfies no prerequisite sentence. Bears on both tasks (no scored-value consequence on a correct path).

## closing_checklist
Written after both task files carry source_derivation_frozen and source_gt_comparison (reveal 2026-10-22T12:22:57Z). Freeze record correction: the "Frozen 12:19Z" stamp above was an estimate; this file's charter-global section was on disk at 12:20:57Z (mtime), before the reveal, and has not been edited since except for this appended section.
- Per-task files 0.md, 1.md correspond one-to-one with tasks/0.json, tasks/1.json; this is revision_1 (no older revision).
- Coverage and scope: GT charter_scope task 0 = {P-DR, P-PG, P-RV, P-DU} + their four tools; task 1 = {P-TU, P-CD, P-RD, P-RP} + their four tools — pairwise disjoint, jointly all eight policies and tools; matches the scope derived pre-reveal. uuid8s independent.
- Trees: each 3 prerequisites, 3 value_input edges, owner=user root, acyclic; difficulty graph acyclic. Edges bear weight on both worlds; in task 0 only under the reading C1 contests.
- Factors: every computation declares 4–6 factors with baselines that give definite numbers different from gold, and every factor moves its scored value (GT factor_sensitivity equal to the auditor's figures in all 8 computations); but C7 (four method factors fail the shape test; P-DR, P-DU, P-TU without a passing method), C8/C9 (unreal tiers), T0-F2 / T1-F2 (no near-miss in P-RV, P-CD, P-RP computations) and T1-F1 (tier on unproducible ssl rows) fail.
- Gates: not re-run by the auditor (coordinator snapshot r1 is the record); the difficulty does NOT pass the source-layer audit.
- Charter-level RED ids: C1, C2, C3, C4, C5, C6, C7, C8, C9, C10 (see findings above). Task-level: task 0 T0-F1..F4; task 1 T1-F1..F6.

VERDICT revision_1: task0=RED task1=RED charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10

## revision_2

## charter_global_frozen
- Written before any revision_2 GT was opened (tasks/*.json not read in this round until the reveal recorded in the task files). Auditor: same independent auditor.
- Entry: worklog tail `REWORK round 2: gates 7/7 green` confirmed; snapshot run by the auditor (execute-only) -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r2.txt: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views 0.view 6c029d29...0c92e70, 1.view c185835c...eb453092; account.extended.yaml 862f9d7f...7d615b (was 4c58aaec...), task_tools.py 7be694eb...7d615b (was 76fd4b57...). Both shared inputs changed -> every charter-global section re-derived in full; both tasks redesigned -> both derivations redone from the rebuilt views.
- Reworker claims read by item id only (worklog section "REWORK round 2 claims"); no scored value in them. check_traceability not run. Base copy still parsed-equal to products/account.yaml.
- Scratch: /tmp/audit_account_credit_and_recovery_0076/r2/, scripts/r2t0.py, r2t1.py, mech.py.

### policy_conflict_scan
| id | subject / trigger | tool (owner) | posts against |
|---|---|---|---|
| P-PF account_ext_renewal_prefund | deposit / on_request | make_prefund_deposit_8453f2b2 (user) | new deposit |
| P-PG provisioning | goodwill / state_due | grant_provisioning_goodwill_e1bd747b | initial-term order number |
| P-RV review | goodwill / state_due | grant_recovery_delay_goodwill_1cc515a4 | recovery request reference (approved only) |
| P-DU duplicate | goodwill / state_due | grant_duplicate_charge_goodwill_d451e88f | duplicate's order number |
| P-TU retry_topup | deposit / on_request | make_topup_deposit_c7a3772f (user) | new deposit |
| P-CD certificate | goodwill / state_due | grant_certificate_delay_goodwill_7e1fd2ff | new-subscription order number |
| P-RD reset | goodwill / state_due | grant_reset_delay_goodwill_979fb2c3 | security-change notice reference |
| P-RP refund posting | goodwill / state_due | grant_refund_posting_goodwill_cac8bb9c | refund line reference |
- The six schedules now post against six distinct reference kinds; base one-grant-per-reference no longer collides (C2 closed).
- P-PF and P-TU share subject account_credit_deposit; each scopes itself by purpose (plan + tied products due in 14 days vs. the next retry of a declined domain auto-renew) and leaves "any other purpose" to the base rule. A customer in both scopes is routed by the purpose stated (observation; not live in either world: P-PF is out of scope in task 1 because the plan's first attempt has passed, P-TU out of scope in task 0 because no decline exists).
- Writes stay in the account category (deposit/goodwill -> account:account_balance_sync only). Scopes: task 0 {P-PF, P-PG, P-RV, P-DU}, task 1 {P-TU, P-CD, P-RD, P-RP} from the prerequisite graph; disjoint, complete.

### rule_compute_equivalence
- Mechanical sweep (mech.py on the new file): every compute_basis quote verbatim in its rule; baseline sentences in the rule; prerequisite sources in their rules; no factor binding names another factor's binding; no binding shared by two factors; no factor id inside a tool name.
- Non-mechanical: the discount factors evade the name check by duplicating another factor's decides-expression: `pf_ssl_base` is the same expression as `pf_cert_charge` (decides of certificate_charge), `tu_host_base` = `tu_host_charge` (hosting_charge), `tu_mail_base` = `tu_mail_charge` (email_charge); the rule sentences say so ("takes its ssl_discount_pct off the certificate charge", "off the counted hosting charge", "off the counted email charge") — finding N2.
- Windows "no more than N calendar days after today" are 0..N everywhere (C6 e closed); ties stated and computed out of scope for P-DU/P-RP (C6 d closed); P-RV reads approved requests only (C6 a closed); P-CD reads the initial-issuance event and the new-subscription charge's years and period (C6 b closed); plan/certificate/email selections are scoped by exact single-order counts or a most-recent initial-term line unique on its date (C6 c closed); top-ups/prefunds above the limits are refused (C6 g closed).
- Residual C6 f: P-RD "for the account's only security-change notice dated after the same calendar date two months before today, whenever that notice applied the account's most recent approved recovery request" — notices carry no link to a request (account_events schema), so whether "that notice applied the request" is not record-visible; compute takes any single notice as the reset. A holder's own sign-in email change within two months after an approval decided months earlier (account_security_rules allows it while active) yields one notice and a large "late reset" goodwill the rule's own condition denies.
- P-TU first sentence "the top-up covers in full the retry and every other auto-renew charge attempted from today up to the day before the retry" vs the counted charges (only the single plan of a one-plan customer and the single email subscription of a one-subscription customer): another domain, a certificate, a second plan or email subscription auto-renewing before the retry is covered by the first sentence and excluded by the second (finding N3 b).
- Copies of other charters' pricing (XF A4): P-PF/P-TU restate hosting_renewal as "the tier's regular rate for its current term length", ignoring hosting_renewal's "unless a scheduled term change applies, and a scheduled downgrade's target tier sets the rates"; P-TU restates email renewals as seats x price, ignoring email_renewal_and_instalments "apply any scheduled seat count and scheduled product at the renewal" and the annual-billed-monthly instalment (its fall-through counts nothing for an instalment that credit-first would pay) (finding N3 a).
- Rounding: each discount is "list less the reduced price rounded half up" = `x - RND(x*(100-pct)/100, 2)`; no half-cent in either world.

### action_binding_and_uuids
- 8 distinct (target_tool, computes); new tool make_prefund_deposit_8453f2b2 has a fresh uuid8; the deposit-withdrawal tool is gone.
- Tool bodies now refuse a malformed order number (`HL-` + 8 digits) or an empty/space-padded reference and a non-deposit funding method (C10 closed). No tool judges a prerequisite; docstrings carry formats only, no ordering words, no examples.

### prerequisite_graph
- P-PF <- P-PG, P-RV, P-DU; P-TU <- P-CD, P-RD, P-RP; all value_input on pf_balance / tu_balance (bindings exist), form state, resolved_by = target tools; acyclic; no viewpoint phrasing.
- Every sentence and condition now adds "the account's goodwill entries dated after the same calendar date one year before today total less than the tier's yearly goodwill limit"; with entries in whole cents the room is then >= 0.01 and every schedule's figure is positive inside its scope, so the waited-on entry can always be posted (C4 closed). E4 now names the active subscription (C5 closed).

### prerequisite_sentences
- Four-point test passes on all six (ordering connective; record-visible ledger state; no tool/id/snake_case; strength = condition). Each waited-on reference kind is posted by exactly one schedule (provisioning: initial-term order number; review: recovery request; duplicate: duplicate order number; certificate: new-subscription order number; reset: security-change notice; refund posting: refund line) — single resolving write per edge.
- E1 omits P-PG's "where no other initial-term charge shares that charge date", but P-PF's own scope (exactly one initial-term charge) makes the omission empty — no gap.

### override_declarations
- account_goodwill S2 ("only for a Harborline service failure"): P-RV now grants only past 7 calendar days, beyond any 2-business-day span (worst cases checked: Friday before a Monday holiday, 2026-12-24 and 2026-12-30 spans = 5 days) — closed. P-CD: "Because the published issuance targets are at most five business days from complete documents and no such span, weekends and US federal holidays included, reaches allowed_issue_days calendar days" — false for the EV products (issuance_target_business_days 5): documents complete Friday 2026-09-04, Labor Day Monday 09-07 -> fifth business day Monday 09-14 = 10 calendar days; documents complete Thursday 2026-12-24 -> Christmas (Fri) and New Year (Fri 2027-01-01) -> fifth business day Monday 2027-01-04 = 11 calendar days. An EV certificate issued on its published target is "late" under P-CD and granted goodwill, which base S2 forbids; undeclared (C3 remains, certificate member only).
- account_goodwill S3/S4/S5, account_withdrawals: no withdrawal policy remains; goodwill is only spent (C1 closed). Caps overwrite unchanged (declared, sibling tails complete).
- account_tier_benefits (new ref of P-PF/P-TU): followed by the discount sentences (renewal component only, ICANN never, restore never, M365 never, half up); the discount "factors" restate this base sentence (N1).
- account_deposits / account_credit_spending: restated and followed.

### factor_ladders
42 declared factors. Method all-pairs (skill test: a `method` tier must change the algorithm, not substitute a rate):
| factor | tiers | verdict |
|---|---|---|
| P-PF certificate_charge | price_Nyr_per_year x years + names x years / price_1yr + names / 0 | T1 vs T2 = the same per-year-price x years formula with years 1 and another rate -> mislabelled parameter |
| P-PF free_domain_charge | renewal x yrs + icann x yrs / restore_fee + n x (renewal + icann) / 0 | passes (adds restore_fee term) |
| P-TU hosting_charge | rate_N x months / monthly_rate_no_commitment / 0 | same rate x months formula (months 1) -> mislabelled |
| P-TU email_charge | seats x monthly price / seats x annual price x 12 / 0 | same seats x price x months formula -> mislabelled |
| P-PG delay_basis, P-RV review_basis, P-DU duplicate_basis (flat middle tier now), P-CD issuance_basis, P-RD reset_basis, P-RP posting_basis | tariff/ceil/flat/share tiers | pass |
(C7: retry_estimate, competing_holdback, renewal_hold removed; duplicate_basis now passes. New members above.)
Reseller-discount factors (P-PF hosting_/certificate_/domain_reseller_discount; P-TU domain_/hosting_/email_reseller_discount): tier 1 (Gold/Platinum) and tier 2 (Bronze/Silver) select the identical value "P('<x>_discount_pct') of the charge"; the fall-through ("any other account takes no percentage") equals that same expression for Personal/Business, whose pct is 0 — one rule (base account_tier_benefits) written as three tiers (N1).
Unreachable fall-throughs (N5): P-DU duplicate_funding "any other duplicate adds nothing" — a domain auto-renew is funded by account credit or the default card (auto_renew_funding_order) and every credit payment carries its purchase entry (account_credit_spending "Each paid charge is recorded once, with the reference number"); P-DU refund_route "any other refund line adds nothing" — a refund line's refund_destination is original_payment_method or account_credit (schema: none only on charge lines); P-RP credit_election "any other charge adds nothing" — the remaining method, bundle_credit, "has nothing to refund" (domain_refunds). Each ladder has two reachable tiers, and its baseline is a tier no customer of this write can occupy. (duplicate_funding and credit_election were already so in revision_1 and were missed then.)
Realism (N4): (a) P-PF free_domain_charge's redemption tier counts "restore_fee plus ..." in a prefund "so that account credit pays the auto-renew charges", while domain_auto_renew charges only while active or on_hold and a restore is a separate manual charge (domain_redemption_restore) — no auto-renew will draw that credit; (b) P-RP priority_posting: "whose priority support promises a posting within priority_posting_days calendar days" — priority_support is "Whether calls and chats route to the priority support queue" (account parameter_schema); no charter promises a posting time, and its sub-condition "the posting lagged more than priority_posting_days days" (1) holds for every customer the schedule reaches (lag > 3).
Remaining new factors judged real: P-PG money_back_time, term_commitment 12-month tier; P-CD refund_window_used, validation_route; P-DU refund_route values; P-RD/P-RV severity now ordered alike. Observation: P-PG plan_class (kept).

### findings
- C1 closed. C2 closed. C4 closed. C5 closed. C8 members R1–R12 closed (removed). C9 closed. C10 closed.
- **C3 SOURCE-POLICY RED (certificate member)** — P-CD's framing sentence is false for EV products; EV certificates issued on target are granted goodwill (demonstration above). Not live in task 1 (OV, 3 business days).
- **C6 SOURCE-POLICY RED (member f only)** — reset date taken from any single security-change notice. Not live in task 1.
- **C7 SOURCE-FACTOR RED (new members)** — certificate_charge, hosting_charge, email_charge mislabelled `method`; P-TU has no passing method factor. Bears on task 0 (certificate_charge) and task 1 (hosting_charge, email_charge).
- **N1 SOURCE-FACTOR RED** — six reseller-discount "ladders" with identical tiers restating account_tier_benefits. Both tasks.
- **N2 SOURCE-FACTOR RED (XF A1)** — three discount factors read another factor's output through a duplicated expression. Both tasks (demonstrated in the task files).
- **N3 SOURCE-POLICY RED (XF A4 + rule two readings)** — (a) cross-product price copies omit owning-charter clauses; (b) P-TU's "every other auto-renew charge" sentence vs its counted list. Not live in either world.
- **N4 SOURCE-FACTOR RED (XF D18)** — (a) redemption restore counted as an auto-renew charge; (b) invented priority-posting promise with a scope-restating sub-condition. (b) live in task 1.
- **N5 SOURCE-FACTOR RED** — unreachable fall-through tiers (duplicate_funding, refund_route, credit_election). Both tasks.

## closing_checklist (revision_2)
- Both task files carry revision_2 derivations (on disk before the 15:48:27Z reveal) and comparisons; every scored write and every factor_sensitivity / baseline_result figure equals the auditor's recomputation.
- Scopes disjoint and complete; uuid8s independent (new 8453f2b2). Trees: 3 prerequisites, 3 value_input edges, user-owned root, acyclic, load-bearing, unmet at the opening, order-independent — PASS in both tasks.
- Round-1 items closed: C1, C2, C4, C5, C8 (R1–R12), C9, C10; C6 a/b/c/d/e/g; T0-F1, T0-F2, T0-F4, T1-F1, T1-F2, T1-F4, T1-F5, T1-F6. Still open: C3 (certificate member), C6 (f), C7 (new members). New: N1–N5 (N5's duplicate_funding / credit_election members already existed in revision_1 and were missed by that round's audit). Regression: P-DU lost its near-miss (T0-R2-3).
- Gates: snapshot r2 is the record; not re-run by the auditor beyond that snapshot. The difficulty does not pass the source-layer audit.

VERDICT revision_2: task0=RED task1=RED charter=C3,C6,C7,N1,N2,N3,N4,N5

## revision_3

## charter_global_frozen
- Written before any revision_3 GT was opened. Entry: worklog tail `REWORK round 3: gates 7/7 green` confirmed; snapshot run execute-only -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r3.txt: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; views 0.view b61bc4fb...6eac, 1.view 0a488d3f...67ab; account.extended.yaml 336adcde...45dc (changed from 862f9d7f...), task_tools.py 7be694eb... (unchanged since revision_2 — the action_binding_and_uuids section of revision_2 is carried forward on that hash). Charter changed -> all other charter sections re-derived; P-PG and P-RV are byte-identical to revision_2 and were re-swept, not re-derived.
- Reworker claims read by item id only (no scored values). owner_ruling.md read: both roots are the holder's own deposit of their own funds into account credit (ruling item c) — accepted. check_traceability not run.

### policy_conflict_scan
- Same eight policies, tools and reference kinds as revision_2 (six distinct goodwill references). P-PF now counts the plan, the certificate installed on it, the security plan on its site, the email subscription on its primary domain and the free domain (auto-renew, grace renewal or restore); P-TU counts the retry plus the customer's single plan, email subscription, security plan, server and certificate due before the retry; each states that charges of other holdings are not counted (N3 b closed).
- Overlap (observation): P-PF and P-TU are both `on_request` deposits. In task 1's world P-PF is also in scope (the plan's next attempt, the 3-day retry on 2026-10-25, is inside 14 days), but the customer's stated purpose (credit to pay the declined vellumandink.com renewal, a domain not tied to the plan) selects P-TU; no second reading of the request.

### rule_compute_equivalence
- mech.py: compute_basis quotes verbatim, baseline sentences in rule, prerequisite sources in rule, no factor binding read by another factor, no binding shared, no factor id in a tool name. Assembly bindings pf_needed / tu_needed read each factor's own discount binding (assembly — allowed). The covered-domain read of P-CD is now one plain binding cd_on_domain read by site_coverage and validation_route (N2 sweep: no duplicated factor expression anywhere; N2 closed).
- Tier discounts are plain rule sentences on each counted charge (N1 closed). Rounding is RND(x + 1e-9, 2) for half up (DSL-KNOWN ruling).
- N3 a sweep of every copied price against its owning charter: hosting (scheduled term change priced, scheduled downgrade -> out of scope, 1-month = monthly_rate_no_commitment without setup fee), email (scheduled seat count used; instalment plans and scheduled product -> out of scope; M365 never discounted), security (term price, higher of hosted_site_discount_pct and tier pct, never added; security_holdings has no scheduled-change field, so no unpriced state exists), server (add-ons -> out of scope; server_discount_pct where account_discount_applies), certificate (last term capped at max_subscription_years, extra names, no volume ladder), domain (renewal component discounted, ICANN never; grace renewal min_renewal_years; restore fee + included years, no discount, restore_available and the redemption window checked), tier-review downgrade grace/due -> out of scope. N3 a closed.
- C6 f: P-RD now requires the approved request decided within the two months, the only security-change notice dated on/after that decision, and the sign-in showing the requested change; probes (holder's own later change -> second notice or a different sign-in; old decision; notice before decision) fall outside. Closed.
- **New, P-DU partner_standing (rule sentences in conflict):** "The partner uplift ... follows the account tier recorded on the duplicate's charge date, the tier whose benefits applied to that charge: ... an account that was already Harborline Reseller Bronze or Harborline Reseller Silver on that date adds uplift_partner; any other account, including one that reached its current tier only after that date, adds nothing." Compute: `du_partner_uplift` from the CURRENT variant_name and `tier_changed_date <= dup date`. World: an account that was Reseller Silver on the duplicate's charge date and moved to Reseller Gold afterwards (an account_tier_change after the charge is producible). The second sentence ("already ... Silver on that date adds uplift_partner") gives uplift_partner; the third ("one that reached its current tier only after that date, adds nothing") and compute give 0. Two values for the same scored grant (finding R3-1). The tier held on a past date is not record-visible (only the current tier and its change date), which is why the sentences cannot agree.

### action_binding_and_uuids
- Carried forward from revision_2 (task_tools.py hash unchanged 7be694eb...).

### prerequisite_graph / prerequisite_sentences
- Graph unchanged in shape (two stars, value_input on pf_balance / tu_balance, state form, single resolving write per edge). E4 now "more than eleven calendar days after the subscription's documents were complete" = P-CD's allowed_issue_days 11; E5 restates P-RD's new linkage tests (decided within the two months, notice on/after the decision, sign-in shows the change) — equal to compute `rd_linked`; conditions match the sentences. Yearly-limit clause kept on every edge (C4 stays closed).

### override_declarations
- C3: P-CD "no such span, weekends and US federal holidays included, is longer than allowed_issue_days [11] calendar days" — checked worst cases: Christmas and New Year both on Fridays (documents Thursday 12-24 -> fifth business day Monday 01-04 = 11), both on Mondays (Friday 12-22 -> Tuesday 01-02 = 11), both observed Fridays (2021: 11); no 5-business-day span exceeds 11. An on-target EV issue is never "late". Closed.
- Other base sentences: as revision_2 (followed / declared).

### factor_ladders
| policy | factors (label) | notes |
|---|---|---|
| P-PF | plan_term_rate (P), certificate_renewal_price (P), security_plan_charge (P), email_renewal_charge (P), free_domain_charge (M) | price ladders now honestly parameter; free_domain_charge tiers (restore: fee + included years, no discount / renewal with rounded component discount / none) differ in formula — passes |
| P-TU | plan_renewal_term (P), mail_renewal_plan (P), site_security_charge (M), server_term_price (P), certificate_term_price (P) | site_security_charge: max-pick of hosted-site and tier percentages / tier percentage alone / none — passes XF A6 ("max/conditional pick"); observation: close to a rate substitution |
| P-DU | duplicate_basis (M), duplicate_size, funding_route, partner_standing (P) | funding_route tiers card->card / card->credit (+ ledger refund entry) / credit-paid: all reachable (N5 member closed); partner_standing: R3-1 |
| P-RP | posting_basis (M), refund_size, credit_election, renewal_exposure (P) | credit_election PayPal / card / credit-paid: all reachable (N5 member closed); renewal_exposure real (renewals draw credit first); priority_posting removed (N4 b closed). Observation: the PayPal-vs-card split rests on the thin ground "what the customer gave up" |
| P-PG, P-RV, P-CD, P-RD | unchanged ladders (P-CD binding fix only) | re-swept: all fall-throughs reachable, no equal outcomes, labels honest; plan_class observation kept |
- Sweep of every class raised in revisions 1–3 across all eight policies: A1/N2 (clean), A6/C7 (clean under the recipe's test), N1 equal outcomes (none), N5 unreachable fall-throughs (none), C6 first-match/tie reads (all scoped by counts or stated ties), N3 owning-charter clauses (clean), B13 framing clauses (only R3-1), D18 realism (no new member beyond the observations), D22 zero-amount (closed), owed-at-once (checked per task).

### findings
- Closed in revision_3: C3, C6 (f), C7 (new members relabelled; remaining methods pass), N1, N2, N3 (a, b), N4 (a, b), N5.
- **R3-1 SOURCE-POLICY RED** — P-DU partner_standing: its own sentences give uplift_partner and 0 to an account that was Bronze/Silver on the charge date and changed tier afterwards; compute takes the current tier. Bears on task 0's tree; not live there (account Bronze since 2026-01-19, before the 2026-08-13 duplicate, no later change).

## closing_checklist (revision_3)
- Both task files carry revision_3 derivations (on disk before the 17:49:37Z reveal) and comparisons; every scored write and every factor_sensitivity / baseline_result equals the auditor's recomputation.
- Scopes disjoint and complete; trees 3 prerequisites / 3 value_input / user-owned deposit root (owner ruling c) / acyclic / load-bearing / unmet at the opening / order-independent; every computation 4–6 factors with >= 2 parameter and 1 method, near-misses present in all eight computations, cross-difficulty and multi-source factors present, seeded cross-category rows priced as their charters produce them.
- Round-2 REDs closed: C3, C6, C7, N1, N2, N3, N4, N5; task items T0-R2-1..3, T1-R2-1..3. New: R3-1 (charter-level, not live in either world).
- Gates: snapshot r3 is the record. Because R3-1 is open, the difficulty does not yet pass the source-layer audit at charter level.

VERDICT revision_3: task0=PASS task1=PASS charter=R3-1

## revision_4

## charter_global_frozen
- Written before any revision_4 GT was opened. Entry: worklog tail `REWORK round 4: gates 7/7 green` confirmed; snapshot run execute-only -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r4.txt: all 7 gates OK; views unchanged (0.view b61bc4fb...6eac, 1.view 0a488d3f...67ab — same hashes as revision_3); account.extended.yaml 9b495d5d...7d77 (changed from 336adcde...), task_tools.py 7be694eb... (unchanged). Reworker claims read by item id only. owner_ruling.md: both roots remain the holder's own deposits (item c).
- Change set: only account_ext_duplicate_renewal_goodwill differs from revision_3 (parsed per-policy diff); within it only the partner_standing rule sentence, its two compute_basis quotes and its ladder wording changed; compute, params and every other policy byte-identical. Charter-global sections of revision_3 are carried forward for the seven unchanged policies; P-DU re-derived below; the full class sweep re-run over all eight policies.

### P-DU partner_standing (R3-1 re-check)
- Rule now: "The partner uplift ... follows the account's current tier and its tier changed date: an account whose current tier is Harborline Reseller Gold or Harborline Reseller Platinum and whose tier changed date is on or before the duplicate's charge date adds uplift_partner_top; an account whose current tier is Harborline Reseller Bronze or Harborline Reseller Silver and whose tier changed date is on or before that date adds uplift_partner; any other account, including one whose tier changed date is after that date whatever tier it held before, adds nothing." Compute `du_tier_since = DAYS(tier_changed_date, dup date)`, `du_partner_uplift` on current variant_name and `du_tier_since >= 0` — word for word the same test; the Silver->Gold-after-the-charge world now has one reading (0). Decidable from the account record alone. R3-1 closed.
- Ladder: three disjoint, reachable tiers with distinct values; label parameter honest; fall-through = baseline 0. Observation: an upgraded partner whose upgrade post-dates the charge gets no partner uplift — a stated, narrow treatment, not a demonstrable unreal one.

### class sweep (all eight policies, every class raised in revisions 1–4)
- mech.py: compute_basis quotes verbatim; baseline sentences in rule; prerequisite sources in rule; no factor reads or duplicates another factor's binding (A1/N2); no factor id in a tool name.
- Past-date state readings (B13, the R3-1 class): rule sweep for "tier recorded / on that date / as of / at the time / held before / was already / on the charge date" — only the new partner sentence, which reads current records; none elsewhere.
- C7/A6 labels, N1 equal outcomes, N5 unreachable fall-throughs, C6 first-match/tie reads, N3 owning-charter clauses, C3 framing, C4 zero room, D18 realism, owed-at-once: unchanged policies -> revision_3 conclusions stand; P-DU re-checked — clean.

### findings
- R3-1 closed. No new charter-level RED.

## closing_checklist (revision_4)
- Task files carry revision_4 freeze notes (before the 18:06:50Z reveal) and comparisons; both tasks PASS on all four relationships; scopes disjoint and complete; trees, factors, near-misses, seeds and owner ruling as closed in revision_3; R3-1 closed; full class sweep clean; no regression.
- Gates: snapshot r4 is the record (7/7 OK). The difficulty passes the source-layer audit.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen
- Written before any revision_5 GT was opened. Entry: worklog tail `REWORK round 5: gates 7/7 green` confirmed; snapshot run execute-only -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r5.txt: all 7 gates OK; views unchanged (0.view b61bc4fb...6eac, 1.view 0a488d3f...67ab); account.extended.yaml d91091f1...192e (changed from 9b495d5d...), task_tools.py 7be694eb... (unchanged). Items under re-check: src=S1, S2 of audits/policy_kb/account_credit_and_recovery/VERDICT.md (KB audit revision_1; read for the S1/S2 definitions only). Reworker claims read by item id only. owner_ruling.md: both roots remain the holder's own deposits (item c).
- Change set (parsed per-policy diff vs revision_4): P-PF (scope sentence absorbs "charges of any other holding are not counted"; new plain binding pf_window read by the scope and every due test; pf_cert_end / pf_cert_due / pf_cert_years moved into certificate_renewal_price), P-TU (new plain binding tu_count_window = the retry lead, read by every due test; tu_plan_id moved into plan_renewal_term), P-DU and P-RP (combination sentence wording only). Compute values, params and the other four policies unchanged. Sections for unchanged policies carried forward from revisions 3–4; changed policies re-derived; full class sweep re-run.

### S1 (XF A2) re-check
- P-DU: "Where the schedule's adjustments apply, the fixed uplifts that apply are added to the duplicate-charge goodwill figure, the limits are then applied, and only the final figure is rounded half up to the cent." P-RP: same with "the late-posting goodwill figure". Both now name the schedule's figure (a quantity the baseline defines and the method factor's basis sentence varies), the same construction P-PG, P-RV, P-CD and P-RD use; no factor-owned quantity is named in an assembly sentence; order unchanged (uplifts, limits, one rounding) and equal to du_figure / rp_figure + result. Quotes verbatim. Closed.
- Sweep of every assembly sentence of the charter: P-PF "the plan's renewal list price together with every other counted charge, all added together, less every discount that applies" (the list price is baseline-defined), P-TU "the retry charge together with every other counted charge ..." (retry charge is a plain baseline quantity), goodwill schedules "the ... goodwill figure ..." — no other member.

### S2 (XF A3) re-check
- pf_cert_end, pf_cert_due, pf_cert_years are now bindings of certificate_renewal_price; tu_plan_id of plan_renewal_term. Mechanical A3 sweep (plain binding read by exactly one factor and by no baseline or plain binding): revision_4 file -> 2 members (pf_cert_years, tu_plan_id); revision_5 file -> 0 members. A1: no factor reads another factor's binding; no binding shared. Closed.
- New plain bindings pf_window (window_days) and tu_count_window (retry lead) are shared selections read by the scope test / several factors' due tests — plain by A2; their compute_basis quotes are verbatim rule text.

### class sweep (all eight policies, every class raised in revisions 1–5)
- mech.py clean (quotes, baselines, prerequisite sources, factor independence, factor ids vs tool names). A2/A3 as above. C7/A6 labels, N1 equal outcomes, N5 reachable fall-throughs, C6 first-match/tie reads, N3 owning-charter clauses and account_tier_benefits stacking (tier discount on list/renewal components only, ICANN and restore never, M365 never, security single higher percentage, no ssl volume ladder on renewals), C3 framing, C4 zero room, B13 past-date readings, D18 realism, owed-at-once: unchanged conclusions, re-confirmed on the changed policies.

### findings
- S1 closed; S2 closed. No new charter-level RED. (K1–K3 are KB-side items outside this audit; their source-side bindings, pf_window and tu_count_window, introduce no source defect.)

## closing_checklist (revision_5)
- Task files carry revision_5 freeze notes (before the 19:22:00Z reveal) and comparisons; both tasks PASS on all four relationships; S1 and S2 closed; no new defect; no regression (values, sensitivities, trees, near-misses, seeds and owner ruling as in revision_3–4).
- Gates: snapshot r5 is the record (7/7 OK). The difficulty passes the source-layer audit.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen
- Written before any revision_6 GT was opened. Entry: worklog tail `REWORK round 6: gates 7/7 green` confirmed; snapshot run execute-only -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r6.txt: all 7 gates OK; 0.view 57d65594...1a01 (rebuilt: three email_events rows added), 1.view 0a488d3f...67ab (unchanged); account.extended.yaml d180cc83...dc21 (changed from d91091f1...), task_tools.py 7be694eb... (unchanged). Items under re-check: src=S3, S4 of the latest KB-VERDICT (revision_3) in audits/policy_kb/account_credit_and_recovery/VERDICT.md (read for the S3/S4 definitions only). Reworker claims read by item id only. owner_ruling.md: both roots remain the holder's own deposits (item c).
- To judge S3/S4 against what the customer-facing corpus publishes, the auditor read the published documents docs/email/{term_renewal_calculation, deleted_mailboxes_seats_term_renewal, price_column_term_renewal, reseller_tier_rate_term_renewal, late_payment_fee_term_renewal, renewal_product_term_renewal, term_renewal_desk_article, renewals_and_instalments}_*.json and docs/ssl/{scheduled_auto_renew_charges, auto_renew_charge_amount, organisation_re_vetting_fee_on_auto_renewal, harborline_domain_credit_on_auto_renewal, reseller_discount_on_auto_renewals, multi_year_name_rate_on_auto_renewals, extra_name_bands_on_multi_year_auto_renewals, support_desk_renewals}_*.json. No sibling tasks directory was read.
- Change set (parsed per-policy diff vs revision_5): P-PF and P-TU only — the email renewal sentences and bindings (renewed seats via idle seats from mailbox deletions/restores), the certificate sentence ("because account credit pays it, its charge is the ssl charter's renewal price"), and cross_category reads (email term_start_date, email_events). The other six policies are byte-identical.

### S3 re-check (email renewal seats vs the published term-renewal rule)
- Published rule (deleted_mailboxes_seats_term_renewal): idle seats = mailbox deletions in the current term less their restores, by the whole-calendar-month test; with a scheduled seat count, renewed seats = min(scheduled, seat count) but never fewer than seat count less idle seats; without one, seat count less idle seats (= seat count when idle is 0). P-PF / P-TU now state exactly this, and compute matches: `pf_mail_deleted` / `pf_mail_restored` = XCOUNT within_months = MONTHS(term start, today) + 1 (i.e. MONTHS(deletion, today) <= MONTHS(term start, today)), restores matched on their `deleted_at`; `pf_mail_in_use = seat_count - MX(0, deleted - restored)`; `pf_mail_seats = MX(MN(scheduled, seat_count), in_use)` or in_use.
- The other published term-renewal factors agree with the copy: price column (annual commitment for annual prepaid; month-to-month for monthly), reseller tier rate (reseller tiers only; M365 none — the non-reseller tiers' email_discount_pct is 0), renewal product (scheduled product -> P-PF/P-TU stand aside), late-payment fee (none for a renewal paid on or before its due date, as an auto-renew attempt before the term end is). Closed.

### S4 re-check (certificate renewal price)
- Published SSL corpus: scheduled_auto_renew_charges §3 "an auto-renew charge that the account credit balance covers in full on that day is paid from account credit by the account's credit run and is not booked under this rule" — the card-charged auto-renew rule (with re-vetting fee, Harborline-domain credit, cert-component-only reseller discount, multi-year name rate and bands) does not price a credit-paid renewal; base ssl_renewal prices a renewal at the tier's price for the years plus names, reduced by ssl_discount_pct, with no volume ladder. P-PF / P-TU count only certificates the deposit lets credit pay and price them exactly so; compute unchanged and equal. The corpus sentence support_desk_renewals 1.2 "Every auto-renew charge is priced under the auto-renew charge rule" contradicts §3 — that is a defect of the SSL difficulty's published corpus, outside this charter; the account rule names its own price in full, so its reader has one value. Closed for this charter (observation: SSL-side 1.2 vs §3 remains for the SSL difficulty's audit).

### class sweep (all eight policies, every class raised in revisions 1–6)
- mech.py clean (quotes verbatim, baselines in rule, prerequisite sources, factor independence, factor ids vs tool names); A3 single-factor sweep: 0 members (new bindings pf_mail_plan_ref, pf_mail_months, pf_mail_deleted, pf_mail_restored, pf_mail_in_use and the tu_ counterparts all belong to their email factors); A2 assembly sentences unchanged; N3/A4 owning-charter clauses re-checked for email (above) and ssl (above); C7/A6, N1, N5, C6 ties, C3, C4, B13, D18, owed-at-once: unchanged conclusions.
- Observation: "the email charter's published term-renewal rule" / "the ssl charter's renewal price" are pointers followed in the same rule by the full computation, not delegations (XF A4 satisfied).

### findings
- S3 closed; S4 closed. No new charter-level RED.

## closing_checklist (revision_6)
- Task files carry revision_6 freeze notes (before the 02:28:16Z reveal) and comparisons; task 0 re-derived on its rebuilt view, task 1 re-run; both PASS on all four relationships; S3 and S4 closed; no new defect; no regression.
- Gates: snapshot r6 is the record (7/7 OK). The difficulty passes the source-layer audit. Outside this charter: the SSL corpus sentence support_desk_renewals 1.2 contradicts scheduled_auto_renew_charges §3 (for the SSL difficulty's own audit).

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen
- Written before any revision_7 GT was opened. Entry: worklog tail `REWORK round 7: gates 7/7 green` confirmed; snapshot run execute-only -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r7.txt: all 7 gates OK; views unchanged since revision_6 (0.view 57d65594...1a01, 1.view 0a488d3f...67ab); account.extended.yaml 42fa915c...acf8 (changed from d180cc83...), task_tools.py 7be694eb... (unchanged). Subject: the coordinator's cross-product alignment — one price per renewal whatever pays it; certificate auto-renewal priced by the published ssl auto-renew rule. Reworker claims read by item id only. owner_ruling.md: roots remain the holder's own deposits (item c). Published corpus read for the check: docs/ssl auto-renew documents (calculation note, reseller discount, multi-year name rate, name bands, re-vetting fee, Harborline domain credit, scheduled charges, support desk), docs/domain renewal_charge_terms / auto_renew_service_terms / grace_period_renewal_billing / autopay_credit_*, docs/hosting renewal_terms_and_auto_renew_attempts / early_ and overdue_renewal_at_checkout, docs/security siteguard renewal terms, docs/server server_term_renewal_terms, docs/email term-renewal documents (revision_6).
- Change set: P-PF and P-TU only (other six policies byte-identical). P-PF: certificate priced by the ssl auto-renew rule; free domain in grace or redemption moved out of scope and the free-domain auto-renew charge made a plain baseline charge (restore/grace tiers withdrawn); email split into email_renewed_seats (method) and email_seat_price (parameter). P-TU: certificate priced by the ssl auto-renew rule.

### alignment check — every counted charge against its product's published rule
| charge | published rule | account copy | verdict |
|---|---|---|---|
| certificate auto-renew (P-PF, P-TU) | years of the latest renewal/auto-renew line else the purchase line, capped; tier ssl percentage on the price component only (reseller tiers only — non-reseller pct is 0); names at the multi-year name rate and bands per year, never discounted; reduced amount rounded; OV/EV re-vetting fee 29 / 49 where (days from organisation validation to the current end) + 365 > 398; Harborline-domain credit 6 (Harborline DNS) / 3 (external) for an active Harborline covered domain; rounded | identical sentences and compute (`pf_cert_line_years`, `pf_cert_name_rate`, `pf_cert_name_units`, `pf_cert_fee`, `pf_cert_credit`, `pf_cert_charge = RND(RND(price x (1-d) + names) + fee - credit)`), "whichever source pays it" | aligned |
| hosting auto-renew | early_/overdue_renewal_at_checkout: "an auto-renew charge ... is billed at the regular rate of the tier and term length that the new term will have ... less the account tier's hosting discount"; new term from a scheduled term change | same | aligned |
| domain auto-renew (free domain, retry) | grace_period_renewal_billing scope: an auto-renew charge is billed at renewal price per year, component reduced by the tier's domain renewal percentage, plus ICANN; autopay credits apply to manual price matches only | same | aligned |
| email term renewal | revision_6 S3 rules (seats, price column, reseller rate, product, fee) | same; seats now a method factor whose tiers are the published three cases | aligned |
| SiteGuard renewal | term price reduced by the higher of hosted-site and tier percentages | same | aligned |
| server renewal | tier price for the term plus active add-ons less the account discount | same, add-ons out of scope | aligned |
| free domain in grace / redemption | priced by the domain charter's own grace and restore rules | now outside the prefund's scope (stated) | aligned |
- Observation (outside this charter): docs/ssl scheduled_auto_renew_charges §3 still says a credit-paid auto-renew "is not booked under this rule"; under the coordinator's alignment the SSL corpus is the side to change. The account rules state their own certificate price in full, so their reader has one value.

### structure (all eight policies)
- mech.py clean; A3 single-factor-binding sweep 0 members (all new certificate and email bindings sit inside their factor); A1 clean.
- P-PF factors: plan_term_rate (P), certificate_renewal_price (P — the years ladder selects the price component; fee, credit and names are bindings of the same factor), security_plan_charge (P), email_renewed_seats (M — min/max with the in-use floor / seat count less idle seats / seat count: added operation and input, passes A6; baseline = seat count = fall-through), email_seat_price (P). Five factors, 4 parameter + 1 method. P-TU unchanged in shape. Ladders disjoint, reachable, distinct outcomes; baselines honest.
- Re-swept every class from revisions 1–7 (A1/A2/A3, A6/C7, N1, N5, C6 ties and absent records — an OV/EV without an organisation validation date cannot be an active issued subscription, so the fee's absent-date branch is unreachable — N3/A4 owning-charter clauses as tabled, C3, C4, B13, D18, owed-at-once): clean.

### findings
- Alignment applied to every counted charge. No charter-level RED.

## closing_checklist (revision_7)
- Task files carry revision_7 freeze notes (before the 10:07:04Z reveal) and comparisons; both tasks PASS; the cross-product alignment is applied to every counted charge in P-PF and P-TU; no new defect; no regression (goodwill values, trees, near-misses, seeds, owner ruling unchanged; the two moved deposit values match the published rules).
- Gates: snapshot r7 is the record (7/7 OK). The difficulty passes the source-layer audit. Outside this charter: docs/ssl scheduled_auto_renew_charges §3 still describes credit-paid auto-renewals as "not booked under this rule".

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen
- Written before any revision_8 GT was opened. Entry: worklog tail `REWORK round 8: gates 7/7 green` confirmed; snapshot run execute-only -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r8.txt: all 7 gates OK; views unchanged since revision_6; account.extended.yaml 9cec8a70...d9b8 (changed from 42fa915c...), task_tools.py 7be694eb... (unchanged). Items under re-check: renderer findings F1, F2 of audits/render_source/account_credit_and_recovery/render_r4.md (read for their definitions only). Reworker claims read by item id only. owner_ruling.md: roots remain the holder's own deposits (item c).
- Change set: P-PF and P-TU only — one certificate rule sentence each and the bindings pf_cert_fee / tu_cert_fee; other six policies byte-identical.

### F1 (rounding grouping of the certificate charge)
- Rule now: "The reduced amount, the reduced certificate price component together with the extra-name amount, is rounded half up to the cent; ... then adds a re-vetting fee ...; ... then takes off a Harborline domain credit ...; and the result is rounded half up to the cent." (P-TU: same with "That reduced amount".) Compute `RND(RND(price x (100 - ssl_discount_pct)/100 + names) + fee - credit)` — same grouping; equal to the published ssl assembly ("the reduced amount, the sum of the price components, is rounded half up to the cent before any fixed fee is added or any fixed credit is subtracted; the result is then rounded"). Closed.
- Disclosure: revision_7 recorded "identical sentences and compute" for this charge without noticing that "The reduced amount" did not say whether the extra names belonged to it; the renderer's finding was correct and is now closed.

### F2 (re-vetting fee with no organisation-validation date)
- Compute now adds the fee only when an organisation validation date is recorded and the age test is met; with no date the fee is 0 — what the rule words ("an OV or EV product whose organisation validation ... would be older than ...") and the published re-vetting schedule (age-defined only) give. Probe on a scratch copy of task 0's world with the date blanked: the prefund drops by exactly the fee. Closed.
- Disclosure: revision_7 judged this branch "unreachable" and therefore clean. Under XF B9 every branch needs a rule tier whether reachable or not; it should have been reported then.

### class sweep (all eight policies, every class raised in revisions 1–8)
- Absent-record branches (the F2 class), all compute branches on None / empty values checked against rule words: P-PF free domain absent -> no charge (stated); certificate covered domain absent -> no credit (stated); P-CD OV/EV with no organisation validation date -> documents never complete -> outside the schedule (the rule's condition is not met; compute 0); P-RV / P-RD missing decision or notice -> outside (stated); P-DU missing duplicate date -> outside; P-RP refund line with no ledger refund entry -> the "dated more than three days after" condition is not met -> outside (compute 0). No further member.
- Rounding-grouping sentences (the F1 class): every discount sentence states "the charge less the reduced charge rounded half up"; domain renewal "renewal price times the years reduced by the discount and rounded half up, plus the ICANN fee"; goodwill schedules "rounded half up once, at the end" after the stated order. No further member.
- mech.py clean; A1/A3 clean; A6, N1, N5, C6, N3/A4 (alignment table of revision_7 unchanged), C3, C4, B13, D18, owed-at-once: unchanged conclusions.

### findings
- F1 closed; F2 closed. No charter-level RED.

## closing_checklist (revision_8)
- Task files carry revision_8 freeze notes (before the 10:14:37Z reveal) and comparisons; both tasks PASS; F1 and F2 closed; the F1/F2 classes were swept across the whole charter with no further member; no regression.
- Gates: snapshot r8 is the record (7/7 OK). The difficulty passes the source-layer audit.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

## charter_global_frozen
- Written before any revision_9 GT was opened. Entry: worklog tail `REWORK round 9: gates 7/7 green` confirmed; snapshot run execute-only -> /tmp/erl0076_coord/snap_account_credit_and_recovery_r9.txt: all 7 gates OK; views unchanged since revision_6; account.extended.yaml e81a6485...453a (changed from 9cec8a70...), task_tools.py 7be694eb... (unchanged). Item under re-check: src=S5 of KB-VERDICT revision_5 (audits/policy_kb/account_credit_and_recovery/VERDICT.md, read for its definition only). Reworker claims read by item id only. owner_ruling.md: roots remain the holder's own deposits (item c).
- Change set: P-PF only (other seven policies byte-identical). Email charge back to one method factor email_renewal_charge (seat basis x seat price inside the factor); certificate price component, years and names now plain baseline text; two new parameter factors certificate_revetting_fee (EV fee / OV fee / none) and certificate_domain_credit (Harborline DNS credit / external credit / none).

### S5 (factor coupling) re-check
- Revision_8 structure: pf_mail_price = pf_mail_seats (email_renewed_seats) x pf_mail_unit (email_seat_price) in a plain binding; with email_seat_price at its baseline (0) the seats factor could not move the result (XF A7 T2 fails). Disclosure: revision_7 passed email_renewed_seats on its shape alone and did not run the factor-alone test; S5 was a real defect then.
- Now: one factor owns seats and seat price (tiers: lower-of-scheduled-and-current with the in-use floor x price / in-use x price / seat count x price / not counted). Factor-alone-against-all-baseline sweep (scratch, both worlds, every factor of all eight policies): every factor moves its result alone, except P-TU site_security_charge and certificate_term_price on task 1's world, where the shortfall with all else at baseline stays below zero (a no-top-up floor, not a dependency on another factor); on any producible world with a lower balance each moves alone (T2 holds). Multiplicative couplings left in the charter (goodwill basis x multipliers in P-PG, P-RV, P-CD, P-RD) multiply a basis whose baseline is non-zero, so each multiplier moves alone (sweep confirmed). Closed.
- New P-PF factors: certificate_revetting_fee — tiers EV (> reuse period) / OV (> reuse period) / none, distinct values, published ssl re-vetting schedule; certificate_domain_credit — Harborline DNS / external / none, published credit note; both parameter, honest, fall-through = baseline 0, each moves alone. The certificate charge's assembly sentence names "the fixed fee added and the fixed credit taken off that apply to it" generically (A2). email_renewal_charge passes A6 (min/max with floor / subtraction of idle seats / plain seat count / none).
- K4 (KB side): no factor sentence names a quantity defined only in another factor (the email sentence carries its own seats and price; fee and credit sentences stand alone).

### class sweep (all eight policies, every class raised in revisions 1–9)
- mech.py clean (quotes, baselines, prerequisite sources, A1, factor ids vs tool names); A3 (plain binding read only by one factor and by no baseline): 0; factor-alone (S5 class): as above; A6, N1, N5, C6, N3/A4 (revision_7 alignment unchanged — certificate auto-renew rule terms all still applied), C3, C4, B13, D18, F1 grouping, F2 absent branches, owed-at-once: unchanged conclusions. P-PF still five factors (4 parameter, 1 method); P-TU unchanged.

### findings
- S5 closed. No charter-level RED.

## closing_checklist (revision_9)
- Task files carry revision_9 freeze notes (before the 10:32:21Z reveal) and comparisons; both tasks PASS; S5 closed; the factor-alone (T2) sweep now run over every factor of all eight policies; no new defect; no regression.
- Gates: snapshot r9 is the record (7/7 OK). The difficulty passes the source-layer audit.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
