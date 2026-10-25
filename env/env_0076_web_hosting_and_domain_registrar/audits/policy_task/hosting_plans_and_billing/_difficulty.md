# Policy-task audit — hosting_plans_and_billing / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-22T12:41Z, before any task GT was revealed. Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiator.
- Hashes (sha256, recomputed by the auditor, equal to the coordinator brief):
  - `tasks/hosting_plans_and_billing/hosting.extended.yaml` f3968c7945e6f97871511da187b9e5f3d56883c955ab554bef9125156b7e8b46
  - `tasks/hosting_plans_and_billing/task_tools.py` b43eb6904d797c391f79e79e5d25a39c45b1fcbf1d65380184331bb9d58e0c83
  - masked views `.audit_views/policy/hosting_plans_and_billing/0.view.json` 9a514adf…22ca, `1.view.json` f4b6d4aa…2e86
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/hosting.yaml and (for cross-category reads) the relevant policies/parameters of account.yaml, domain.yaml, email.yaml, ssl.yaml; the extended charter; task_tools.py; the two masked views; `audits/render_source/XF_recipe.md`; the DSL sandbox in `skills/erl-task-instantiate/scripts/check_compute.py` (to fix the semantics of MONTHS/DAYS/within_months/CFIELD/LATEST/MAX/RND).
- Masked / not read before the freeze: tasks/*.json (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure), plan.md, worklog.md of this difficulty, every other difficulty's tasks directory, every other scenario. No recursive search touched tasks/.
- Step 0 entry conditions: gate snapshot `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r1.txt` shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked-view hashes supplied and verified; check_traceability deferred by the coordinator (not run here). Entry conditions complete.
- Base copy: lines 1–1619 of the extended yaml are byte-identical to `blueprint/products/hosting.yaml` (diff empty).

### policy_conflict_scan
Extended policies (4): `hosting_ext_overdue_renewal` (bill_overdue_hosting_renewal_c53aa4e7, agent), `hosting_ext_cloud_upgrade` (buy_hosting_upgrade_8645a072, user), `hosting_ext_auto_renew_refund` (refund_hosting_auto_renewal_84b3efde, agent), `hosting_ext_early_renewal` (pay_hosting_renewal_early_31233d6b, user).

- Overlapping subjects: overdue and early both claim `[hosting_renewal_charge, hosting_term_renew]` and both supersede the same base clause of `hosting_renewal`; they are meant to be split by "term end date on or before today" vs "still later than today". The split as written is not closed — see finding P-1 (tails name each other with scopes the sibling does not have; auto-renew charges fall into the early rule's tail-routed scope).
- Refund subject `hosting_refund` overlaps base `hosting_money_back` / `hosting_agg_money_back_limit` only by event type; refund_kind differs (auto_renew_refund vs money_back), no conclusion collides — the two overwrites on those base policies retire nothing (finding P-4).
- Upgrade: scope "Cloud 4 → Cloud 8 only"; no other extended policy prices `hosting_upgrade_charge`.
- Cross-category read boundaries: account (variant_name → hosting_discount_pct) in overdue/upgrade/early; domain (status, auto_renew by bundled_hosting_id) in overdue; email (seat_count, status, email_domain) in overdue; ssl (validation_level, status, hosting_id) in early. The upgrade's two percentages collide with the account charter's in-force discount rules (finding P-3).
- Eligibility / time anchors: renewals "only while active or suspended" (base, inherited and restated); upgrade "only while active" (base); auto-renew refund window charge_date + auto_renew_refund_days inclusive (base, restated). No conflicting anchor.
- Terminal states: overdue/early advance term dates (hosting_term_renew), refund rolls back term dates and switches auto-renew off (hosting_term_rollback), upgrade moves variant (hosting_upgrade). Compatible.
- Scope exclusivity across tasks (inferred pre-reveal from the trees the rules and worlds imply; charter_scope itself masked): task 0 = {cloud_upgrade (root), overdue_renewal}; task 1 = {early_renewal (root), auto_renew_refund}. Pairwise disjoint, jointly cover the 4 extended policies.

### rule_compute_equivalence
- Mechanical sweep (scratch `/tmp/audit_hosting_plans_and_billing_0076`): every `compute_basis` value is a verbatim substring of its policy's rule (whitespace-normalised); every baseline.rule sentence is in the rule; every overwrite `replaced_by` is in the rule; every compute binding has a basis except `paid_for_current_term` (upgrade; plain sum covered by "plus any earlier upgrade_proration lines…" — observation O-8).
- DSL semantics used (from check_compute.py): `within_months=1` keeps rows with MONTHS(row,NOW)=0, i.e. strictly less than one calendar month — matches "dated less than one calendar month before today"; `MONTHS(a,b)` drops a month when day(b) < day(a) — matches "a month counts only once its day of the month is reached" (month-end case: a day never reached is not counted, consistent with the sentence); `DAYS` = calendar-day difference; `LATEST` keeps the first row on ties; `CFIELD`/`CPARAM` return the first matching holding; `MAX` returns 0.0 on no rows; `RND` is float `round()` (engine primitive, observation O-4; no scored intermediate in either world lands on a half cent).
- Per policy, rule ↔ compute agree in every branch on the two task worlds, with these exceptions (all charter-global, findings below): first-match / sum / max reads that a producible second record breaks (P-5); results with no floor or a floor at 0.00 where the tools and schema say "positive" (P-6).
- Factor ladders: every tier named in `factors[].ladder` is a sentence of its rule and a branch of its `decides` binding, and vice versa (checked for all 18 factors). No tier lives only in compute.

### action_binding_and_uuids
- `(target_tool, computes)`: (bill_overdue_hosting_renewal_c53aa4e7, amount), (buy_hosting_upgrade_8645a072, amount), (refund_hosting_auto_renewal_84b3efde, amount), (pay_hosting_renewal_early_31233d6b, amount) — each claimed once.
- uuid8s c53aa4e7 / 8645a072 / 84b3efde / 31233d6b: distinct, no shared prefix, no sequence pattern; no factor id is a substring of any tool name (XF 25).
- Docstrings: no ordering word, no other tool named, no position in a sequence; no concrete example values (XF 24); no composite string args (XF 23); every write tool calls ctx.create/ctx.update in its own body (XF 26); rounding via `_HostingCalc.cents` (Decimal half-up, class static method) (XF 11 rounding part OK).
- Tool bodies do NOT enforce the docstring contracts "positive" and "of this plan" — finding T-1.
- Trigger rule (XF 20): bodies write `hosting_renewal_charge` (charge_type renewal; payment_method only card/paypal, so the `account:account_credit_apply` trigger cannot fire), `hosting_upgrade_charge` (card/paypal only), `hosting_refund` (refund_destination fixed to original_payment_method, so `account:account_credit_refund` cannot fire). No cross-category write. The price of that closure: the refund tool cannot represent the rule's account-credit destination branch (observation O-3).
- owner=user tools are genuinely the customer's own acts: buying an upgrade of one's own plan and paying a manual renewal of one's own plan are self-service purchases; the agent tools (billing an authorised overdue renewal to a named payment method, issuing a refund) are support acts.

### prerequisite_graph
- `prerequisite` filled everywhere: overdue `[]`, refund `[]`, upgrade → overdue (E1), early → refund (E2). Both `problem` ids are extended policies of this file, neither self-referential; graph acyclic (two disjoint 2-node chains).
- E1: policy_source "An upgrade charge is fixed only after the plan's term end date is later than today." — verbatim in the upgrade rule; form state, no fallback_reason (correct); kind value_input, gate `prorated_upgrade_share` (a real binding of the upgrade compute); resolved_by = overdue's target_tool; effect (term dates advance, paying line becomes the renewal line, remaining share positive) is what the bill tool body does. Condition neither strengthened nor weakened.
- E2: policy_source "An early renewal is not billed until the plan's term start date is on or before today." — verbatim in the early rule; form state; kind value_input, gate `early_tariff_price` (real binding); resolved_by = refund's target_tool, whose body rolls term_start back. Its `effect` text, however, is written about one world ("the running term paid by the earlier 12-month line", "the term end date is days away") — finding P-7.

### prerequisite_sentences
- E1 four-point test: ordering connective "only after" ✓; waited-on state "the plan's term end date is later than today" in record words (hosting_holdings.term_end_date) ✓; no tool, policy id, snake_case token or row id ✓; strength equals the condition ✓. Unique writer: among this difficulty's writes only the overdue renewal can move a term end date from on-or-before today to later than today (the early renewal's own scope already requires a later term end; the refund moves term dates back). Derivation: sentence + `term_end_date` ≤ today in the record + overdue rule ("This rule prices the renewal of a plan whose term end date is on or before today…; The new term always starts on the previous term end date…") → bill the overdue renewal. Single reading.
- E2 four-point test: "not … until" ✓; waited-on state "the plan's term start date is on or before today" (hosting_holdings.term_start_date) ✓; no tool/id ✓; strength equals condition ✓. Unique writer: only the refund's roll-back moves term_start_date from a future date to one on or before today (the overdue renewal is out of scope while the term end is later than today). Derivation: sentence + a term start in the future, which only a prepaid auto_renew line produces + refund rule ("Refunding the auto-renew charge rolls the plan back to the term paid before it…"; "The charge refunded is the plan's most recent auto_renew line") → refund that line. Single reading.
- Neither depended-on rule restates the sentence; no rule carries a second wording, tool name or other policy id; no rule states an undeclared cross-problem order (the overdue/early scope pointers name the sibling rule as a pricing route, not an order — their scope defect is P-1). Base order sentences (`hosting_renewal` "the cancellation must first be withdrawn", `hosting_suspension` reactivation) ground no edge and no task rests on them (observation).

### override_declarations
Sentence-by-sentence against `base_policy_refs`:
- overdue × `hosting_renewal`: S1 "A renewal may be charged only while active or suspended" — followed (restated). S2 pricing sentence — superseded and declared. S3 "The new term length is the current one unless a scheduled term change applies, and a scheduled downgrade's target tier sets the rates…" — followed (requested term priced; downgrade plans scoped out). S4 "The new term always starts on the previous term end date, even when paid late" — followed. S5–S7 auto-renew attempts / fully declined cycle / cancel_pending — not touched; the overdue rule defines its own "fully declined cycle" with a one-calendar-month window instead of `hosting_msr_cycle_declines`' cycle window (observation O-2). overdue × `hosting_downgrade_and_term_change`: followed (scope excludes scheduled downgrades; no mid-term change).
- upgrade × `hosting_upgrade_proration`: S1 active-only, S2 upgrade_targets / effect without changing term dates — followed. S3 formula — superseded and declared (proration share per term length). S4 "new term price … less the account tier's hosting_discount_pct: intro when first term, otherwise regular, monthly for 1-month" — followed in substance (first-term test made line-based; Personal/Business 0 % matches the account parameters). S5 amount paid, S6 remaining/term days, S7 next renewal at upgraded rates — followed.
- refund × `hosting_auto_renew_refund`: "refunded in full" — superseded and declared (keep-backs). Window counting, 1-month/manual exclusion, roll-back, destination — restated. × `hosting_money_back` and × `hosting_agg_money_back_limit`: the "superseded" sentences govern money-back refunds only and never conflicted with an auto-renew refund — finding P-4.
- early × `hosting_renewal`: S2 pricing — superseded and declared. S3 "The new term length is the current one unless a scheduled term change applies" — NOT followed and NOT declared: the early rule takes the term from the line that paid the current term and ignores any scheduled term change — finding P-2. early × `hosting_downgrade_and_term_change`: "superseded" sentence restated plus a scope clause; no conflict existed — finding P-4.
- Sibling overwrites of the same base clause (overdue/early × hosting_renewal pricing sentence): each tail names the sibling, but with a scope the sibling does not have — finding P-1.

### factor_ladders
Structure only (weight per task lives in 0.md / 1.md). "Shape" = XF A6 all-pairs test.

| policy | factor | label | tiers (fall-through last) | distinct outcomes | multi-source tier | x-diff | verdict |
|---|---|---|---|---|---|---|---|
| overdue | ovr_term_tariff | method | 1-month request → monthly once; 12/24/36 request → regular rate × requested months; none → current term tariff | 2 (T1 and T2 are the one regular-tariff function of the requested term) | no | — | FAIL (F-1) |
| overdue | ovr_reseller_pct | parameter | Platinum/Gold/Silver/Bronze → that tier's hosting_discount_pct; Personal/Business → 0 | 5 | no | account | ok |
| overdue | ovr_domain_bundle | parameter | active+auto-renew on → 15; active+off → 7.5; else 0 | 3 | no (one record) | domain | ok (realism O-1) |
| overdue | ovr_mail_bundle | parameter | ≥5 seats → 20; <5 → 10; none → 0 | 3 | no | email | ok |
| overdue | ovr_late_fee | parameter | >2 days & fully declined → 10; >2 days & not → 25; ≤2 days → 0 | 3 | yes (holding term end × decline events) | — | ok (O-2, O-6) |
| upgrade | upg_reseller_pct | parameter | as ovr_reseller_pct | 5 | no | account | ok (but cross-charter P-3) |
| upgrade | upg_proration_unit | method | 24/36 → whole months / term months; 1 → whole difference; 12 → days ratio | 3 shapes (MONTHS floor; constant 1; DAYS ratio with term-days input) | no | — | ok |
| upgrade | upg_outgrown_incentive | parameter | over_limit → 10 %; warning only → 5 %; none → 0 | 3 | no | — | ok (P-3 no-compounding) |
| upgrade | upg_uptime_goodwill | parameter | >0.5 pt below SLA → 30; ≤0.5 below → 12; meets/none → 0 | 3 | no | — | FAIL realism (F-4) |
| refund | rf_processing_cost | method | card → pct × line + fixed; PayPal → flat 0.49; credit → 0 | pair PayPal/credit = constant vs constant | no | — | FAIL (F-3) |
| refund | rf_handling_age | parameter | >9 days → 19; 4–9 → 9; ≤3 → 0 | 3 | no | — | ok |
| refund | rf_change_reversal | parameter | applied term_change on period_start → 15; applied downgrade → 10; none → 0 | 3 | yes (change request × refunded line) | — | ok |
| refund | rf_commitment_share | parameter | 36 → tier monthly rate; 24 → 12; 12 → 0 | 3 | no | — | ok |
| early | early_term_source | method | paying line 1 month → monthly once; 12/24/36 → regular × line months; no paying line → billing_term_months | 2 (T1≡T2); fall-through reachable only with an incomplete ledger | no | — | FAIL (F-2) |
| early | early_reseller_discount | parameter | as ovr_reseller_pct | 5 | no | account | ok |
| early | early_advance_credit | parameter | ≥30 days & off → 20; <30 & off → 5; on → 0 | 3 | no (both fields on the holding row) | — | ok |
| early | early_cert_bundle | parameter | ov/ev → 12; dv → 6; none → 0 | 3 | no | ssl | ok (decoy P-5) |
| early | early_reliability | parameter | as upgrade, 20 / 8 / 0 | 3 | no | — | FAIL realism (F-4) |

Counts after striking failed factors: overdue 4 parameter / **0 method**; upgrade 3 parameter (one of them F-4) / 1 method; refund 3 parameter / **0 method**; early 4 parameter (one F-4) / **0 method**. Every surviving ladder has ≥3 pairwise-disjoint tiers stated in full in the rule and implemented in compute; no factor's `decides` is `result`; binding sets disjoint; no factor tier reads another factor's binding (mechanical read check: every factor binding reads only F/P/K/history/cross reads or plain bindings — XF A1 ok). Assembly sentences: one generic combination sentence per policy fixes the non-commuting order (discount → round → credits/fees → round; upgrade: discount on term price → round → minus paid × share → round → incentive % → round → fixed credit → floor) (XF A2/A5 ok). Multi-source per task: task 0 has ovr_late_fee; task 1 has rf_change_reversal. Cross-difficulty per task: task 0 account/domain/email; task 1 account/ssl.

### findings
Every item below is RED (XF_recipe membership or a demonstrated second reading) unless marked observation.

**P-1 SOURCE-POLICY — sibling overwrite tails mis-scope each other (XF C16/C17).** Bears on task 1 (demonstrated there), charter-wide otherwise.
- Overdue `replaced_by`/rule: "a renewal paid while the plan's term end date is still later than today is priced by the early renewal rule". Early rule: "This rule prices a renewal the customer pays while the plan's term end date is still later than today and which applies no scheduled downgrade request, and only such a renewal … a renewal that applies a scheduled downgrade request is never an early renewal under this rule."
- Early tail: "the renewal of a plan whose term end date is on or before today is priced by the overdue renewal rule"; overdue rule: "…which carries no scheduled downgrade request, and only such a renewal".
- Same situation, different conclusions: (a) every auto-renew charge is billed while the term end is still later than today (first attempt auto_renew_days_before_term_end before it) — overdue's text sends it to the early rule (paying-line term, reseller %, advance/certificate/reliability credits, scheduled term change ignored), early's "the customer pays" may or may not take it, early's own tail sends it to the base price; (b) a downgrade-applying renewal with term end later than today: overdue → early rule, early → "never an early renewal" → base; (c) a downgrade-applying overdue renewal: early → overdue rule, overdue → not mine → base. Neither tail excludes its sibling's case by the sibling's own scope.

**P-2 SOURCE-POLICY — early renewal departs undeclared from an in-force base sentence (XF C17).** Base `hosting_renewal`: "The new term length is the current one unless a scheduled term change applies". Not superseded by `hosting_ext_early_renewal` (its only hosting_renewal overwrite is the pricing sentence). Early rule: "The new term always starts on the previous term end date and runs for the months the early renewal is priced on" with the term "taken from the line that paid the plan's current term"; the same rule calls `billing_term_months` "the plan's current billing term length". Where billing_term_months differs from the paying line's months (the state every auto-renew refund roll-back leaves, since hosting_term_rollback does not reset billing_term_months), or a scheduled term change exists, base gives one term length and the early rule another. Demonstrated in 1.md.

**P-3 SOURCE-POLICY — upgrade percentages vs the account charter's in-force discount rules.** account_tier_benefits: "A tier discount applies to the list or renewal price component of a charge only; it never applies to … proration lines …" and "When a product's own promotion or volume discount could also apply to the same price component, only the single higher percentage applies and percentages are never added or compounded." Upgrade rule: "The Cloud 8 term price takes the reseller discount of the customer's Harborline account tier …" (the line written is charge_type upgrade_proration) and "The Cloud 8 upgrade charge carries an outgrown-plan incentive … the percentage acts on the prorated charge" — a product promotion compounded with the tier discount. (The tier-discount-on-new-term-price sentence is already in base hosting_upgrade_proration; the extended rule restates it and adds the compounding.) Demonstrated in 0.md (three readings, three numbers).

**P-4 SOURCE-POLICY — overwrites that retire nothing (XF C15).** Refund × hosting_money_back ("A money-back refund is given only for an immediate cancellation …") and × hosting_agg_money_back_limit ("A money-back refund may be given only while …"): both base sentences govern money-back refunds only and never applied to an auto-renew refund; early × hosting_downgrade_and_term_change ("A scheduled downgrade is applied at renewal only when … fit"): no conflict with an early renewal existed. Each `replaced_by` is the base sentence plus a scope remark; nothing real is retired. Charter-level, no scored consequence.

**P-5 SOURCE-POLICY — first-match / sum / max reads break on producible second records (XF B9/B10).**
- overdue `bundled_domain_status`/`_auto_renew` = CFIELD(domain, bundled_hosting_id=HID) (first match). domain_hosting_bundle: "a cancelled registration does not use up the entitlement" — a plan can carry a cancelled bundled registration and a later active one; rule "the Harborline domain registration that names this plan" presupposes one; compute returns whichever row is first (cancelled → 0 credit, active → full credit).
- early `installed_cert_level` = CPARAM(ssl, validation_level, hosting_id=HID, status=active) (first match). ssl_agg_multi_holding: "several subscriptions may cover the same name"; with an active DV and an active OV on the plan the rule's "its product's validation level" has no single referent and compute takes the first row (6 vs 12).
- upgrade `paying_line_amount` = SUM(renewal lines with period_start = term start) and early `paying_line_months` = MAX(renewal lines with period_start = term start): after an auto-renew refund followed by a manual renewal of the same period (exactly task 1's end state), both the refunded auto_renew line and its replacement carry that period_start; the rule's "the … line whose period_start equals the plan's term start date" is singular, the SUM adds the refunded line to the amount paid and the MAX picks the refunded line's months.
No seeded world of this difficulty contains the colliding pair; charter-level.

**P-6 SOURCE-POLICY — negative / zero amounts against "positive" (XF B9, D22).** Overdue result "the discounted price less every credit plus any fee, rounded half up to the cent" has no floor: a Plus plan bought on 12 months (free bundled domain, auto-renew on), with a scheduled 1-month term change, an active ≥5-seat mail subscription on its domain, renewed ≤2 days late gives 17.99 − 15.00 − 20.00 = −17.01. Early ("never below zero") gives 0.00 on a Starter 1-month term paid on its first day with auto-renew off (12.99 − 20.00 → 0.00). Upgrade 24/36-month tier gives 0.00 in a term's last month (zero whole months). hosting_charges.amount for these events is "USD, positive" and every tool docstring says "positive"; no rule tier handles the case.

**P-7 SOURCE-POLICY — world-specific text in a prerequisite declaration (check 7).** E2 `effect`: "the plan's term returns to the running term paid by the earlier 12-month line, auto-renew is switched off and the term end date is days away" — describes one task's world (a 12-month earlier line; a term end days away), not the general effect.

**F-1 SOURCE-FACTOR — ovr_term_tariff is not a method factor and its ladder has two outcomes.** Tier 1 "monthly_rate_no_commitment billed once" and tier 2 "the tier's regular rate for the requested term length times its months" are the one regular-tariff function the base states in a single clause ("renewal_rate_12mo, renewal_rate_24mo or renewal_rate_36mo times the months, or monthly_rate_no_commitment for a 1-month term") applied to the requested term; tier 3 is the same function on the current term. The tiers only substitute a different term length into one formula (parameter), and two tiers select the same method. Overdue is left with 0 method factors.

**F-2 SOURCE-FACTOR — early_term_source: same defect, plus an unreachable fall-through.** Tier 1 ≡ tier 2 (one tariff function of the paying line's term); tier 3 "no line paid the current term" holds for no plan whose ledger is complete (XF D19 — every current term has its paying line). The factor only substitutes which record supplies the term length. Early is left with 0 method factors.

**F-3 SOURCE-FACTOR — rf_processing_cost fails the all-pairs shape test (XF A6).** PayPal tier "keep back the flat paypal_reversal_fee" vs credit tier "keep back nothing": constant vs constant, no distinguishing input or operation. Refund is left with 0 method factors.

**F-4 SOURCE-FACTOR — uptime credits stacked on the SLA credit (XF D18 realism).** upg_uptime_goodwill and early_reliability credit the latest month's uptime shortfall below uptime_sla_pct; hosting_sla_credits already compensates exactly that month ("the customer may claim a service credit … for each started 0.1 percentage point of shortfall"), and neither rule excludes a month credited or creditable under it. Hosts publish SLA credits as the remedy for missed uptime; a second fixed uptime credit on an unrelated purchase for the same month is not a schedule a real host publishes (Harborline's own account_goodwill bars goodwill "for an outage already credited under a product's uptime rule"). In both worlds the latest month is below SLA and inside its SLA claim window.

**T-1 tool contracts — bodies do not enforce the docstring (XF B11).** All four write tools document `amount` as "positive" and none checks it (`_HostingCalc.cents(amount)` accepts 0 or negatives; the refund tool silently takes `abs()`); `refund_hosting_auto_renewal_84b3efde` accepts any `original_hosting_charge_id` without checking it is an auto_renew line of this plan; `bill_overdue_hosting_renewal_c53aa4e7` marks any `hosting_request_id` applied without checking it is this plan's scheduled term change.

Observations (no RED): O-1 domain-bundle credit graded by the domain's auto-renew switch is a weak pricing condition. O-2 overdue redefines "fully declined cycle" with a one-calendar-month window rather than hosting_msr_cycle_declines' cycle window; late fee also stacks on a suspended plan's reactivation_fee. O-3 refund tool fixes refund_destination=original_payment_method, so the rule's "or to account credit when the customer elects it or the charge was paid from credit" branch (always, per account_refund_credit, for credit-paid lines — common, since credit_first_for_auto_renew) has no tool realisation; no task world reaches it. O-4 DSL RND is float round(), not half-up (engine-level; no scored half cent). O-5 task 1 expired DV cert reissued 2025-04-23 vs auto-reissue day 2025-04-13 (only read as a status decoy). O-6 attempt_number = 3 on the last decline agrees with the late-fee tier (natural sequence field). O-7 uptime reports seeded only from 2026-07 (only the latest is read). O-8 `paid_for_current_term` has no compute_basis entry.

## closing_checklist
Written after both reveals (2026-10-22T15:20Z); nothing above this heading was changed after a reveal.
- Per-task files 0.md, 1.md present alongside this file; first revision (revision_1).
- Blind derivations equal GT on every write, owner, order and argument in both tasks, and prerequisite_closure / factor_sensitivity / baseline_result match figure for figure.
- Coverage: the 4 extended policies are covered; task scopes (task 0: overdue + upgrade; task 1: refund + early) pairwise disjoint; each task tool uses an independent uuid8. Both trees: 1 prerequisite problem, 1 value_input edge, one owner=user write, acyclic; whole-difficulty graph acyclic.
- NOT closed: the four relationships do not all PASS — SOURCE-POLICY RED (P-1, P-2, P-3, P-4, P-5, P-6, P-7), SOURCE-FACTOR RED (F-1, F-2, F-3, F-4), tool-contract RED (T-1). Three of four computations have no honest method factor; F-4 leaves the upgrade with 3 factors.
- Instantiation gates were not re-run by this auditor (coordinator snapshot r1 green); the difficulty does not pass the source-layer audit in revision_1.

VERDICT revision_1: task0=RED task1=RED charter=P-1,P-2,P-3,P-4,P-5,P-6,P-7,F-1,F-2,F-3,F-4,T-1

## revision_2

## charter_global_frozen
- Frozen 2026-10-22 (revision_2), before any revision_2 task GT was revealed. Auditor: same independent auditor; revision_1 text above left untouched.
- Entry: `tail -n 1 tasks/hosting_plans_and_billing/worklog.md` = "REWORK round 2: gates 7/7 green". Gate snapshot run by this auditor (execute-only): `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r2.txt` — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Hashes (changed since revision_1, so every charter-global section is re-derived): hosting.extended.yaml d6c73c4037f171433709853bd5c140ad177eef5ff810abe45e6ac4a47374b3a7; task_tools.py bca142a98212c9660bac6737196d561907e6f947447e83fee7f27942e7fe0b55; 0.view.json 48d08a26…75f3; 1.view.json 78622eaf…75b9. Base section (lines 1–1619) still byte-identical to products/hosting.yaml.
- Also read: `audits/render_source/owner_ruling.md` (coordinator ruling on owner=user writes). The worklog's "REWORK round 2 claims" section was NOT read before the freeze (read only after both task derivations were frozen).

### policy_conflict_scan (r2)
- Owners now: overdue renewal (bill_overdue…c53aa4e7) owner=user, upgrade owner=user, refund owner=agent, early renewal owner=user. Both renewal rules and the upgrade rule state "the account holder's own payment, completed at Harborline's checkout after the agent quotes the amount, because Harborline support never takes payment details" — ruling (b) satisfied at charter level (no base hosting sentence assigns renewal/upgrade billing to the agent; the rule states the checkout act). Persona necessity is judged per task.
- Renewal split: overdue = checkout renewal, term end on or before today, no scheduled downgrade; early = checkout renewal, term end later than today, no scheduled downgrade or term change; both tails name the sibling with the sibling's own scope and send auto-renew charges, downgrade-applying renewals and term-change plans paying early to the base price. Closed and consistent (P-1 closed). Residual wording: the tails' "every other renewal, which is …" enumeration omits a plan carrying a scheduled downgrade that does not fit; that case still lands on the base price uniquely (observation O-10).
- Cross-category boundaries: account (variant_name) ×3; domain (status/auto_renew/bundled_hosting_id) in both renewals, domain (nameservers/status/domain_name) in upgrade; email ×2 renewals; ssl ×2 renewals. Upgrade percentages vs account_tier_benefits: the outgrown-plan adjustment is now a fixed credit and the rule states the tier discount acts only on the list-price component and "no tier discount or other percentage is ever applied to the prorated line itself" — no second reading left (P-3 closed).
- Scope exclusivity unchanged: task 0 {upgrade, overdue}, task 1 {early, refund}.

### rule_compute_equivalence (r2)
- Mechanical sweep: every compute_basis verbatim in its rule; every baseline sentence in the rule; every replaced_by in the rule; every binding has a basis; both prerequisite sentences verbatim, gates are real bindings (`prorated_upgrade_share`, `early_new_term_months`).
- Branch check per policy: overdue (term from scheduled request else billing_term_months; discount; domain/mail/cert credits; late fee three tiers; credit cap at half the discounted price) — rule = compute. Upgrade (paying line = latest renewal line at the term start else initial_term; first-term test; discount on list price; 24/36 months-with-≥1-month / 1-month / days share; outgrown credit capped at half; DNS move fee) — rule = compute except the same-day tie below. Refund (latest auto_renew line; processor pct; handling age; reversal; commitment share; floor) — rule = compute. Early (billing_term_months; discount; advance credit three tiers; domain/mail/cert; cap) — rule = compute.
- Same-day tie (XF B9/B10, residue of P-5): upgrade `latest_renewal_line` = LATEST(renewal lines, period_start = term start) by charge_date (date-only); the rule justifies the pick with "(a refunded line is always older than the line that replaced it)". A refund window includes the auto-renew charge date itself, so an auto-renew line refunded and replaced by a checkout renewal on the same calendar day ties on charge_date; LATEST keeps the first row met (the refunded line) and the rule's assertion is false on that day.

### action_binding_and_uuids (r2)
- (target_tool, computes) pairs unchanged and unique; uuid8s unchanged (c53aa4e7, 8645a072, 84b3efde, 31233d6b), distinct, no factor id ⊂ tool name; no ordering words or example values in docstrings; no composite args; each write tool calls ctx.create/update itself.
- T-1 closed: all four bodies reject a non-positive cent amount; refund rejects a line that is not an auto_renew renewal line of this plan; bill_overdue rejects a request id that is not a scheduled term_change of this plan. These are argument checks, none tests a prerequisite state (term dates are never inspected).
- Refund body now restores billing_term_months from the earlier paying line (rule: "rolls the plan back to the term paid before it, meaning that term's start date, end date and billing term length"); base event hosting_term_rollback lists only term dates and auto_renew (observation O-9). Refund destination still fixed to original_payment_method (O-3 stands).
- Trigger rule: unchanged, no cross-category write.

### prerequisite_graph / prerequisite_sentences (r2)
- E1 unchanged (state form, "only after", unique writer = overdue renewal); effect text now general. E2 unchanged sentence; gate `early_new_term_months`; effect now general ("returns to the term paid before it, with that term's end date and billing term length and with auto-renew switched off") — P-7 closed. Graph acyclic; no undeclared cross-problem order; depended-on rules do not restate the sentences.

### override_declarations (r2)
- overdue × hosting_renewal: pricing sentence superseded and declared; "The new term length is the current one unless a scheduled term change applies" now restated verbatim in substance; downgrade plans scoped out. Clean.
- early × hosting_renewal: pricing superseded; term length = billing_term_months with term-change plans out of scope — follows the base sentence (P-2 closed).
- early × hosting_downgrade_and_term_change: replaced_by = base sentence + "which concerns only a renewal that applies a scheduled downgrade request and therefore never an early renewal". The base gate `downgrade_fits` speaks only of a scheduled downgrade being applied; an early renewal (scoped to plans with no scheduled downgrade) never met it, so this overwrite still retires nothing (XF C15) — P-4 residue, this member only.
- refund × hosting_money_back / × hosting_agg_money_back_limit: re-judged in revision_2 — the base eligibility entries `money_back_window` and `money_back_quota` both declare `applies_to: [hosting_refund]`, i.e. every hosting_refund event including an auto-renew refund, so these overwrites do retire a real application. Revision_1's P-4 call on these two members is withdrawn as over-called.
- upgrade × hosting_upgrade_proration: formula superseded; the base "amount paid … the … line whose period_start equals the plan's term start date" is refined to "the most recently charged" one (disambiguation, observation O-11).

### factor_ladders (r2)
| policy | factor | label | tiers | verdict |
|---|---|---|---|---|
| overdue | ovr_reseller_pct | parameter | 4 reseller tiers / 0 | ok, x-diff account |
| overdue | ovr_domain_bundle | parameter | active on 15 / active off 7.5 / 0 | ok, x-diff domain (O-1 stands) |
| overdue | ovr_mail_bundle | parameter | ≥5 seats 20 / <5 10 / 0 | ok, x-diff email |
| overdue | ovr_cert_bundle | parameter | any OV/EV 12 / all DV 6 / 0 | ok, x-diff ssl |
| overdue | ovr_late_fee | method | per-day × days past end / pct × regular price / none | ok (shapes differ in inputs and operation); multi-source (term end × decline events) |
| upgrade | upg_reseller_pct | parameter | as above | ok |
| upgrade | upg_proration_unit | method | months ratio (≥1 month left) / whole difference / days ratio | ok |
| upgrade | upg_outgrown_credit | parameter | over_limit 40 / warning 20 / 0 (cap half) | ok |
| upgrade | upg_dns_move_fee | parameter | Harborline reg. on external NS 15 / no active Harborline reg. 25 / Harborline DNS 0 | FAIL N-1 |
| refund | rf_processor_fee | parameter | card 2.9 % / PayPal 3.49 % / credit 0 | ok |
| refund | rf_handling_age | parameter | >9 days 19 / 4–9 9 / ≤3 0 | ok |
| refund | rf_change_reversal | parameter | applied term change 15 / applied downgrade 10 / 0 | ok, multi-source |
| refund | rf_commitment_share | method | 36: one month at tier monthly rate / 24: 12 × (r12 − r24) / 12: none | ok (all-pairs: tariff input vs difference operation vs nothing) |
| early | early_reseller_discount | parameter | as above | ok |
| early | early_advance_credit | method | off & ≥30 days: 2.00 × whole months / off & <30 days: daily 12-month price × days / on: none | FAIL N-2 |
| early | early_domain_bundle / early_mail_bundle / early_cert_bundle | parameter | as overdue | ok |
Counts (struck factors removed): overdue 4 parameter + 1 method = 5 ✓; upgrade 2 parameter + 1 method = 3 (< 4) ✗; refund 3 parameter + 1 method ✓; early 4 parameter + 0 method ✗. Caps MN(credits, half price) are plain assembly in `result`, stated once generically (XF A2/A5 ok); T1/T2 judged per task. Factor independence: no factor binding reads another factor's binding (credits_total/cap are plain).

### findings (r2)
Closed since revision_1: P-1, P-2, P-3, P-6, P-7, F-1, F-2, F-3, F-4, T-1 (evidence above). Withdrawn: P-4's refund members.
Open / new:
- **P-4 (residue) SOURCE-POLICY** — early × hosting_downgrade_and_term_change overwrite retires nothing (XF C15).
- **P-5 (residue) SOURCE-POLICY** — upgrade paying-line LATEST ties on a same-day refund-and-replace; the rule's "(a refunded line is always older than the line that replaced it)" is false on that day and the read keeps the refunded line (XF B9/B10, B13).
- **N-1 SOURCE-FACTOR / SOURCE-POLICY** — `upg_dns_move_fee`: the rule's framing "The move to the larger cloud server changes the plan's dedicated IP address" is a fact no record and no base sentence holds (both Cloud tiers carry dedicated_ip true; hosting_upgrade_proration says the upgrade takes effect without changing term dates and hosting_inclusions says resources apply when the tier takes effect — nothing about an IP move) (XF B13); and the fee charges the customer for keeping DNS elsewhere — more (25) when the domain is not registered with Harborline at all than when it is registered here on external nameservers (15), i.e. graded by registrar, not by any work Harborline performs. No host publishes an upgrade surcharge for the customer's own choice of DNS host or registrar (XF D18). Upgrade left with 3 factors.
- **N-2 SOURCE-FACTOR** — `early_advance_credit` <30-day tier credits "one day of the tier's 12-month regular price … for each of those days" — the value of the days still left on the running term, which the customer keeps anyway because the new term "always starts on the previous term end date"; the credit for paying 29 days early is a month's worth of service while 30 days early earns early_credit_per_month × 1. A host does not refund days it still delivers, and no published early-payment schedule falls by an order of magnitude when paying one day earlier (XF D18; unreal tier outcome). Early left with 0 method factors.
- **N-3 SOURCE-FACTOR (task 1 seed, XF D19)** — demonstrated in 1.md: the seeded .ca registration is a free hosting-bundle registration on a TLD whose `free_with_hosting_eligible` is false.
Observations: O-1, O-2, O-3, O-4, O-5 (task 1 expired DV), O-9 (rollback writes billing_term_months beyond hosting_term_rollback's listed fields), O-10 (tail enumeration), O-11 (paying-line disambiguation), O-12 ("as the hosting upgrade rule states" appeal; content stated in full).

## closing_checklist (r2)
Written after both r2 reveals (2026-10-22T17:10Z); the r2 charter-global sections above were frozen before them.
- Blind r2 derivations equal GT in both tasks on every write, owner, order, argument, prerequisite_closure and factor figure.
- Reworker claims (worklog "REWORK round 2 claims", read after the freeze) checked item by item: P-1, P-2, P-3, P-6, P-7, F-1, F-2, F-3, F-4, T-1 verified closed. P-4: the claim that `downgrade_fits` applies_to every hosting_term_renew row is correct (its eligibility entry lists applies_to [hosting_term_renew]), the same structural ground on which the refund members were accepted above; for consistency the early × hosting_downgrade_and_term_change member is also withdrawn — P-4 closed in full. (This is a re-judgement of the charter on the reworker's stated ground, not on any GT value.) P-5: domain/cert/early-MAX members closed; the upgrade same-day tie member remains.
- Final sweep of every class raised in r1/r2 across all four policies: sibling tails (closed); undeclared base departures (none beyond observations O-9, O-11); empty overwrites (none after re-judgement); cross-charter percentages (none); first-match/latest/sum decoys (only the upgrade same-day tie); zero/negative amounts (closed — caps keep every result positive); method shape (4 method factors pass); world-specific prerequisite text (closed); tool contracts (closed); realism of every factor (N-1, N-2 fail; O-1, O-2 observations); cross-category seed producibility (task 0 clean; task 1 .ca bundle fails — N-3); owner=user per ruling (all three user writes accepted).
- Coverage, scope disjointness, uuid8s, tree shapes (1 prerequisite, 1 value_input, user write, acyclic) hold. Factor bounds fail: upgrade 3 surviving factors (N-1), early 0 surviving method factors (N-2).
- Gates: coordinator-format snapshot r2 run by this auditor, 7/7 OK. The difficulty does not pass the source-layer audit in revision_2.

VERDICT revision_2: task0=RED task1=RED charter=P-5,N-1,N-2,N-3

## revision_3

## charter_global_frozen (r3)
- Frozen before any revision_3 GT reveal; revision_1/2 text untouched. Entry: worklog tail "REWORK round 3: gates 7/7 green"; snapshot run by this auditor (execute-only) → `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r3.txt`: 7/7 OK.
- Hashes: hosting.extended.yaml aed44454…0fdaf (changed → charter sections re-derived); task_tools.py bca142a9…0b55 (unchanged since r2 → action_binding_and_uuids (r2) carried forward by reference); 0.view 48d08a26…75f3 (unchanged since r2); 1.view c92b7385…fc19 (changed → task 1 re-derived from the rebuilt view). Base section still byte-identical. Copies kept in `/tmp/audit_hosting_plans_and_billing_0076/ext_r3.yaml`, `tools_r3.py`. Worklog "REWORK round 3 claims" not read before the freeze.

### changes found (r3 vs r2)
- Upgrade: `upg_dns_move_fee` and its framing sentence removed; new `upg_welcome_credit` (no upgrade_proration line ever → first_upgrade_credit; only earlier-term lines → returning_upgrade_credit; a line in the current term → none), joined to the outgrown credit under the half-of-prorated cap; paying line now = checkout `renewal` line at the term start, else `auto_renew` line, else `initial_term`, with the justification "(a refunded line is always an auto_renew line, because a renewal the customer paid manually is never refundable)".
- Overdue and early: domain bundle credit re-written as a `method` factor: auto-renew on → "the TLD's renewal_price plus its icann_fee_per_year"; auto-renew off → "the TLD's renewal_price alone, without the ICANN fee"; none → 0, framed "because Harborline credits the yearly renewal of a plan's bundled domain against the hosting renewal (the domain itself is still billed at its normal renewal price under the domain charter)". Domain cross reads add renewal_price, icann_fee_per_year.
- Early: `early_advance_credit` is now a parameter (off & ≥30 days → early_credit_long; off & <30 → early_credit_short; on → 0); early's only method factor is now `early_domain_bundle`.

### policy_conflict_scan / rule_compute_equivalence / prerequisites / overrides (r3)
- Renewal split tails, owner statements, prerequisite sentences/edges/effects, override declarations: textually unchanged from r2 → r2 conclusions carried (P-1, P-2, P-3, P-4, P-6, P-7 remain closed).
- Mechanical sweep r3: all compute_basis verbatim, baseline sentences in rule, replaced_by in rule, every binding has a basis, prerequisite sources verbatim, gates real.
- Rule = compute in every branch of the changed bindings (paying-line priority; welcome-credit ladder; domain credit ladder via CPARAM(domain, renewal_price / icann_fee_per_year, bundled_hosting_id=HID, status=active); advance credit).
- P-5 residue re-checked: with checkout `renewal` lines preferred over `auto_renew` lines, the refund-and-replace pair resolves to the replacement regardless of dates; two `auto_renew` lines can share a period_start only if a refunded one is followed by a fresh auto-renew attempt, which runs on a later attempt day than the refunded charge (one attempt per day; the refund follows the charge), so LATEST by charge_date is unambiguous; a refunded initial_term (money-back / failed order) leaves the plan cancelled, so no upgrade reads it. P-5 closed.
- Cross-charter: domain_hosting_bundle "Renewals of a bundled domain are billed at the normal renewal price" — the credit lands on the hosting line, the domain line stays at the domain price; no literal conflict (observation O-13: economic offset of that sentence).

### factor_ladders (r3)
| policy | factor | label | verdict |
|---|---|---|---|
| overdue | ovr_reseller_pct, ovr_mail_bundle, ovr_cert_bundle | parameter | ok |
| overdue | ovr_domain_bundle | method | FAIL N-4 |
| overdue | ovr_late_fee | method | ok, multi-source |
| upgrade | upg_reseller_pct / upg_outgrown_credit | parameter | ok |
| upgrade | upg_proration_unit | method | ok |
| upgrade | upg_welcome_credit | parameter | ok — 3 disjoint tiers on the plan's upgrade history, distinct values; a first-upgrade promotion is a real host practice |
| refund | rf_processor_fee, rf_handling_age, rf_change_reversal | parameter | ok |
| refund | rf_commitment_share | method | ok |
| early | early_reseller_discount, early_mail_bundle, early_cert_bundle | parameter | ok |
| early | early_advance_credit | parameter | ok — 10 / 4 / 0 flat schedule (N-2 closed) |
| early | early_domain_bundle | method | FAIL N-4 |
Counts after striking: overdue 3 parameter + 1 method = 4 ✓; upgrade 3 + 1 = 4 ✓; refund 3 + 1 ✓; early 4 parameter + **0 method** ✗.

### findings (r3)
Closed this round: N-1 (DNS fee and its framing removed), N-2 (advance credit flat schedule), P-5 (paying-line priority). N-3: see 1.md (rebuilt seed).
- **N-4 SOURCE-FACTOR — the domain bundle credit ladder (ovr_domain_bundle, early_domain_bundle).** (a) Label: tier 1 "renewal_price plus its icann_fee_per_year" and tier 2 "renewal_price alone, without the ICANN fee" are one formula with the ICANN term multiplied by 1 or 0 — a 0/1 multiplier substituting a number, not a change of method (XF A6 constant multipliers ignored); for every TLD whose icann_fee_per_year is 0 (.us, .ca, .co, .io) the two tiers give the same value. (b) Realism: whether a registry fee is passed through in a hosting credit is made to depend on the domain's auto-renew switch — a condition no host weighs for that quantity (XF D18). (c) Framing (XF B13): "Harborline credits the yearly renewal of a plan's bundled domain" — the credit is the TLD list price, not the yearly renewal the domain charter bills this customer (the renewal_price component is reduced by the account tier's domain_renewal_discount_pct; a Bronze .com renewal is billed 17.64 while the credit is 18.18), so the stated basis is not what any record shows. Consequence: early renewal has no honest method factor; both renewal computations carry an unreal tier.
Observations carried: O-1 superseded by N-4; O-2, O-3, O-4, O-9, O-10, O-11, O-12; new O-13.

## closing_checklist (r3)
Written after both r3 reveals (2026-10-22T18:18Z).
- Blind r3 derivations equal GT in both tasks on every write, owner, order, argument, prerequisite_closure and factor figure.
- Reworker claims (read after the freeze) checked: P-5, N-1, N-2, N-3 verified closed; revision-1 items re-checked, none reopened. Disputed: the claim that no rule sentence asserts an unrecorded fact and that every method factor has distinct inputs per pair — N-4 (domain bundle credit framing, 0/1 ICANN multiplier, auto-renew condition).
- Final sweep of every class raised in r1–r3 across all four policies: sibling tails (closed); undeclared base departures (none); empty overwrites (none); cross-charter percentages (none); first-match/latest/sum decoys and same-day ties (closed); zero/negative amounts (closed); method shape (late fee, proration, commitment pass; both domain bundle factors fail); world-specific prerequisite text (closed); tool-body contracts (closed, tools unchanged); realism (only the domain bundle ladder fails); framing clauses (only the domain bundle "credits the yearly renewal"); cross-category seed producibility (both tasks clean); owner=user per ruling (accepted); uptime/SLA stacking (gone).
- Factor bounds: overdue 4 surviving (1 method) ✓, upgrade 4 ✓, refund 4 ✓, early 0 method ✗. Coverage, scope disjointness, uuid8s, tree shapes hold. Gates 7/7 OK (snapshot r3).

VERDICT revision_3: task0=RED task1=RED charter=N-4

## revision_4

## charter_global_frozen (r4)
- Frozen before any revision_4 GT reveal; earlier revisions untouched. Entry: worklog tail "REWORK round 4: gates 7/7 green"; snapshot run by this auditor → `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r4.txt`: 7/7 OK.
- Hashes: hosting.extended.yaml 35c3e348…01aa (changed; copy `/tmp/audit_hosting_plans_and_billing_0076/ext_r4.yaml`); task_tools.py bca142a9… (unchanged since r2; diff against tools_r3.py empty → action_binding_and_uuids (r2) carried); 0.view 48d08a26… and 1.view c92b7385… unchanged since r3 (worlds unchanged; only the charter-dependent figures are recomputed). Worklog "REWORK round 4 claims" not read before the freeze.

### changes found (r4 vs r3) — `diff ext_r3.yaml ext_r4.yaml`
Only the domain bundle credit of the overdue and early rules changed: rule sentence now "because Harborline credits the bundled domain's yearly renewal against the hosting renewal (the domain itself is still billed under the domain charter): a bundled registration that has been renewed is credited the amount of its most recent domain renewal charge line, as the domain charter billed it; a bundled registration still in its free first year, with no renewal charge yet, is credited its TLD's renewal_price; …"; compute = XLATEST(domain, domain_charges, amount, charge_date, domain_id = bundled active registration, event_type domain_renewal_charge), else CPARAM renewal_price, else 0; cross reads domain_id / domain_charges.amount; factor ladders updated; inputs list the domain_charges history. Everything else byte-identical → all other r3 conclusions carried (P-1…P-7, F-1…F-4, T-1, N-1, N-2, N-3, P-5 closed).

### rule_compute_equivalence (r4)
- Sweep: compute_basis verbatim, baseline sentences in rule, every binding has a basis (bad = 0). Rule = compute on the two stated tiers and the fall-through.
- Edge / decoy probes of the new read (XF B9/B10), against the domain charter's own producible records:
  - multi-year line: domain_renewal_pricing bills "the TLD's renewal_price per year renewed plus the icann_fee_per_year per year" and allows renewals up to max_registration_years (10); a bundled .com renewed manually for 2 years carries one domain_renewal_charge line of about two years' price. The framing says Harborline credits "the bundled domain's yearly renewal"; the specific clause credits "the amount of its most recent domain renewal charge line". Reading 1: the whole multi-year line; reading 2: the yearly renewal (line ÷ years). Two numbers, no rule sentence picks.
  - refunded line: domain_refunds allows an auto-renew charge to be refunded within auto_renew_refund_days (30 for .com); the refund is a separate `domain_refund` row and the original `domain_renewal_charge` line stays. XLATEST still returns the refunded line's amount, so a renewal the customer got back is credited as "the bundled domain's yearly renewal … as the domain charter billed it".
  - restore line: a redemption restore is billed as `domain_restore_charge` ("Renewal years included"); the read ignores it and credits the older renewal line, although the restore is the domain's most recent renewal as billed.
  No member occurs in either task world (both bundled .com domains carry only 1-year auto_renew lines, none refunded or restored).

### factor_ladders (r4)
- ovr_domain_bundle / early_domain_bundle (method): tier 1 = a ledger read (latest renewal line amount), tier 2 = a tariff parameter (TLD renewal_price), fall-through none — distinct inputs per pair, label honest; the auto-renew condition is gone; the framing now matches the billed amount for a 1-year line. Realism: crediting a bundled domain's renewal against the hosting renewal (a free domain for as long as the plan is kept) is a real host practice. Structure passes; the read's edge members are recorded under N-5.
- Counts: overdue 4 parameter + 2 method; upgrade 3 + 1; refund 3 + 1; early 4 + 1 — all within bounds.

### findings (r4)
- N-4 closed (all three parts: label, auto-renew/ICANN condition, framing vs billed amount).
- **N-5 SOURCE-POLICY (new, XF B9/B10/B13)** — both renewal rules' domain bundle read: multi-year renewal lines (whole line vs the "yearly renewal" the framing names), refunded renewal lines (still credited), and restore lines carrying the renewal year (ignored) — each a producible domain-charter record on which the rule's framing and its compute-backed clause give different credits. Charter-level; no task-world consequence.

## closing_checklist (r4)
Written after both r4 reveals (2026-10-22T18:43Z).
- Blind r4 derivations equal GT in both tasks on every write, owner, order, argument, prerequisite_closure and factor figure; both tasks PASS all four relationships on their own worlds.
- Reworker claims (read after the freeze): N-4 verified closed. Their probes (free first year, non-bundled domain, cancelled/deleted decoys, absent) do not cover multi-year, refunded or restore lines — N-5.
- Final sweep of every class raised in r1–r4 across all four policies: sibling tails, base departures, overwrites, cross-charter percentages, paying-line and other first-match/latest reads, zero/negative amounts, method shapes (late fee, both domain bundles, proration, commitment pass), prerequisite text, tool contracts, realism, framing, seed producibility, owner ruling — only the domain bundle read's edge members (N-5) remain.
- Coverage, scope disjointness, uuid8s, tree shapes and factor bounds (overdue 5, upgrade 4, refund 4, early 5; each ≥1 method, ≥2 parameter; per task multi-source and cross-difficulty) hold. Gates 7/7 OK (snapshot r4). The difficulty is not closed while N-5 stands.

VERDICT revision_4: task0=PASS task1=PASS charter=N-5

## revision_5

## charter_global_frozen (r5)
- Frozen before any revision_5 GT reveal; earlier revisions untouched. Entry: worklog tail "REWORK round 5: gates 7/7 green"; snapshot run by this auditor → `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r5.txt`: 7/7 OK.
- Hashes: hosting.extended.yaml 9fa883f4…1c91 (changed; copy ext_r5.yaml); task_tools.py bca142a9… (unchanged; diff vs tools_r3.py empty → r2 tool section carried); 0.view 48d08a26… and 1.view c92b7385… unchanged since r3. Worklog "REWORK round 5 claims" not read before the freeze.

### changes found (r5 vs r4) — `diff ext_r4.yaml ext_r5.yaml`
Only the domain bundle credit of the overdue and early rules: framing "credits one year of the bundled domain's renewal"; tier 1 "when the registration's most recent domain renewal charge line carries no refund and no restore charge line is dated later than it, the credit is that line's amount divided by the years it renewed, as the domain charter billed it"; tier 2 "any other active bundled registration (free first year, latest renewal refunded, or restored after that line) is credited its TLD's renewal_price"; fall-through none. Compute adds XLATEST years / id / date of the latest renewal line, XCOUNT of domain_refund rows pointing at it, XLATEST restore date; credit = RND(amount / years, 2). Everything else byte-identical → all other r4 conclusions carried.

### rule_compute_equivalence (r5)
- Sweep: compute_basis verbatim, every binding has a basis (bad = 0).
- N-5 members re-probed: multi-year line → divided by its years ✓ (rule = compute); refunded latest line → detected by the refund row's original_domain_charge_id, falls to list price ✓; later restore line → falls to list price ✓ (same-day restore counts as "not later", consistent with "dated later than it"). N-5 closed.
- New edge members of the same read (XF B9 / B11):
  - rounding: compute rounds the per-year share, `RND(bundled_last_renewal / bundled_last_renewal_years, 2)` (and the early twin); the rule states no rounding for "that line's amount divided by the years it renewed" — its only rounding sentence is the final "rounded half up to the cent" of the whole amount. Where the per-year share falls exactly on a half cent the two placements differ by one cent (and RND is float round(), not half-up — O-4).
  - same-day tie: the domain charter lets a bundled domain carry two renewal lines dated the same day (an auto-renew charge and a manual renewal of further years on that day); "the registration's most recent domain renewal charge line" does not say which of them is meant, and XLATEST keeps the first row met. When one of the two is later refunded (manual renewals are refundable within renewal_refund_days), the pick decides between the per-year tier and the list-price tier.
  Neither member occurs in either task world (each bundled .com has two 1-year auto_renew lines on distinct dates, no refund, no restore; 17.64 / 1 is exact).

### factor_ladders (r5)
- ovr_domain_bundle / early_domain_bundle (method): ledger per-year share / tariff parameter / none — distinct inputs and operations per pair, honest label, real practice. Counts unchanged (overdue 5, upgrade 4, refund 4, early 5; each ≥ 1 method).

### findings (r5)
- N-5 closed.
- **N-6 SOURCE-POLICY (XF B9/B11)** — domain bundle per-year credit (both renewal rules): rounding of "that line's amount divided by the years it renewed" stated nowhere in the rule while compute rounds it; same-day tie between two renewal lines of the bundled domain unstated. Charter-level; no task-world consequence.

## closing_checklist (r5)
Written after both r5 reveals (2026-10-22T19:04Z).
- Blind r5 derivations equal GT in both tasks; both tasks PASS all four relationships.
- Reworker claims (read after the freeze): N-5 verified closed (multi-year, refunded, restore and decoy probes match the rule). Not covered by their probes: per-year rounding placement and a same-day pair of renewal lines — N-6.
- Final sweep of every class raised in r1–r5 across all four policies: sibling tails, base departures, overwrites, cross-charter percentages, first-match/latest reads and same-day ties (only the domain renewal-line tie, N-6), rounding placement (only the per-year domain share, N-6; every other RND in the four computes has its rounding sentence), zero/negative amounts, method shapes, prerequisite text, tool contracts, realism, framing, seed producibility, owner ruling — nothing else open.
- Coverage, scope disjointness, uuid8s, tree shapes, factor bounds hold; gates 7/7 OK (snapshot r5). Not closed while N-6 stands.

VERDICT revision_5: task0=PASS task1=PASS charter=N-6

## revision_6

## charter_global_frozen (r6)
- Frozen before any revision_6 GT reveal; earlier revisions untouched. Entry: worklog tail "REWORK round 6: gates 7/7 green"; snapshot run by this auditor → `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r6.txt`: 7/7 OK.
- Hashes: hosting.extended.yaml ab2792e1…cd0e (changed; copy ext_r6.yaml); task_tools.py bca142a9… (unchanged; r2 tool section carried); 0.view 48d08a26… and 1.view c92b7385… unchanged since r3. Worklog "REWORK round 6 claims" not read before the freeze.

### changes found (r6 vs r5) — `diff ext_r5.yaml ext_r6.yaml`
1. Domain bundle credit (overdue, early): tier 1 now requires the latest renewal line to be "the only renewal charge line on its charge date" and states "rounded half up to the cent" for the per-year share; two or more renewal lines on that date fall to the list-price tier. Compute adds XCOUNT of renewal lines on that charge_date.
2. Upgrade (not requested by any r5 finding): the reseller discount is removed — new second overwrite of hosting_upgrade_proration, superseded "The new term price is the target tier's rate for the current term length times its months, less the account tier's hosting_discount_pct: …", replaced_by "The new term price is the target tier's rate for the current term length times its months, with no account tier discount, because the account charter never applies a tier discount to proration lines: …"; `upg_reseller_pct` deleted, `cloud8_term_price` = RND(list price); new factor `upg_mail_bundle` (≥ mail_large_min_seats → 20, fewer → 10, none → 0) joins the half-of-prorated credit cap; upgrade cross_category now email only.

### rule_compute_equivalence (r6)
- Sweep: compute_basis verbatim, replaced_by in rule, every binding has a basis (bad = 0).
- N-6 members: per-year rounding now stated and placed as computed ✓ (RND float vs half-up remains the engine-level O-4); same-day pair → list-price tier, stated and computed (XCOUNT on the latest charge_date) ✓. N-6 closed.
- Upgrade: rule = compute on the discount-free term price, mail credit tiers, cap.

### override_declarations (r6) — new upgrade overwrite
- The superseded sentence genuinely conflicted with account_tier_benefits ("it never applies to … proration lines"), so the overwrite retires something real. But its `replaced_by` carries no scope: the policy's first sentence says "This rule prices the upgrade of a Harborline Cloud 4 plan to Harborline Cloud 8, and only such an upgrade", yet the second replaced_by restates the new term price for every upgrade "with no account tier discount". For an out-of-scope upgrade (e.g. Starter → Plus on a Reseller Bronze account) the base policy hosting_upgrade_proration still carries, un-retired, `params.new_term_price: target tier rate for the current term length times its months, less the account tier hosting discount`, while the merged rule now says "with no account tier discount" — two in-force passages of the charter, two different upgrade charges for the same world (XF C15: a replaced_by restates in-force content for out-of-scope cases and names its own scope; XF C17).

### factor_ladders (r6)
- Upgrade: upg_proration_unit (method), upg_outgrown_credit, upg_welcome_credit, upg_mail_bundle (parameter, x-diff email; 3 disjoint tiers on the email subscription of the primary domain) → 4 factors ✓. Domain bundle factors unchanged in shape (method, honest). Counts: overdue 5, upgrade 4, refund 4, early 5; each ≥ 1 method, ≥ 2 parameter.
- Mail bundle credit now granted on both the overdue renewal and the upgrade for the same subscription (observation O-14: per-charge bundle credits, a business choice, no conflicting sentence).

### findings (r6)
- N-6 closed.
- **N-7 SOURCE-POLICY (XF C15/C17)** — the new unscoped upgrade overwrite (above): reaches upgrades this policy says it does not price and leaves the base `params.new_term_price` description ("less the account tier hosting discount") in force against it. Charter-level; no task-world consequence (task 0's upgrade is in scope and the extended rule governs it).

## closing_checklist (r6)
Written after both r6 reveals (2026-10-22T19:23Z).
- Blind r6 derivations equal GT in both tasks; both tasks PASS all four relationships.
- Reworker claims (read after the freeze): N-6 verified closed. The account_tier_benefits change is called "a scoped overwrite", but its replaced_by names no scope and leaves the base params description in force against it — N-7.
- Final sweep of every class raised in r1–r6 across all four policies: sibling tails, base departures (only N-7), overwrites (only N-7), cross-charter percentages (none — renewals discount the renewal component only; upgrade now takes none), first-match/latest reads and ties, rounding placement, zero/negative amounts, method shapes, prerequisite text, tool contracts, realism, framing, seed producibility, owner ruling — nothing else open.
- Coverage, scope disjointness, uuid8s, tree shapes, factor bounds hold; gates 7/7 OK (snapshot r6). Not closed while N-7 stands.

VERDICT revision_6: task0=PASS task1=PASS charter=N-7

## revision_7

## charter_global_frozen (r7)
- Frozen before any revision_7 GT reveal; earlier revisions untouched. Entry: worklog tail "REWORK round 7: gates 7/7 green"; snapshot run by this auditor → `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r7.txt`: 7/7 OK.
- Hashes: hosting.extended.yaml 9e189402…a86f (changed; copy ext_r7.yaml); task_tools.py bca142a9… (unchanged); 0.view 48d08a26… and 1.view c92b7385… unchanged. Worklog "REWORK round 7 claims" not read before the freeze.

### changes found (r7 vs r6) — `diff ext_r6.yaml ext_r7.yaml`
Only the upgrade's second overwrite of hosting_upgrade_proration (replaced_by, the matching rule sentence and the `cloud8_term_price` basis): "For every upgrade other than the Cloud 4 to Cloud 8 upgrade this rule prices, the new term price is the target tier's rate for the current term length times its months, less the account tier's hosting_discount_pct, as the hosting upgrade rule and its new_term_price parameter state: …; for the Cloud 4 to Cloud 8 upgrade this rule prices, the Cloud 8 term price takes no account tier discount and its new_term_price parameter description does not apply, because the account charter never applies a tier discount to proration lines." Compute unchanged.

### override_declarations / rule_compute_equivalence (r7)
- Sweep bad = 0. The replaced_by now restates the in-force base content (discounted new term price, matching base `params.new_term_price`) for every out-of-scope upgrade and names its own scope (Cloud 4 → Cloud 8, no tier discount, the params description declared inapplicable there). The out-of-scope world of revision_6 (Starter → Plus, Reseller Bronze) now reads one discounted price from both the base params and the merged rule. N-7 closed (XF C15/C17).
- Residual, base-level (observation O-16): for out-of-scope upgrades the base hosting charter's own "less the account tier's hosting_discount_pct" still stands against account_tier_benefits "it never applies to … proration lines"; that conflict is between two blueprint product charters, predates this difficulty, is restated here verbatim in substance as XF C15 requires, and reaches no world this difficulty prices. Routed as a blueprint-level note, not a RED of this difficulty.

### factor_ladders / findings (r7)
- Factors unchanged from r6 (overdue 5, upgrade 4, refund 4, early 5; each ≥ 1 method, ≥ 2 parameter; per task multi-source and cross-difficulty present).
- N-7 closed. No new finding.

## closing_checklist (r7)
Written after both r7 reveals (2026-10-22T22:06Z).
- Per-task files 0.md / 1.md correspond to the two tasks, each revision appended in order (revision_1 … revision_7), every comparison section of revision_7 PASS.
- The 4 extended policies are covered; scopes pairwise disjoint (task 0: overdue + upgrade; task 1: refund + early); task tools closed, uuid8s independent (c53aa4e7, 8645a072, 84b3efde, 31233d6b).
- Both trees: 1 prerequisite problem, 1 value_input edge (state form, own-rule prerequisite sentence), owner=user writes accepted under the coordinator ruling, acyclic; whole-difficulty graph acyclic.
- Every computation: self-sufficient baseline, 4–6 factors (overdue 5, upgrade 4, refund 4, early 5), ≥ 2 parameter and ≥ 1 method each, every ladder ≥ 3 disjoint tiers stated in its rule, every factor bearing weight on its task's world against an honest baseline, baseline-only number ≠ gold; per task ≥ 1 multi-source (ovr_late_fee; rf_change_reversal) and ≥ 1 cross-difficulty factor with seeded, charter-priced rows.
- Reworker claims r7 verified: N-7 closed; nothing reopened.
- Final sweep of every class raised in r1–r7 across the whole charter (sibling tails, base departures, empty/unscoped overwrites, cross-charter percentages, first-match/latest reads, same-day ties, rounding placement, zero/negative amounts, method shapes, prerequisite text, tool-body contracts, realism, framing, seed producibility, owner ruling): no open member. Observations on file: O-2, O-3, O-4, O-9–O-14, O-16 (base-level account vs hosting discount wording for out-of-scope upgrades — blueprint note).
- Instantiation gates on the final form: 7/7 OK (`/tmp/erl0076_coord/snap_hosting_plans_and_billing_r7.txt`). The difficulty passes the source-layer audit in revision_7.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

## charter_global_frozen (r8)
- Frozen before any revision_8 GT reveal; earlier revisions untouched. Entry: worklog tail "REWORK round 8: gates 7/7 green"; snapshot run by this auditor → `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r8.txt`: 7/7 OK. Scope of this round: renderer findings S1–S2 in `audits/render_source/hosting_plans_and_billing/render_r1.md` (read), plus regression.
- Hashes: hosting.extended.yaml 5ad9d562…27f3 (changed; copy ext_r8.yaml); task_tools.py cc48c6d2…4184 (changed → tool section re-derived); 0.view 48d08a26… and 1.view c92b7385… unchanged. Worklog "REWORK round 8 claims" not read before the freeze.

### changes found (r8 vs r7)
- S1: overdue.overwrite[0] and early.overwrite[0] replaced_by (and the matching rule sentences) now carry "(renewal_rate_12mo, renewal_rate_24mo or renewal_rate_36mo times the months, or monthly_rate_no_commitment for a 1-month term, with no setup fee)" for the "every other renewal" class.
- S2: refund rule adds "This rule books the refund of an auto-renew line paid by card or through PayPal that goes back to that payment method (refund_destination_default), and only such a refund; a refund the customer elects to take as account credit, and the refund of a line paid from account credit, goes to account credit as stated above and is credited under the account charter's refund-credit rule, not booked under this rule." Processor-fee ladder now: card refunded after its charge date → card_fee_pct; PayPal after its charge date → paypal_fee_pct; otherwise ("refunded on its own charge date, a voided payment") → 0. Refund tool docstring/body: rejects a line not paid by card or PayPal.
- Overdue, upgrade and early rules add "completed at Harborline's checkout by card or through PayPal …; a payment from account credit is not taken under this rule."

### rule_compute_equivalence / action_binding (r8)
- Sweep: compute_basis verbatim, replaced_by in rule, every superseded_clause verbatim in its base rule, every binding has a basis (bad = 0). Processor-fee compute (`refund_on_charge_date = DAYS(line date, NOW) == 0`) = the new ladder.
- Tools: uuid8s unchanged; the new refund check is an object check (the line's payment method), not a prerequisite test; refund_destination booked = original_payment_method, which is now exactly the rule's stated scope. S2's rule-vs-tool mismatch is closed; O-3 closed.
- S1 closed: the out-of-scope renewal class now has its full in-force pricing statement in both sibling replaced_by texts.

### override_declarations (r8)
- **Refund overwrite of hosting_auto_renew_refund (new scope carve).** The overwrite still retires the base "may be refunded in full only on or before …" and its replaced_by reads, with no scope, "An auto-renew charge for a term of 12 months or longer may be refunded only on or before …, and the auto-renew refund amount is the charge less the keep-backs this rule lists." The new rule sentence then says the rule books only card/PayPal refunds back to that method, and that a credit election or a credit-paid line is "credited under the account charter's refund-credit rule, not booked under this rule". account_refund_credit gives no amount of its own ("The credited amount equals the refunded amount of the product charge"). For an out-of-scope refund — e.g. a 36-month auto_renew line paid from account credit (the common case, credit_first_for_auto_renew) refunded 5 days after its charge — reading 1 (the unscoped replaced_by): the line less handling, reversal and commitment keep-backs; reading 2 (base "refunded in full", which nothing in force replaces for a case "not booked under this rule"): the whole line. Two amounts; the replaced_by neither restates the in-force content for the out-of-scope class nor names its own scope (XF C15/C17, same class as N-7).
- The "a payment from account credit is not taken under this rule" sentences in the overdue, upgrade and early rules state what the rule books, while the price sentences are unchanged and independent of payment route; a credit-paid renewal or upgrade keeps the rule's price (observation O-17 — no second price follows from any sentence).

### factor_ladders (r8)
- rf_processor_fee (parameter): card-after / PayPal-after / same-day void → 3 disjoint tiers, distinct values; a same-day void carrying no processor fee is real card/PayPal practice. Other factors unchanged. Counts unchanged (overdue 5, upgrade 4, refund 4, early 5).

### findings (r8)
- S1 closed; S2 closed (rule, docstring and body now agree on what the tool books).
- **N-8 SOURCE-POLICY (XF C15/C17)** — the refund's hosting_auto_renew_refund overwrite keeps an unscoped replaced_by after the rule carved credit-destination refunds out of its scope: out-of-scope auto-renew refunds get either the keep-back amount or the base full amount. Charter-level; no task-world consequence (task 1 refunds a card-paid line to the card).

## closing_checklist (r8)
Written after both r8 reveals (2026-10-22T22:36Z).
- Blind r8 derivations equal GT in both tasks; both tasks PASS all four relationships.
- Renderer findings: S1 closed, S2 closed. Reworker claims (read after the freeze) verified except "the refund overwrites (window, money-back gates) restate their in-force content": the window overwrite's replaced_by applies the keep-back amount to every auto-renew refund while the rule now books only card/PayPal-to-origin refunds — N-8.
- Final sweep of every class raised in r1–r8 across the whole charter: overwrites with unscoped replaced_by after a scope carve (only the refund window overwrite, N-8; the renewal pricing overwrites and both upgrade overwrites are scoped; the money-back/quota overwrites restate their content); sibling tails, base departures, cross-charter percentages, first-match/latest reads and ties, rounding placement, zero/negative amounts, method shapes, prerequisite text, tool-body contracts and rule-vs-tool destinations, realism, framing, seed producibility, owner ruling — nothing else open.
- Coverage, scope disjointness, uuid8s, tree shapes, factor bounds hold; gates 7/7 OK (snapshot r8). Not closed while N-8 stands.

VERDICT revision_8: task0=PASS task1=PASS charter=N-8

## revision_9

## charter_global_frozen (r9)
- Frozen before any revision_9 GT reveal; earlier revisions untouched. Entry: worklog tail "REWORK round 9: gates 7/7 green"; snapshot run by this auditor → `/tmp/erl0076_coord/snap_hosting_plans_and_billing_r9.txt`: 7/7 OK.
- Hashes: hosting.extended.yaml 1c2236e9…b758 (changed; copy ext_r9.yaml); task_tools.py cc48c6d2… (unchanged since r8 → r8 tool section carried); 0.view 48d08a26… and 1.view c92b7385… unchanged. Worklog "REWORK round 9 claims" not read before the freeze.

### changes found (r9 vs r8) — `diff ext_r8.yaml ext_r9.yaml`
Only the refund's hosting_auto_renew_refund overwrite (replaced_by and the matching rule sentence): "…may be refunded only on or before the charge date of the auto-renew charge plus auto_renew_refund_days calendar days; a refund this rule books, of a line paid by card or through PayPal returned to that payment method, is the charge less the keep-backs this rule lists, while the refund of a line paid from account credit, or one the customer elects to take as account credit, is refunded in full and goes to account credit as the base auto-renew refund rule states." Compute, factors, tools unchanged.

### override_declarations / rule_compute_equivalence (r9)
- Sweep: compute_basis verbatim, replaced_by in rule, superseded_clause verbatim in base, every binding has a basis (bad = 0).
- The replaced_by now names its own scope (card/PayPal-to-origin refunds: keep-backs) and restates the in-force base content for the out-of-scope class (credit-paid or credit-elected: in full, to account credit), matching the rule's "This rule books … and only such a refund" sentence and account_refund_credit. The revision_8 world (credit-paid 36-month line refunded after 5 days) now has one amount: the full line, to account credit. N-8 closed.

### findings (r9)
- N-8 closed. No new finding. Factors, trees and tool contracts unchanged from r8.

## closing_checklist (r9)
Written after both r9 reveals (2026-10-22T23:45Z).
- Per-task files correspond one-to-one with the tasks; revisions 1–9 appended in order; every revision_9 comparison PASS; blind = GT on every write, argument and factor figure.
- 4 extended policies covered; scopes disjoint; tools closed, uuid8s independent; both trees 1 prerequisite / 1 value_input / owner=user write (ruling accepted) / acyclic; factor bounds hold (overdue 5, upgrade 4, refund 4, early 5; ≥ 2 parameter, ≥ 1 method each; per task multi-source and cross-difficulty with seeded, charter-priced rows); each factor bears weight against an honest baseline; baseline-only ≠ gold.
- Reworker claims r9 verified: N-8 closed; nothing reopened.
- Final sweep of every class raised in r1–r9 across the whole charter (overwrite scoping incl. both renewal, both upgrade and all three refund overwrites; sibling tails; base departures; cross-charter percentages; first-match/latest reads and ties; rounding placement; zero/negative amounts; method shapes; prerequisite text; tool-body contracts and rule-vs-tool destinations; realism; framing; seed producibility; owner ruling): no open member. Observations on file: O-2, O-4, O-9–O-14, O-16 (blueprint-level), O-17.
- Instantiation gates on the final form: 7/7 OK (`/tmp/erl0076_coord/snap_hosting_plans_and_billing_r9.txt`). The difficulty passes the source-layer audit in revision_9.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
