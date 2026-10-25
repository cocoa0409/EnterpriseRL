# Policy-task audit — professional_email_seats / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-22T12:37Z by an independent policy auditor (erl-task-policy-audit). Not the instantiator.
- Hashes (sha256, checked on disk before reading): `email.extended.yaml` 1c5b41b05a2abeff8fddbb437a91442bf66ae6c595d6585db8f5588a38a07a67; `task_tools.py` ee2ae5e3618e9f243302e7e11bb00305c52e291254d8bdd717406a06c95f925c; views 0.view 34e2f738…2cfa4b8932f2ae2aaf5860ebfad8072c5928215b10cff3d2e984, 1.view 39c507bb…26ccc96fd1a017b1fca6346d3fd64b721d567201b73ef6850a9fbec7. All match the brief.
- Read for this section: blueprint.yaml, products/email.yaml (base), the account.yaml tier parameters and rules, db_schema.json (enums), share_tools.py signatures, email.extended.yaml, task_tools.py, audits/render_source/XF_recipe.md, the DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py (DAYS = date difference; SUM/COUNT scoped to the target holding; CFIELD/CPARAM = first cross-category holding of the customer that matches).
- Masked and unread at the time of writing: every tasks/*.json, plan.md, worklog.md of this difficulty (no recursive search touched the directory). Nothing in this section comes from a revealed GT.
- Entry conditions (Step 0): gate snapshot /tmp/erl0076_coord/snap_professional_email_seats_r1.txt carries EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked-view list and hashes given. check_traceability deferred to step 3 by the coordinator (not run here). Inputs complete.

### policy_conflict_scan
Five extended policies, all scoped to Harborline Mail (Microsoft 365 excluded by each scope sentence):

| policy | subject | target tool (owner) | scope test in the rule |
| --- | --- | --- | --- |
| email_ext_reactivation_renewal | email_renewal_charge, email_reactivate | reactivate_suspended_mail_4fbd3039 (agent) | suspended Harborline Mail, renewal unpaid, scheduled product none |
| email_ext_mail_pro_upgrade | email_plan_change | upgrade_mail_product_74224a57 (user) | Mail Plus on annual_prepaid moving to Mail Pro |
| email_ext_unbilled_seat_catch_up | email_seat_charge | bill_unbilled_mail_seats_5cd17f30 (agent) | Mail on the monthly plan, seats beyond those billed for the current month |
| email_ext_late_monthly_renewal | email_renewal_charge | pay_late_mail_renewal_a889cd52 (user) | Mail monthly plan, paid after term end, status still active, scheduled product none |
| email_ext_annual_conversion | email_renewal_charge | convert_mail_to_annual_cfde09f1 (agent) | Mail monthly plan moved to annual_prepaid, new 12-month term from today |

- Overlapping subjects: three policies price an `email_renewal_charge`. Their scopes are disjoint by record tests: suspended (reactivation) vs active and after term end (late monthly) vs active moving to annual_prepaid starting today (conversion). One residual overlap, recorded as observation O1: the late monthly rule's eligibility sentence "A late monthly renewal may be charged only while the subscription status is active, suspended or expired" admits suspended/expired subscriptions, while its definition ("…while the subscription status is still active…") and the reactivation scope cover a suspended monthly Mail subscription. The definition governs, so no defensible second price follows; the eligibility words are dead text.
- Triggers / terminal states: every tool writes one email_charges row, plus an email_holdings update for four of them (not the catch-up). Base `triggers`: email_renewal_charge -> email:email_term_renew (charge_type renewal), email_seat_charge added_seats -> email:email_seat_update, upgrade_proration -> email:email_plan_change; account:account_credit_apply only when payment_method is account_credit, and every tool writes `card`. Nothing lands in another category (XF 20 clean).
- Cross-category read boundaries: account (variant_name; tier_changed_date for the catch-up), hosting (variant_name, status, primary_domain), domain (nameservers, status, domain_name). They are declared in every policy's cross_category and match compute exactly. Conflict found with the account charter's tier-timing rule: finding CG-3.
- Task scopes: the coordinator gives no claimed per-task split, and charter_scope is masked. Coverage of 5 policies over 2 tasks is checked after the reveal. Claim event types that no extended policy uses: email_seat_update, email_refund, email_settings_update, email_cancel_immediate, email_cancel_schedule, email_expired_renew, email_mailbox_restore (observation O9; nothing requires full claim coverage, but see CG-4 on the customer act).

### rule_compute_equivalence
- Mechanical sweep (scratch, whitespace-normalised): every `compute_basis` quote is verbatim in its own rule; every `overwrite.superseded_clause` is verbatim in the named base rule; every `replaced_by` is verbatim in the extended rule; every `baseline.rule` sentence is in the rule; every prerequisite `policy_source` is in the rule; compute keys and compute_basis keys are the same set in all five policies.
- Sentence-by-sentence sweep back (rule -> compute):
  - Reactivation: renewal months 12/1, list price per plan, combined rate (additive, one reduction), reinstatement charge un-discounted and added before the single RND, tier/volume/bundle/domain/reinstatement/seat-basis ladders: each one maps to a branch. Floor `seat_minimum_reduction_floor` applies only on the two deletion tiers. The rule says "The renewed seats are never fewer than seat_minimum_reduction_floor" after the whole ladder, so on the third tier the floor is vacuous (scheduled seat count >0 or seat count >=1). No gap.
  - Pro upgrade: price difference = K(pro price) − P(current annual price); window test `days_into_term*24 < cancellation_window_hours` equals "full 60-minute periods from 00:00 on the term start date, reaching the last hour closing the window" for date-granular DAYS (day 29 = 696..719 h in window; day 30 = 720 h closed). Final-60-days tier = ceil(days_left/30)/12, inclusive 1..60. Fall-through = days_left/term_days. Matches.
  - Catch-up: billed month seats = opening charge (subscription+renewal with period_start = term start) + added_seats lines with period_end = term end; idle tiers; MX(0,…); price seat_price_monthly un-prorated; tier rate requires tier_changed_date <= term start (DAYS >= 0). Matches. `opening_volume_seats` duplicates `month_opening_seats` as a separate binding with the identical expression (observation O5: rule states the selection once, so it has no consequence).
  - Late monthly: seat_price_monthly, rates, seat basis identical in shape to reactivation, no reinstatement. Matches.
  - Conversion: annual price × seats × 12 with rates, less the credit (credit never discounted, subtracted after multiplication, single RND). Credit tiers: >= 15 days: amount×days/month_days; 1..14: amount×7·floor(days/7)/month_days; else 0. Matches.
- Rounding (XF 11): every rule says "rounded half up to the cent once, on the final figure", and each compute applies a single RND on `result`. Tool bodies round with `_Calc.cents_half_up` (static, int-based half-up), enforce a positive amount and seats >= 1 where the docstring says so.
- Edge inputs (XF 9): CFIELD reads with no match return None -> fall-through tiers (rule "otherwise"). tier_changed_date is never empty (schema: "the sign-up date if never changed"). Negative days_left / unused_days fall to the rule's "otherwise" tiers. Month-end: the tools fall back to the month's last day, and the rules only say "12 calendar months"/"1 calendar month". No scored parameter depends on it, because term dates are written by the tool and read back (observation O4).
- Categorical baseline sentences inside the full rule ("No reinstatement charge is added.", "No conversion credit is given.", "the renewal seat price is the list monthly seat price") stand next to the factor sentences that override them. This is the skill-mandated baseline form, recorded as observation O3.

### action_binding_and_uuids
- (target_tool, computes) pairs are unique: (4fbd3039, renewal_amount), (74224a57, upgrade_amount), (5cd17f30, catch_up_amount), (a889cd52, renewal_amount), (cfde09f1, conversion_amount). renewal_amount appears twice but on different tools.
- uuid8s 4fbd3039, 74224a57, 5cd17f30, a889cd52, cfde09f1: distinct, no shared prefix/suffix, no sequence. No factor id is a substring of a tool name (XF 25): "reactivation_" ⊄ "reactivate_suspended…", "pro_upgrade_" ⊄ "upgrade_mail_product…", "catch_up_" ⊄ "bill_unbilled…".
- Docstrings: no worked values, no composite args, one enumerated value per argument (XF 23/24). No docstring names another tool or a position in a sequence. "…rounded half up to the cent before it is booked" describes internal processing, not an order between actions (observation O7). Every write tool calls ctx.create (and ctx.update where stated) in its own body (XF 26). No tool body tests status, a prerequisite or a window: the tool layer judges no prerequisite.
- Owner assignment: finding CG-4.

### prerequisite_graph
- Every policy has `prerequisite` filled in. Edges: mail_pro_upgrade -> reactivation_renewal (value_input, gate upgraded_seats); late_monthly_renewal -> unbilled_seat_catch_up (state_gate); annual_conversion -> late_monthly_renewal (value_input, gate conversion_credit). All point at extended ids in this file, not at self. The graph is acyclic (two chains: {upgrade->reactivation}, {conversion->late->catch-up}).
- form = state on all three edges, no fallback_reason. resolved_by equals the depended-on target_tool in all three. value_input gates name real bindings (upgraded_seats, conversion_credit). The state_gate is the "not collected until" sentence.
- No authoring-viewpoint phrasing in the prerequisite blocks.
- Condition vs sentence: late-monthly and conversion conditions match their sentences (the conversion condition's "while the status is active" repeats the conversion's own eligibility). The Pro-upgrade condition is narrower than its sentence: finding CG-2.

### prerequisite_sentences
1. Pro upgrade: "The Pro upgrade charge is fixed only after the subscription stands active on a paid term whose term end date lies after today." Ordering connective "only after", state form (status, paid term, term end date), no tool/id/snake_case. Writes of this difficulty that can bring the state about on a subscription inside the Pro-upgrade scope (Plus, annual_prepaid): the reactivation renewal (suspended -> active, new paid term). The late monthly renewal is monthly-only. A conversion only makes a monthly subscription annual, which is a different world (observation O2). Derivation: sentence + a suspended annual Plus record + the reactivation rule ("Once the reactivation renewal is paid the subscription status is active … new term runs from the previous term end date for 12 calendar months") -> the reactivation renewal. One reading. The reactivation rule does not restate the sentence.
2. Late monthly: "A late monthly renewal is not collected until the charges of the current month carry every seat on the subscription other than the seats of mailboxes deleted and never restored." Connective "not … until", state form. The only write that adds seats to the current month's charges without adding seats to the seat count is the catch-up's added-seat line, because a base seat addition raises both sides. Derivation: sentence + records (opening charge seats + added lines < seat count − idle) + the catch-up rule ("one added-seat line for the current month … never changes the seat count") -> the catch-up. One reading. But the depended-on rule cannot always bring the state about: finding CG-1.
3. Conversion: "The annual conversion charge is fixed only after a paid monthly renewal opens a month that runs past today." Connective "only after", state form. For an active monthly subscription past its term end, the late monthly renewal brings it about. For a suspended one, the reactivation renewal would, but the conversion's own scope test ("only while the subscription status is active") and the late rule's definition partition the cases by the status record (observation O2). One reading per world.
- No rule carries a second wording of a dependency or a cross-problem order that grounds no edge. Sibling rules name the other problems' business terms ("a reactivation renewal, a late monthly renewal or a seat catch-up") only inside the shared overwrite restatements that XF 16 requires, and never as an order. No base sentence grounds an edge.

### override_declarations
Sentence by sentence against base_policy_refs:
- email_renewal_and_instalments, sentence "Renewals and instalments use the product's current seat price … apply any scheduled seat count and scheduled product at the renewal." Retired by reactivation, late monthly and conversion. Each replaced_by excludes all three siblings by name and restates the in-force content (XF 15/16 clean). "An annual term billed monthly … a monthly plan renews each month" is retired by the conversion with in-force content restated. "may be charged only while … active, suspended or expired", auto-renew timing, grace, suspension and expired-renewal window are inherited and not contradicted.
- email_suspension_and_retention: "A suspended subscription is reactivated as soon as the overdue amount is paid, and its term dates are unchanged." Retired by reactivation, with out-of-scope content restated. Retention window inherited and restated in the rule. (Minor: the replaced_by's second half "a suspended Harborline Mail subscription whose renewal went unpaid is reactivated as soon as its reactivation renewal is paid" omits the "scheduled product is none" scope test. For a suspended Mail subscription with a scheduled product, the first half ("other than one this policy prices") sends it to base, so the reading is still unique: observation O10.)
- email_mailboxes: "Deleting a mailbox frees its seat but does not reduce the billed seat count." Retired by reactivation, catch-up and late monthly, each tail naming all three (XF 16 clean).
- email_plan_changes: the upgrade billing sentence is retired for the Pro upgrade with out-of-scope content restated. "A product change may be made only while the subscription status is active" is inherited and restated.
- email_seat_changes: the added-seat proration sentence is retired for the catch-up. "Seats may be added or reduced only while … active" is inherited and restated.
- email_cancellation: "Outside the window … a month-to-month charge is never refunded" is retired by the conversion with in-force content restated.
- email_agg_m365_seat_cap (catch-up refs): Microsoft-365-only, so it cannot bite on a Mail subscription. Followed.
- Anonymous intermediates / 0-1 multipliers / dropped branches: none found inside the email base. The one undeclared departure is from another category's base sentence (account charter): CG-3.

### factor_ladders
| policy | factor | label | decides | tiers (fall-through last) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| reactivation | reactivation_tier_rate | parameter | tier_rate | Platinum 12 / Gold 10 / Silver 8 / Bronze 5 / other 0 | no | account |
| reactivation | reactivation_volume_rate | parameter | volume_rate | >=50:8 / 10–49:4 / <10:0 | no | – |
| reactivation | reactivation_bundle_rate | parameter | bundle_rate | Business/Cloud active on email domain 6 / Plus,Pro 3 / else 0 | yes (hosting row × email domain) | hosting |
| reactivation | reactivation_domain_rate | parameter | domain_rate | active + harborline_dns 3 / active + external 1 / else 0 | yes (domain row × email domain) | domain |
| reactivation | reactivation_reinstatement | parameter | reinstatement_months | >=15 d:1 / 4–14 d:0.5 / <4:0 | no | – |
| reactivation | reactivation_seat_basis | method | renewed_seats | seat−idle / min(scheduled, seat−idle) / standard | yes (holding scheduled count × email_events) | – |
| pro_upgrade | tier / volume / bundle / domain | parameter | as above | as above | bundle, domain | account, –, hosting, domain |
| pro_upgrade | pro_upgrade_billing_span | method | billing_fraction | 1 / ceil(d/30)/12 / d/term_days | no | – |
| catch_up | catch_up_tier_rate | parameter | tier_rate | per reseller tier if tier date <= term start / else 0 | yes (account row × email term start) | account |
| catch_up | catch_up_volume_rate, catch_up_bundle_rate | parameter | | as above | bundle | –, hosting |
| catch_up | catch_up_idle_seats | method | catch_up_seats | seat−billed−idle / min(that, scheduled−billed) / seat−billed | yes | – |
| late_monthly | tier / volume / bundle / domain / seat_basis | 4 parameter, 1 method | | as reactivation | bundle, domain, seat_basis | account, hosting, domain |
| conversion | tier / volume / bundle / domain | parameter | | as above | bundle, domain | account, hosting, domain |
| conversion | conversion_credit_basis | method | conversion_credit | amount·d/month_days / amount·7⌊d/7⌋/month_days / 0 | yes (charge row × holding dates) | – |

- Counts: reactivation 6 (5p/1m), Pro upgrade 5 (4p/1m), catch-up 4 (3p/1m), late monthly 5 (4p/1m), conversion 5 (4p/1m). All within 4–6, >= 2 parameter, >= 1 method.
- Every ladder has >= 3 disjoint tiers with stated boundaries. No two tiers of one ladder share a value or method: the tier ladder's 12/10/8/5/0 come from the account charter; Personal and Business are 0 there, which equals the fall-through and is consistent. Every tier is stated in the rule and implemented as a compute branch. Every fall-through equals the factor's `baseline` and the baseline.rule statement.
- Method shape all-pairs (XF 6): seat_basis t1 adds the deletion-count input to t3, t2 adds a min over the scheduled count. Billing span: t1 constant, t2 ceiling over 30-day periods, t3 adds the term_days input. Idle seats: same pattern as seat basis. Credit: t2 adds a floor-to-weeks operation to t1, t3 is 0, and no other tier is 0 over its domain. All pass. Labels are honest.
- Independence (XF A.1/A.2): no factor's tier condition reads another factor's binding. The reinstatement charge (renewed_seats × list price × reinstatement_months) and the results are plain assembly bindings.
- Realism (XF 18): the tier rates are the account charter's email_discount_pct. The volume, hosting-bundle and domain/DNS bundle rates are worded as Harborline's own schedule. The reinstatement charge for a suspension, the full-term difference inside the refund window, the 30-day-period billing in the last 60 days, the unused-days credit on conversion and the idle-seat true-ups are things a real host publishes. Weak points recorded as observation O6: the 1 % external-DNS domain rate is thin, the backdated reactivated term plus a reinstatement charge is a double charge, and the in-window Pro upgrade bills the whole term although days have elapsed. None is demonstrably something no host publishes.

### findings
- **CG-1 — SOURCE-POLICY RED (late monthly prerequisite vs the catch-up's scheduled-seat tier; no solution exists).**
  - Symptom: the state the late monthly renewal waits on cannot be reached by the only write that brings it about once a scheduled seat count is set and idle seats exist.
  - Evidence: the late monthly rule says "A late monthly renewal is not collected until the charges of the current month carry every seat on the subscription other than the seats of mailboxes deleted and never restored" (condition: billed month seats >= seat count − idle). The catch-up rule says "where idle seats are above zero and a scheduled seat count is set, the catch-up seats are the lower of that figure and the scheduled seat count less the seats billed for the current month".
  - Demonstrated consequence: on a producible world (a monthly Mail subscription, seat_count 10, opening charge 6 seats, 1 unrestored deletion, scheduled_seat_count 7; base email_seat_changes schedules reductions on monthly plans), the catch-up bills min(3, 1) = 1 seat, so billed = 7 < 9. A second catch-up computes min(2, 0) = 0, and the tool refuses fewer than 1 seat. The late monthly renewal can never be collected, so the policy entails no solution.
  - Affected: email_ext_late_monthly_renewal rule/prerequisite and email_ext_unbilled_seat_catch_up rule (idle-seat tier 2). Bears on: neither task world (both have scheduled_seat_count 0), so it is charter-only.
- **CG-2 — SOURCE-POLICY RED (prerequisite condition strengthened).**
  - Evidence: the Pro upgrade policy_source says "…stands active on a paid term whose term end date lies after today", while the condition says "…the current term opened by a paid renewal charge on email_charges".
  - Demonstrated consequence: an active annual Plus subscription in its first term (opened by a new_subscription charge, term end after today). The sentence says the state holds; the condition says it does not, so the declared edge would be certified unmet at the opening while the policy surface says it is satisfied.
  - Affected: email_ext_mail_pro_upgrade.prerequisite[0].condition. Bears on: the task whose tree is upgrade <- reactivation. In that world both readings agree (see the task file).
- **CG-3 — SOURCE-POLICY RED (cross-category base rule departed from).**
  - Evidence: the account charter account_tier_qualification says "A tier change never re-prices charges already billed; the new tier's figures apply from the next charge." The catch-up rule says "…any other account, including a Reseller account whose tier took effect after the term start date, takes no account-tier rate."
  - Demonstrated consequence: a Reseller Silver account whose tier took effect after the current month's term start, catch-up billed today (a new charge). The account charter gives 8 % from this next charge; the catch-up gives 0. Two prices for one charge. An email overwrite cannot retire an account-charter sentence, and none is declared.
  - Affected: email_ext_unbilled_seat_catch_up rule/compute tier_rate. Bears on the catch-up task only where the tier date falls after the term start (not the case in that task's world; see its file).
- **CG-4 — SOURCE-CHAIN RED (owner=user tools are not the constitution's customer acts).**
  - Evidence: blueprint.yaml, difficulty professional_email_seats, says "The agent bills seats, upgrades and renewals, records seat counts, scheduled changes, refunds, reactivations and mailbox restores on a verified account, while cancelling a subscription immediately or at term end is the customer's own decision that the customer performs." The charter lifecycle gives the only by: user transitions as cancel_schedule and cancel_immediate. task_tools.py nevertheless makes `upgrade_mail_product_74224a57` (an upgrade) and `pay_late_mail_renewal_a889cd52` (a renewal) owner=user. No email_cancel_* event is used by any policy.
  - Members (all): upgrade_mail_product_74224a57 and pay_late_mail_renewal_a889cd52.
  - Demonstrated consequence: each tree's customer-own write is satisfied only by handing the customer an act the scenario constitution assigns to the agent. A solver reading the constitution and the charter has the agent perform the upgrade or renewal, while the tool can only be run by the customer, so the hand-over requirement is met nominally. The late monthly rule's own "paid by the customer" makes it a declared definition, but it still contradicts the constitution's division.
  - Bears on: task with the upgrade root and task with the late monthly renewal (each file demonstrates it).
- Seeded-world classes are judged per task, and each member is listed in the task files: XF 19 complete cross-category ledgers (hosting_charges/domain_charges), XF 21 owed-at-once, and near-miss.
- Observations (not grounds for rework): O1 dead eligibility words in late monthly, plus its tool leaves the status unchanged; O2 the conversion and Pro-upgrade states are reachable by more than one write across different worlds, partitioned by status and plan records; O3 categorical baseline sentences in the full rule; O4 month-end fallback only in the tool docstrings; O5 duplicate opening-charge binding in the catch-up; O6 realism weak points above; O7 "before it is booked" wording in the docstrings; O9 claim event types unused; O10 reactivation replaced_by omits the scheduled-product scope test.

## closing_checklist
Written after both reveals (2026-10-22T12:41Z). The charter-global section above was written before any reveal and is unchanged.
- Per-task files 0.md and 1.md correspond one to one with tasks 0 and 1 and sit beside this file; this is revision_1, with no older revisions. The comparison sections are not all PASS: task 0 RED (F0-1 chain, F0-2/F0-3 factor) and task 1 RED (F1-1 chain, F1-2 factor). The difficulty does not close.
- Coverage and scope: task 0 = {reactivation_renewal, mail_pro_upgrade} and task 1 = {unbilled_seat_catch_up, late_monthly_renewal, annual_conversion}. Disjoint and jointly complete over the 5 extended policies. Task tools are closed, and uuid8s are independent.
- Trees: task 0 has n=1 with 1 value_input; task 1 has n=2 with 1 value_input + 1 state_gate. Each has one owner=user write (nominal, CG-4). The whole-difficulty graph is acyclic.
- Factors: all computations carry an honest, self-sufficient baseline and 4–6 factors. Every factor bears weight on its world (all sensitivities verified figure for figure). The seeded-ledger realism class fails in both tasks.
- Gates not re-run on a final form (no final form exists, because REDs are open).
- Charter-global REDs open: CG-1, CG-2, CG-3, CG-4. Per-task REDs: F0-1, F0-2, F0-3, F1-1, F1-2.

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4

## revision_2

## charter_global_frozen (revision_2)
- Re-audit, frozen 2026-10-22 (round 2) by the same independent auditor. Entry: `tail -n 1 tasks/professional_email_seats/worklog.md` reads `REWORK round 2: gates 7/7 green`. Gate snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r2.txt` (run by me, execute-only) prints EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- New hashes: `email.extended.yaml` a615ccf6da362ef8dca4c07b548ae73b2bdd69275e70252230918fd7ecc3e502; `task_tools.py` 7eaba5a2ce380fb13ceec3aae926399fc14d8593f2f07b72e31c026e6e2242ba; 0.view 413d710cae8973b2b489f5450997ba3c1fb54afb1e3f3c6cf9aacfffeb9d522c; 1.view d414bbdff0be0f3b2d8035f471e14f51810ee9830a0f141feeed890f3ed25200.
- Both the charter and the tools changed, so every charter-global section below is re-derived in full. The revision_1 text above is left untouched.
- Also read: audits/render_source/owner_ruling.md (coordinator ruling on owner=user writes). From the worklog I read only the item ids listed under "REWORK round 2 claims" (CG-1..CG-4, F0-1..F0-3, F1-1, F1-2, O1, O2, O10), not their text. Task JSONs remained unread until the per-task revision_2 derivations were frozen.

### policy_conflict_scan (r2)
- Base copy is still verbatim (all 10 base keys equal products/email.yaml).
- Same five policies, same target tools. Owners changed:
  - `upgrade_mail_product_74224a57`: user, PayPal checkout.
  - `convert_mail_to_annual_cfde09f1`: now user, PayPal checkout.
  - `pay_late_mail_renewal_a889cd52`: now agent, card on file.
- Scopes are still disjoint by record tests. The late monthly eligibility now reads "may be charged only while the subscription status is active", so O1 is closed.
- Triggers (XF 20): new rows are email_charges with payment_method card or paypal; account_credit_apply fires only for account_credit, and nothing lands in another category. Clean.
- Cross-category reads: the catch-up now reads account variant_name only (tier_changed_date dropped), matching compute.

### rule_compute_equivalence (r2)
- Mechanical sweep repeated: every compute_basis quote, superseded_clause (in base), replaced_by, baseline sentence and policy_source is verbatim in place; compute keys equal compute_basis keys in all five policies.
- Changes swept back:
  - Catch-up tier rate is "the email_discount_pct the account charter sets for the account's tier when the catch-up is billed …", and compute is the current-tier CPARAM ladder. Equivalent.
  - Late-monthly gate sentence now carries the "or carry at least the scheduled seat count where one is set and is lower" branch. It is a gate, not a compute binding. Its prerequisite.condition says "at least the lower of the seat count less … and, where one is set, the scheduled seat count". Equivalent.
  - New payment sentences ("Once the agent has quoted … the account holder pays it personally at Harborline's secure checkout with PayPal … takes effect when that payment completes") in the Pro upgrade and the conversion. These are procedure, with no compute counterpart needed.
- Rounding, edge inputs and month-end: unchanged from revision_1 (O3, O4, O5 stand as observations).

### action_binding_and_uuids (r2)
- Pairs are unique and the uuid8s unchanged, with no factor id inside a tool name. Docstrings carry no values and name no other tool or order.
- Each write tool's body creates its own row. Bodies check no status, gate or window.
- The two user tools book payment_method "paypal", and their docstrings say "The account holder pays, personally at Harborline's secure checkout with PayPal". The late renewal docstring now says "Collect, on the customer's default card on file".

### prerequisite_graph (r2)
- The same three edges, still acyclic: upgrade->reactivation (value_input), late->catch-up (state_gate), conversion->late (value_input). All are state form.
- Pro upgrade condition now: "…the current term being covered by a paid new-subscription or renewal charge whose period start is email_holdings.term_start_date". This equals "a paid term" in the sentence, so CG-2 is closed.
- Late condition matches its new sentence. The late edge's **effect** text was not updated: "Once the seat catch-up line is booked for the current month, the charges of the month carry every seat other than the idle ones, so the late monthly renewal may be collected." That is false on the scheduled-seat tier: finding CG-5.

### prerequisite_sentences (r2)
1. Pro upgrade: unchanged sentence, unchanged derivation (the reactivation renewal is the one write). Pass.
2. Late monthly: "A late monthly renewal is not collected until the charges of the current month carry every seat on the subscription other than the seats of mailboxes deleted and never restored, or carry at least the scheduled seat count where one is set and is lower." Connective "not … until", state form, no tool or id. The catch-up's tier 2 now leaves billed = min(seat − idle, scheduled), which meets the gate. Re-probe of the round-1 deadlock world (seat 10, billed 6, idle 1, scheduled 7): catch-up 1 makes billed 7, which is >= the lower of 9 and 7, so the gate holds and the renewal can be collected (7 seats).
   - Other edges probed: scheduled >= seat − idle -> billed = seat − idle, pass. Idle 0 with a lower schedule -> the otherwise tier bills to the full seat count, which is >= the schedule, pass. Scheduled below billed -> the gate already holds and the catch-up computes 0, pass.
   - CG-1 is closed.
3. Conversion: unchanged. Pass. The new payment sentence is an intra-problem order (quote, then holder pays), not a cross-problem order.
- No rule carries an undeclared cross-problem order (new sentences checked).

### override_declarations (r2)
- Unchanged overwrites. Sibling tails still name all three siblings (XF 16).
- The new holder-pays sentences retire no base email-charter sentence. No base email rule assigns upgrade or renewal billing to the agent (lifecycle has no by: agent transition for a plan change or a conversion), so no overwrite is owed (owner_ruling (b)).
- CG-3: the catch-up now follows the account charter's "the new tier's figures apply from the next charge". Closed.
- O10 is unchanged (observation).

### factor_ladders (r2)
- Counts are unchanged: 6/5/4/5/5, each with >= 2 parameter and 1 method.
- catch_up_tier_rate is now a single-source, five-tier current-tier ladder (Platinum 12 / Gold 10 / Silver 8 / Bronze 5 / other 0) labelled parameter, with cross_difficulty account. That is a real ladder.
- The catch-up computation keeps its multi-source factors: catch_up_idle_seats (holding × events) and catch_up_bundle_rate.
- Every other ladder is as in revision_1. Method shapes, independence and labels pass.
- Realism: as revision_1 O6. New observation O11: the rule fixes PayPal as the *only* way any holder pays a Pro upgrade or an annual conversion. That is plausible as a checkout policy, but narrower than a real host's checkout (cards accepted). Both personas want PayPal, so it has no consequence.

### owner=user writes against owner_ruling.md (r2)
| tool | owner | rule sentence (holder's own act at checkout after the agent quotes) | in-person necessity in the persona | verdict |
| --- | --- | --- | --- | --- |
| upgrade_mail_product_74224a57 | user | "Once the agent has quoted the Pro upgrade charge, the account holder pays it personally at Harborline's secure checkout with PayPal, a payment method Harborline never stores on the account…" | task 0: "pay … with your studio's PayPal … that PayPal account is not saved on your Harborline account" | accepted under (b) |
| convert_mail_to_annual_cfde09f1 | user | "Once the agent has quoted the annual conversion charge, the account holder pays it personally at Harborline's secure checkout with PayPal…" | task 1: "the company's PayPal … not saved on your Harborline account" | accepted under (b) |

The constitution's "agent bills … renewals" is no longer contradicted: the late renewal is now agent-collected on the card. "A payment method Harborline never stores" is consistent with the account charter, under which auto-renew draws credit or "the default card" only. **CG-4 closed.**

### findings (r2)
- CG-1: closed (re-probed above). CG-2: closed. CG-3: closed. CG-4: closed.
- **CG-5 — SOURCE-POLICY RED (XF 27, stale prerequisite effect text; new in revision_2, produced by the CG-1 fix).**
  - Evidence: email_ext_late_monthly_renewal.prerequisite[0].effect says "Once the seat catch-up line is booked for the current month, the charges of the month carry every seat other than the idle ones, so the late monthly renewal may be collected." The rule now gates on "…or carry at least the scheduled seat count where one is set and is lower", and the catch-up's tier 2 bills only up to the scheduled count.
  - Demonstrated: on the world seat 10, billed 6, idle 1, scheduled 7, the catch-up line brings the month to 7 seats, not to "every seat other than the idle ones" (9). The effect's assertion about the world is false there, while the renewal is nevertheless collectable.
  - Affected: email.extended.yaml, late-monthly prerequisite effect. Bears on: neither task world numerically (scheduled 0 in task 1).
- Observations: O1 closed; O2, O3, O4, O5, O6, O7, O9, O10 stand; O11 is new.
- Class sweep across the whole charter (every class raised in any revision):
  - (i) condition vs sentence: all 3 edges equal.
  - (ii) unreachable gate: none.
  - (iii) cross-charter tier timing: all 5 policies now read the current tier.
  - (iv) owner=user: both members accepted.
  - (v) stale proof text in the charter: CG-5 is the only member. The other two effect texts are true.
  - (vi) cross-category ledgers: judged per task.

## closing_checklist (revision_2)
- Task 0 is RED (F0-3 residual stale proof text). Task 1 is PASS. Charter RED CG-5 is open. The difficulty does not close in revision_2.
- Coverage and disjointness: 5/5 policies, scopes disjoint. Trees: each holds one owner=user write accepted under owner_ruling (b). The graph is acyclic.
- Factors: all bear weight, verified figure for figure in both tasks. Ledger class closed in both tasks.
- Final class sweep (every class raised in any revision, whole charter and both tasks):
  - (i) condition vs sentence: clean.
  - (ii) unreachable gate: clean.
  - (iii) cross-charter tier timing: clean.
  - (iv) owner=user: clean.
  - (v) stale proof/effect text: CG-5 (charter) and F0-3 (task 0) are the members.
  - (vi) cross-category ledgers: clean.
  - (vii) XF 21 owed-at-once: clean in both.

VERDICT revision_2: task0=RED task1=PASS charter=CG-5

## revision_3

## charter_global_frozen (revision_3)
- Entry: worklog tail reads `REWORK round 3: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r3.txt` (run by me, execute-only) prints EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK. Claims read by item id only: CG-5, F0-3.
- Hashes:
  - `email.extended.yaml` 9576bc118c9ab2e4e9f147828e28b9c40a41ae6d577324da06766686e80c5b46 (changed);
  - `task_tools.py` 7eaba5a2ce380fb13ceec3aae926399fc14d8593f2f07b72e31c026e6e2242ba (unchanged since revision_2);
  - views 0.view 413d710c…522c and 1.view d414bbdf…5200, both unchanged since revision_2.
- The charter changed, so the charter-global sections were re-derived.
  - Base copy verbatim.
  - Mechanical sweep clean: compute_basis, superseded/replaced_by, baseline sentences and policy_source all verbatim; compute keys equal basis keys.
  - Rules, overwrites, cross-category reads, compute, params and factors are identical to revision_2 (full dump diffed against the revision_2 dump).
  - The only change is email_ext_late_monthly_renewal.prerequisite[0].effect.
  - Therefore § policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_sentences, override_declarations, factor_ladders and the owner table of revision_2 stand as re-derived, with conclusions unchanged.
- CG-5 re-check: the effect now reads "Once the seat catch-up line is booked for the current month, the charges of the month carry every seat other than the idle ones, or at least the scheduled seat count where one is set and is lower, so the late monthly renewal may be collected."
  - Probed on the scheduled-tier world (seat 10, billed 6, idle 1, scheduled 7): after the catch-up the month carries 7 = the scheduled count (lower than 9). The effect is true.
  - On the no-schedule tier it carries seat − idle. True.
  - It matches the sentence and the condition. **CG-5 closed.**
- Class sweep over the whole charter (every class raised in any revision), each checked again:
  - (i) condition vs sentence: 3/3 edges equal.
  - (ii) unreachable gate: none.
  - (iii) cross-charter tier timing: all current-tier.
  - (iv) owner=user: upgrade and conversion accepted under owner_ruling (b); the late renewal is agent.
  - (v) stale effect/proof text in the charter: the 3 effect texts are all true.
  - (vi) XF 20 trigger rule: clean.
  - (vii) uuid / docstring / composite-arg classes: clean.
  - No new charter defect.

## closing_checklist (revision_3)
- Per-task files 0.md and 1.md are one to one with the tasks, with revisions 1–3 kept intact. Both comparison sections PASS in revision_3.
- 5/5 extended policies covered, scopes pairwise disjoint (task 0 = reactivation + Pro upgrade; task 1 = catch-up + late renewal + conversion). Task tools are closed, and the uuid8s are independent and frozen.
- Trees:
  - task 0: n = 1, 1 value_input;
  - task 1: n = 2, 1 value_input + 1 state_gate;
  - each has one owner=user write accepted under owner_ruling (b);
  - the whole-difficulty prerequisite graph is acyclic.
- Factors: every computation has a self-sufficient baseline and 4–6 factors (>= 2 parameter, 1 method). Per task there is >= 1 multi-source and >= 1 cross-difficulty factor. Ladders are real, at least three tiers each, and fully stated in the rule. Every factor bears weight against an honest baseline, and each baseline alone gives a definite number different from gold. Verified figure for figure.
- Seeded worlds: cross-category ledgers complete and priced per their charters. XF 21 clean.
- Gates on the final form: `/tmp/erl0076_coord/snap_professional_email_seats_r3.txt`, 7/7 OK, snapshot run by the auditor. check_traceability is deferred to the coordinator.
- Final sweep of every class raised in any revision (CG-1..CG-5, F0-1..F0-3, F1-1, F1-2), across the whole charter and both tasks: all closed, and no further member found.
- Standing observations (not grounds for rework): O2, O3, O4, O5, O6, O7, O8, O9, O10, O11.

VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN

## revision_4

## charter_global_frozen (revision_4)
- Entry: worklog tail reads `REWORK round 4: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r4.txt` (run by me, execute-only) prints all 7 gates OK. Claims read by item id only: F1, F2, F3, F4, the renderer findings in audits/render_source/professional_email_seats/render_r1.md (read in full; it carries no scored value).
- Hashes:
  - `email.extended.yaml` f9d569fc5254f7e830e80d2869b814bf45872463604d296dcbbdc3312f9cbb53 (changed);
  - `task_tools.py` 7eaba5a2… (unchanged);
  - views 413d710c…/d414bbdf… (unchanged since revision_2).
- The charter changed, so I re-derived it.
  - Base copy verbatim.
  - Mechanical sweep clean: basis, overwrite, baseline and prerequisite quotes all verbatim; compute keys equal basis keys.
  - Sentence-level diff against revision_3: only the reactivation's suspension replaced_by/rule sentence and its reinstatement sentence changed.
  - Factor bindings changed in reactivation_reinstatement, conversion_credit_basis and catch_up_idle_seats. Every other rule, overwrite, prerequisite, cross-category read, param and ladder is identical to revision_3.

### renderer findings F1–F4 (render_r1.md) — closure check
- **F1 (reinstatement assembly):**
  - The plain binding `reinstatement_charge` is gone. The factor reactivation_reinstatement now owns `reinstatement_per_seat = list_month_price * reinstatement_months`, with basis verbatim in the rule: "The reinstatement charge per renewed seat, where one applies, is the list monthly seat price times the reinstatement months; it is never reduced by any rate, and the reinstatement charge, that figure times the renewed seats, is added after the reduced renewal seat price has been multiplied by the renewed seats and the renewal months and before the rounding."
  - `result = RND(renewed_seats * renewal_seat_price * renewal_months + renewed_seats * reinstatement_per_seat, 2)` matches the generic assembly "…plus the reinstatement charge", with a single rounding.
  - Independence: the factor's bindings read list_month_price (plain) and its own reinstatement_months only, and no other factor reads them.
  - The value is algebraically identical to revision_3 (renewed × list × months), so the order is unchanged and the rounding stays a single final RND. Closed.
- **F2:** unused_days and month_days are now in conversion_credit_basis.bindings, and their only reader is conversion_credit. Closed.
- **F3:** scheduled_seats is now in catch_up_idle_seats.bindings, and its only reader in the catch-up is catch_up_seats (standard_catch_up_seats does not read it). Closed.
- **F4 (= my observation O10):** the replaced_by and the rule now read "a suspended Harborline Mail subscription whose renewal went unpaid and whose scheduled product is none is reactivated as soon as its reactivation renewal is paid". The scope matches the definition. Closed; O10 closed.

### class sweep (revision_4, whole charter)
- XF A1–A4 (factor independence; shared selections; factor-only quantities kept out of the baseline; assembly sentences):
  - For every policy I listed the plain bindings read only by factor bindings: standard_seats (reactivation, late), standard_fraction (Pro upgrade), standard_catch_up_seats (catch-up).
  - Each is the factor's baseline value and is defined by a baseline.rule sentence ("The renewed seats are the scheduled seat count where one is set…", "The upgrade billing fraction is the calendar days from today…", "The catch-up seats are the seat count on the subscription less the seats billed for the current month"), so each correctly belongs to the baseline.
  - No other plain binding is defined only by a factor sentence. No factor binding reads another factor's binding.
  - The assembly sentences ("…plus the reinstatement charge", "…less the conversion credit", "first added into one combined rate…") are generic.
  - No member found.
- Classes from revisions 1–3, all re-checked clean:
  - (i) condition vs sentence;
  - (ii) unreachable gate;
  - (iii) cross-charter tier timing;
  - (iv) owner=user, with both members accepted under owner_ruling (b);
  - (v) stale effect text, with the 3 effect texts true;
  - (vi) trigger rule;
  - (vii) uuid / docstring / composite-arg.
- Counts are unchanged: 6/5/4/5/5 factors, >= 2 parameter and 1 method each. The multi-source and cross-difficulty factors per task are unchanged.
- No new charter defect. Observations standing: O2, O3, O4, O5, O6, O7, O8, O9, O11.

## closing_checklist (revision_4)
- Renderer findings F1–F4 are closed, and so is O10.
- Both task comparisons PASS. 5/5 policies are covered with disjoint scopes.
- Trees: task 0 has n = 1 with 1 value_input; task 1 has n = 2 with 1 value_input + 1 state_gate. Each has one owner=user write accepted under owner_ruling (b). The graph is acyclic.
- Factors: 4–6 per computation with honest baselines. All bear weight (verified figure for figure). Independence and ownership are clean after the F1–F3 moves.
- Ledgers are complete.
- Gates on the final form: `/tmp/erl0076_coord/snap_professional_email_seats_r4.txt`, 7/7 OK. check_traceability is deferred to the coordinator.
- Final sweep of every class raised in any revision (CG-1..CG-5, F0-1..F0-3, F1-1, F1-2, renderer F1–F4), across the whole charter and both tasks: no member open.
- Standing observations: O2, O3, O4, O5, O6, O7, O8, O9, O11.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Entry: worklog tail reads `REWORK round 5: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r5.txt` (run by me, execute-only) prints all 7 gates OK. Claims read by item id only: XP-1 (KB audit `audits/policy_kb/professional_email_seats/VERDICT.md`, read in full; it carries no scored value).
- Hashes:
  - `email.extended.yaml` 3b638b829a2d5a1bfe096a1e92de786a9c78e4f07be7a452dc8a44852d515415 (changed);
  - `task_tools.py` 7eaba5a2… (unchanged);
  - 0.view 413d710c… (unchanged);
  - 1.view aa3b00c091b0f557bd00784d2d1864ffcbbaef88f8754e15327dc1a08a1ad028 (changed; task 1 redesigned: seat_count 23, persona "added eight people").
- All charter-global sections are re-derived.
- Self-disclosure: the account charter's `account_tier_benefits` sentence ("…only the single higher percentage applies and percentages are never added or compounded…", "…never applies to … proration lines…", "Discounted components are rounded … before fees are added", "Benefits follow the tier recorded on the account on the charge date") was not checked in revisions 1–4. That was a miss of this audit. XP-1 was a genuine cross-charter conflict of the CG-3 class that I should have listed in revision_1.

### what changed (sentence-level)
- All five policies drop the additive percentage rates (volume / bundle / domain) and replace them with **included seats**: hosting-included (2 for Business/Cloud, 1 for Plus/Pro), domain-included (2 on harborline_dns, 1 external) and volume bonus seats (1 for 10–49 opening seats, 3 for 50+). Each policy states: "Included seats are never billed: the billed seats are the … seats less every seat included with the subscription, never fewer than zero." Each also scopes out the zero-billed case ("This policy prices … only where at least one … seat is billed").
- The tier rate is now "the only percentage that ever reduces" the reactivation renewal component, the late renewal and the annual component. It is applied once before that component is rounded. The reinstatement charge and the conversion credit are rounded separately and added or subtracted after.
- Pro upgrade: no tier rate ("A Pro upgrade charge is a proration line, so no account-tier rate ever reduces it"). The factor pro_upgrade_paid_credit sets a credited seat price = Plus annual price reduced by the tier "recorded on the account on the date of the charge that opened the current term".
- Catch-up: no percentage ("A seat catch-up is an added-seat line, so no account-tier rate and no other percentage ever reduces it").
- Late gate: "…the charges of the current month, together with the seats included with the subscription, carry every seat…".
- Mechanical sweep is clean: basis, overwrite, baseline and policy_source quotes are verbatim, and compute keys equal basis keys. The base copy is verbatim. Factor counts are 6/5/4/5/5, each with >= 2 parameter and 1 method. RND(x + 1e-9) is used for half-up, which is acceptable.

### XP-1 closure check
- Percentage stacking: now gone. Only the tier percentage remains, applied once, and components are rounded before fees and credits. The proration line takes no tier rate. The tier is the one recorded on the charge date. These are closed as stated.
- **The volume discount is still stacked on the tier discount, now in seat form.** `volume_seats` ("volume_seats_mid seats … earn volume_bonus_mid included seat", earned purely by seat volume) is a volume discount on the same price component (billed seats × list price), and it applies together with the tier percentage. The account charter says "When a product's own promotion or volume discount could also apply to the same price component, only the single higher percentage applies and percentages are never added or compounded."
- Demonstrated in task 0's reactivation: 12 renewed seats, 1 volume seat free (8.3 % of the component) plus Bronze 5 %. Both apply, so the scored amount moves under the account reading (see 0.md r5).
- Members: reactivation_volume_seats, late_month_volume_seats, conversion_volume_seats. These are the three policies where a tier percentage and the volume seats both reduce one component. The catch-up has no tier rate, and the Pro upgrade's proration line takes no tier rate, so neither is a member.
- **XP-1 is not closed. It continues as CG-6.**

### rule_compute_equivalence (r5)
- Assembly is generic: renewal component, annual component and result; included = hosting + domain + volume; billed = max(0, seats − included).
- Rounding placement equals the rule sentences in all five policies.
- The scope carve-outs (zero billed seats) are stated. For the conversion, nothing prices the carved-out case (there is no base conversion rule): observation O13.
- **CG-8 — SOURCE-POLICY RED (rule ≠ compute; the rule names a fact no record holds).**
  - Rule: Pro upgrade "The credited seat price of a Pro upgrade is the price the current term billed each seat at, read from the tier recorded on the account on the date of the charge that opened the current term … where that tier is Harborline Reseller Platinum, Gold, Silver or Bronze, the credited seat price is … reduced by that tier's email_discount_pct …; otherwise, including a Reseller tier recorded on the account only after that date, it is the current product's seat_price_annual_prepaid."
  - Compute: `credit_lead_days = DAYS(CFIELD('account','tier_changed_date'), opening_charge_date)`, and the current tier's pct applies only when that is >= 0.
  - Demonstrated on a producible world: an account on Reseller Silver when the term opened, downgraded to Bronze by a failed tier review afterwards (account_tier_qualification: "moves down to the highest tier it qualifies for"). The rule says the credited price is Silver-discounted (the tier recorded on that date, and "the price the current term billed each seat at"). The compute gives the undiscounted price, because the current tier's change date is after the charge.
  - The tier held on a past date is held by no record (account_holdings carries only the current tier and its date; account_tier_change writes no history row).
  - Affected: email_ext_mail_pro_upgrade rule/compute (pro_upgrade_paid_credit). No consequence in task 0's world, where Bronze was recorded before the reactivation line was charged.
- **CG-7 — SOURCE-POLICY RED (tool contract books licensed seats into the field the rules read as billed seats).**
  - Schema: email_renewal_charge `seats: Seats billed`; email_seat_charge `seats: Seats added, or seats upgraded`.
  - The rules now bill fewer seats than the subscription carries (billed = seats − included), yet the tools write the licensed count:
    - `reactivate_suspended_mail_4fbd3039` books `seats=renewed_seats`;
    - `pay_late_mail_renewal_a889cd52` books `seats=renewed_seats`;
    - `convert_mail_to_annual_cfde09f1` books `seats=seat_count`;
    - `upgrade_mail_product_74224a57` books `seats=seat_count`.
  - None can record the billed count. The rules then read those rows as billed seats: "the seats billed for the current month are the seats on the charge that opened the current month…"; "the volume seats … read from the seats on the charge that opened the current term"; and the late gate adds the included seats on top of them.
  - Demonstrated:
    - (a) In task 0 the reactivation line records 12 seats while 7 were billed. The upgrade's volume seats read that line, so on the schema reading (7 billed, fewer than 10) the upgrade's included seats fall by one and its scored amount moves (see 0.md r5).
    - (b) On the next month after any late renewal, the line's seats (licensed) plus the included seats double-count the included seats in the late gate, so up to that many added seats are never caught up.
  - Members: the four tools above. The catch-up tool records the billed catch-up seats it is given, so it is not a member.

### realism (r5)
- **CG-9 — SOURCE-FACTOR RED (XF 18/13 — included seats invented and granted only on late, suspended, upgrade and conversion charges).**
  - Evidence: "the plan includes hosting_seats_high Harborline Mail seats" (hosting-included), "the registration includes domain_seats_dns Harborline Mail seats" (domain-included), plus the volume bonus seats. No charter grants these entitlements. The hosting charter's `mailboxes_included` is cPanel mailboxes, which email_domain_integration says stop receiving mail once Harborline Mail takes over MX. The email base new-subscription (email_pricing) and the ordinary renewal (base email_renewal_and_instalments, still in force for every other renewal) bill every seat.
  - So the same subscription's seats are "included" only when its renewal went unpaid (reactivation), was paid late (late monthly), when a seat catch-up is billed, at a Pro upgrade or at a conversion.
  - Demonstrated:
    - task 0: the on-time auto-renewal attempted on 2026-10-07 would have billed all 14 seats. The reactivation after suspension bills 7, and the suspended customer pays roughly half of the on-time price even with the reinstatement charge.
    - task 1: the on-time 2026-10-13 auto-renewal billed all 23 seats. The late renewal bills 18 of 21 and costs less than the on-time attempt.
  - A host does not publish an entitlement that pays customers for paying late or being suspended. The ladders' values are padding with no real-world counterpart.
  - Members (all 15 included-seat factors, 3 per policy × 5): reactivation_hosting_seats, reactivation_domain_seats, reactivation_volume_seats; pro_upgrade_hosting_seats, pro_upgrade_domain_seats, pro_upgrade_volume_seats; catch_up_hosting_seats, catch_up_domain_seats, catch_up_volume_seats; late_month_hosting_seats, late_month_domain_seats, late_month_volume_seats; conversion_hosting_seats, conversion_domain_seats, conversion_volume_seats.
- Observation O12: "A seat catch-up is an added-seat line, so no account-tier rate … ever reduces it" asserts a consequence that the account charter states only for proration lines, while the catch-up is explicitly un-prorated. The email charter may withhold the discount, so this is not a conflict.

### prerequisite_graph / sentences (r5)
- Same three edges. Conditions match the sentences (the late condition now adds the included seats, exactly as the sentence does). Acyclic.
- The late gate is reachable: after the catch-up, billed + (catch-up − included) + included = seat − idle. When included seats >= catch-up seats, the gate already holds and the catch-up is out of scope. Consistent, apart from the CG-7 double-count on rows written by the tools.
- Effect texts are true in the task worlds.

### owner (r5)
- Unchanged and accepted under owner_ruling (b).

### findings (r5)
- **CG-6** (XP-1 residual): volume bonus seats stacked with the tier percentage, against account_tier_benefits. Members: reactivation, late monthly, conversion.
- **CG-7**: tools record licensed seats in the field the rules read as billed seats. Members: reactivate_suspended_mail_4fbd3039, pay_late_mail_renewal_a889cd52, convert_mail_to_annual_cfde09f1, upgrade_mail_product_74224a57.
- **CG-8**: the Pro-upgrade credited price reads "the tier recorded on the account on the date of the charge", which no record holds after a later tier change; the rule and compute diverge.
- **CG-9**: included Harborline Mail seats granted only on late, suspended and special charges — invented, and a perverse incentive. Members: all 15 included-seat factors.
- Observations: O12 and O13 are new. O2–O9 and O11 stand.

## closing_checklist (revision_5)
- Not closed: charter REDs CG-6 (XP-1 residual), CG-7, CG-8, CG-9; task-local F0-4.
- Task 0 RED (CG-6, CG-7, CG-9, F0-4). Task 1 RED (CG-6, CG-9).
- Coverage and scope, trees, owners, ledgers, XF 21 and factor weight figure for figure: unchanged and clean.
- Final sweep of every class raised in any revision (CG-1..CG-9, F0-1..F0-4, F1-1, F1-2, renderer F1–F4, XP-1):
  - cross-charter (account_tier_benefits / tier timing): CG-6 and CG-8 are the open members;
  - tool contract vs schema: CG-7;
  - realism / invented entitlements: CG-9;
  - stale proof text: F0-4;
  - condition vs sentence, unreachable gate, owner=user, trigger rule, ledgers, uuid/docstring: clean.
- Gates: `/tmp/erl0076_coord/snap_professional_email_seats_r5.txt` 7/7 OK.

VERDICT revision_5: task0=RED task1=RED charter=CG-6,CG-7,CG-8,CG-9

## revision_6

## charter_global_frozen (revision_6)
- Entry: worklog tail reads `REWORK round 6: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r6.txt` (run by me, execute-only) prints all 7 gates OK. Claims read by item id only: CG-6, CG-7, CG-8, CG-9, F0-4, O12, O13, XP-1.
- Hashes, all changed:
  - `email.extended.yaml` 72a1cb06bda6aa846cf799bbaee731f1ef9d1bfc43001d2e30be80cf3353858e;
  - `task_tools.py` f67f62397d2313a7e28d9bd92de49cbe8a1b4dc9dddea56464132dbee3db8ea2;
  - 0.view 40253a386f9db91e2f804299da5c45af1bd12403713e3dc4c629a56809f3f1a9;
  - 1.view 48baa2af8a89bfa96909ced433047f3d29cf23d3e85c062940b0a522738502e9.
- This is a full redesign, so every charter-global section is re-derived. Base copy verbatim. Mechanical sweep clean: basis, overwrite, baseline and policy_source quotes are verbatim; compute keys equal basis keys in all five policies. `email_ext_late_monthly_renewal` is renamed `email_ext_late_renewal`.

### design now (summary)
- All five policies cover any "email subscription" (Microsoft 365 included where the scope allows). Microsoft 365 takes no tier rate.
- Pricing for each charge is:
  - the tier percentage only, applied once before the component is rounded;
  - "seat-band list prices" keyed to the seats on the charge that opened the current term (10–49 and 50+ bands, Starter/Plus/Pro × annual/monthly), declared "Harborline Mail's published list price for a seat in that band, not a discount";
  - a "plan price" factor (renewal months and plan seat price by billing plan);
  - flat fees: a reinstatement fee of 10/20 by days suspended, and a late fee of 5/10 by days late;
  - the Pro upgrade and the conversion credit what the term-opening charge paid, less the fees it carried (inferred from charge-date offsets), times a fraction.
- Hosting and domain rows are removed from both seeds. The only cross-difficulty read is the account tier.
- Factor counts:
  - reactivation 5 (4p/1m);
  - Pro upgrade 6 (4p/2m);
  - catch-up 4 (3p/1m);
  - late renewal 5 (4p/1m);
  - conversion 5 (3p/2m).
  - Multi-source: seat basis/idle (holding × events) and carried fees (charge date × term start). Cross-difficulty: the tier rate in every policy.
- Tools: the reactivation and late renewal now handle annual and annual-billed-monthly terms (`renewal_span`). The upgrade targets Mail Pro or Microsoft 365 Premium by family. All seats are billed, so every line's seats are the billed seats. PayPal/card as before.

### round-5 REDs — closure
- **CG-7 closed.** With included seats gone, every line's `seats` is the count billed (reactivation, late renewal and conversion bill every renewed or converted seat; the upgrade bills every seat), which matches the schema's "Seats billed".
- **CG-8 closed.** The credited price is now the term-opening charge's recorded amount ("the credit basis is its amount"), less fees. No past tier is read.
- **CG-9 closed** in its demonstrated form.
  - No included seats remain. Ordinary renewals now also take band prices and drop idle seats (via the shared replaced_by), so a suspended or late customer no longer pays less than an on-time one.
  - Task 0: the 2026-10-07 on-time attempt would have billed 12 seats at the band price with Bronze. The reactivation bills the same component plus a reinstatement fee. That is coherent.
  - The words-only nature of that fix is CG-11 below.
- **CG-6 (XP-1) — still open, relabelled.** Percentage stacking is gone, but the seat-band "list price" behaves as a volume discount on the variants' list price, and it stacks with the tier percentage.
  - (i) The charter's single list price per seat is the variant parameter seat_price_annual_prepaid / seat_price_monthly ("Price per seat per month…").
  - (ii) The band price is lower and is earned only by volume.
  - (iii) It never applies to a new order. Base email_pricing (not overwritten) bills a new 15-seat order at the plan price, while the same 15 seats at the next renewal get the 10–49 band price. Task 1's seed carries both: the 2026-02-20 new order bills 15 seats at the plan price, and the 2026-03-13 renewal bills the same 15 seats, same tier (0 %), at the band price. A real published list price for a band would apply to the new order too.
  - (iv) "…, not a discount" is a classification sentence the records contradict.
  - Under account_tier_benefits ("When a product's own promotion or volume discount could also apply to the same price component, only the single higher percentage applies and percentages are never added or compounded"), the band reduction and the tier percentage both apply to one component.
  - Members (every policy where tier and band both apply): reactivation_seat_band, pro_upgrade_seat_band (inside the window, where the tier applies), catch_up_seat_band, late_renewal_seat_band, conversion_seat_band.
- O12 resolved (the catch-up now takes the tier rate). O13 resolved (no zero-billed carve-out remains).

### new findings
- **CG-10 — SOURCE-FACTOR RED (straw-man baselines in the plan-price factors).**
  - The charter's standard method for a renewal is "the product's current seat price for the billing plan" (base email_renewal_and_instalments, restated in every replaced_by for all other renewals; base email_pricing per_tier annual/annual_monthly/monthly).
  - The four plan-price factors make the subscription's own billing plan a factor, and their baselines fix one plan regardless of the subscription:
    - reactivation_plan_price baseline "The renewal months are 1 and the plan seat price is seat_price_monthly";
    - pro_upgrade_plan_price baseline "The upgrade months are 1 and the target plan seat price is the target product's seat_price_monthly";
    - catch_up_plan_price baseline "The catch-up months are 12 and the plan seat price is seat_price_annual_prepaid";
    - late_renewal_plan_price baseline "The renewal months are 12 and the plan seat price is seat_price_annual_prepaid".
  - Each fixed plan is the opposite of the plan in that policy's task world: task 0 is annual, with monthly baselines; task 1 is monthly, with annual baselines.
  - No reader renews an annual-prepaid term as one month at the monthly price, or a month-to-month renewal as twelve months at the annual price. The baselines are straw men chosen to differ from the world, not a standard method with default values.
  - Demonstrated:
    - task 0: the Pro upgrade's plan-price baseline alone gives a *negative* upgrade charge;
    - task 1: the late renewal's plan-price baseline alone bills a year for a month-to-month renewal (both shown in the task files).
  - Members: reactivation_plan_price, pro_upgrade_plan_price, catch_up_plan_price, late_renewal_plan_price.
- **CG-11 — SOURCE-POLICY RED (XF 14/15 and check 2: replaced_by sentences add new pricing for out-of-scope cases in words only, with no compute).**
  - The overwrites no longer only restate still-in-force base content for out-of-scope cases. They add new obligations that no compute prices:
    - (a) renewal replaced_by (in reactivation, late renewal, conversion): "…a Harborline Mail seat being priced at its seat-band list price where one applies, … a renewal that starts a new term dropping the seats of mailboxes deleted and never restored" for every ordinary renewal and instalment;
    - (b) seat-change replaced_by (catch-up): "…a Harborline Mail seat being priced at its seat-band list price where one applies" for every ordinary seat addition;
    - (c) suspension replaced_by (reactivation): "A suspended subscription is reactivated as soon as the overdue amount and its reinstatement charge are paid" for every suspended subscription, including ones this policy does not price (for example a suspended instalment);
    - (d) grace replaced_by (late renewal): "…a renewal paid after its due date but before that day carries the late-payment fee this policy sets" for every late renewal, including ones carrying a scheduled product, which the policy leaves "under the base rule";
    - (e) mailboxes replaced_by: "seats are figured from the mailbox deletions only at a renewal that starts a new term…" for ordinary renewals.
  - Demonstrated:
    - (d) A monthly Mail renewal with a scheduled product, paid 2 days late, is "under the base rule" by the late policy's scope sentence yet "carries the late-payment fee this policy sets" by its replaced_by. No compute prices that fee, and the base rule has none. Two readings of the same charge.
    - (a) and (b) Seeded ordinary rows (task 0's 2026-01-12 added seats, task 1's monthly auto-renewals) are priced at band prices that only these words state.
  - Members: (a)–(e).
- Observations:
  - O14: the band is keyed to the term-opening charge's seats, not the seats bought.
  - O15: the carried fees are inferred from charge-date offsets rather than read from the line.
  - O2–O9 and O11 stand.

### other classes re-checked (r6)
- Prerequisite conditions equal their sentences (3 edges). Gates are reachable (late: catch-up brings billed to seat − idle or the scheduled count). Effect texts are true. Acyclic.
- Owner (b) is accepted. Trigger rule is clean. uuid8s, docstrings and composite args are clean. Rounding placement equals the rule sentences.
- Factor independence: assembly bindings only (target component − term credit; (paid − fees) × fraction).
- Method shapes: credit basis t2 adds the data input "months of term"; paid-month t2 adds an input. Both pass.

## closing_checklist (revision_6)
- Closed this round: CG-7, CG-8, CG-9, F0-4 (plus O12, O13).
- Open:
  - CG-6 (XP-1, relabelled as band list prices);
  - CG-10 (straw-man plan-price baselines);
  - CG-11 (replaced_by words-only pricing for out-of-scope cases).
- Task 0 RED, task 1 RED (both bear CG-6, CG-10, CG-11).
- Scope (5/5, disjoint), trees, owners (ruling (b)), ledgers (account + email only, consistent), XF 21 and factor weight figure for figure: clean.
- Final sweep of every class raised in any revision across the whole charter:
  - cross-charter account_tier_benefits: CG-6;
  - baseline honesty: CG-10;
  - words-only pricing / replaced_by scope: CG-11;
  - tool vs schema seats: clean;
  - past-tier reads: clean;
  - invented entitlements: clean;
  - condition vs sentence, unreachable gate, stale proof text, trigger rule, uuid/docstring: clean.
- Gates: `/tmp/erl0076_coord/snap_professional_email_seats_r6.txt` 7/7 OK.

VERDICT revision_6: task0=RED task1=RED charter=CG-6,CG-10,CG-11

## revision_8

## charter_global_frozen (revision_8)
- No revision_7 of this report exists. The worklog shows `REWORK round 7: gates RED check_extended check_compute`, so round 7 never reached this audit. The "round-7 REDs" to verify are therefore the open REDs of revision_6 (CG-6, CG-10, CG-11), which match the round-8 claim ids (CG-6, CG-10, CG-11, XP-1, O15).
- Entry: worklog tail reads `REWORK round 8: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r8.txt` (run by me, execute-only) prints all 7 gates OK.
- Hashes:
  - `email.extended.yaml` e0e3304534f1a439b3bc64990d6ce73c4f60d5fb980b6158b8ba47468c305a62 (changed);
  - `task_tools.py` f67f6239… (unchanged since revision_6);
  - 0.view 472adf9a142fdd38a74c64af390da8eb68d83cd3142506dede8491de41b2335a (redesigned);
  - 1.view 6b28044c3c9d5e52bfcca51328b9ae76e0f5e32006d7bcd077d4c964c4b30f93 (redesigned).
- Charter-global sections are re-derived in full.
  - Base verbatim. Mechanical sweep clean (basis, overwrite, baseline and policy_source verbatim; compute keys equal basis keys).
  - `email_ext_late_renewal` becomes `email_ext_term_renewal`, which now prices every renewal of an active subscription falling due on its term end with no scheduled product, on time or late.

### round-6 REDs — closure
- **CG-6 closed.** Seat-band prices are removed from every policy. The only percentage left is the tier rate. The Pro upgrade takes no percentage ("A Pro upgrade charge is a proration line, so no account-tier rate and no other percentage ever reduces it"). Fees are flat and never discounted. account_tier_benefits is honoured.
- **CG-10 closed.**
  - Every plan-price baseline is now the product's own annual-commitment price ("The plan seat price is the product's seat_price_annual_prepaid, its annual-commitment price"). The renewal or catch-up months follow the billing plan in the baseline itself.
  - The monthly and annual-monthly prices are the premium tiers ("the month-to-month price above the annual commitment"). This is one uniform standard price, no longer a per-task opposite plan.
  - This matches how Harborline's own variants and Microsoft's published prices relate (monthly is a premium over annual).
- **CG-11 closed.**
  - Every replaced_by again restates only the in-force base content for out-of-scope cases (renewal: "…uses the product's current seat price for the billing plan … applies any scheduled seat count and scheduled product…"; suspension: "…reactivated as soon as the overdue amount is paid, and its term dates are unchanged"; seat changes: base proration).
  - Ordinary renewals are now priced by a policy with compute (term renewal) instead of by words.
  - The seeded ordinary rows in both tasks reproduce under the term-renewal compute (see the task files).

### new / remaining findings (revision_8)
- **CG-12 — SOURCE-FACTOR RED (unreal ladders: two tiers select the same value, so the ladder has fewer than three distinct tiers).**
  - Four ladders read "(deletions outnumber restores) → that difference; (every such deletion restored) → 0; (otherwise, no such deletion) → 0":
    - reactivation_kept_seats;
    - term_renewal_kept_seats;
    - catch_up_kept_seats;
    - catch_up_idle_seats.
  - Two of the three tiers select the same value (0). The ladder is one formula (an unrestored-deletion count, which is 0 when there is nothing unrestored) written as three tiers.
  - The compute shows it: `(… ) if (deletes > 0 and deletes > restores) else (0 if deletes > 0 else 0)`, both else-branches 0.
  - Members: the four factors above. Each policy keeps its other factors, but these four fail the >= 3 pairwise-distinct-tier rule.
- **CG-13 — SOURCE-FACTOR RED (method tier that overrides the customer's own scheduled seat count).**
  - Rule (reactivation, term renewal): "where a scheduled seat count is set and the idle seats are above zero, they start from the scheduled seat count less the idle seats". The catch-up does the same through "the catch-up target is the scheduled seat count" less the idle seats.
  - Revisions 1–6 used the lower of the scheduled count and the seat count less idle seats.
  - Demonstrated on a producible world: 10 seats, 2 mailboxes deleted this term (8 in use), the customer schedules 8 for the renewal (base email_seat_changes: a reduction outside the window "is scheduled as the seat count for the next renewal"). The renewal bills 8 − 2 = 6 seats. That is fewer seats than mailboxes in use, a state the base charter cannot hold ("Deleting a mailbox frees its seat"; every mailbox occupies a seat). It also overrides the seat count the customer explicitly ordered.
  - No host renews fewer seats than the customer scheduled because of deletions the schedule already reflects.
  - Members: reactivation_seat_basis (tier 2), term_renewal_seat_basis (tier 2), catch_up_scheduled_target together with catch_up_idle_seats (a scheduled target less idle seats).
  - Neither task world has the double count: in task 1 the schedule is explained by the persona as dropping two temporary seats, not as the leavers. The defect is charter-level.
- Observations:
  - O16: kept seats use "less than one whole calendar month" while the base restore window is deleted_mailbox_retention_days = 30 calendar days. They diverge by month length, and the rule's "so that the mailbox can still be restored" is framing.
  - O17: the reactivation charges both a late-payment fee and a reinstatement fee for one unpaid renewal (plausible, as utility-style late plus reconnection).
  - O2–O9, O11, O14 and O15 stand where still applicable. O14 (band) is moot now that bands are gone.

### other classes re-checked (r8)
- Factor counts:
  - reactivation 6 (5p/1m);
  - Pro upgrade 5 (3p/2m), no account read; task 0's cross-difficulty comes from the reactivation tier;
  - catch-up 5 (4p/1m);
  - term renewal 5 (4p/1m);
  - conversion 4 (2p/2m).
  - Multi-source: seat basis, scheduled target, carried fees.
- Prerequisite edges:
  - The late gate is now "A late renewal is not collected until the charges of the current term carry at least the seats it renews". Its condition is equivalent.
  - It is reachable: the catch-up brings billed seats to target − idle + kept, which equals the renewed seats in every scheduled/unscheduled case. Kept seats are a subset of idle seats by window.
  - Effect texts are true. Acyclic.
- Owner (b) accepted. Tools unchanged and clean. Trigger rule, uuid8s and docstrings clean. Rounding placement matches.
- Ledgers: account + email only, consistent. XF 21 clean.

## closing_checklist (revision_8)
- Closed: CG-6 (XP-1), CG-10, CG-11.
- Open:
  - CG-12 (four two-valued "ladders": reactivation_kept_seats, term_renewal_kept_seats, catch_up_kept_seats, catch_up_idle_seats);
  - CG-13 (scheduled count less idle seats overrides the customer's own schedule: reactivation_seat_basis, term_renewal_seat_basis, catch_up_scheduled_target + catch_up_idle_seats).
- Task 0 RED (CG-12). Task 1 RED (CG-12).
- Scope (5/5, disjoint), trees, owners (ruling (b)), ledgers (account + email, reproducing under the charter), XF 21, and factor weight figure for figure: clean.
- Final sweep of every class raised in any revision:
  - cross-charter account_tier_benefits: clean;
  - baseline honesty: clean;
  - words-only pricing / replaced_by scope: clean;
  - tool vs schema seats: clean;
  - past-tier reads: clean;
  - invented entitlements: clean;
  - ladder distinctness: CG-12;
  - method-tier realism: CG-13;
  - condition vs sentence, unreachable gate, stale proof text, trigger rule, uuid/docstring: clean.
- Gates: `/tmp/erl0076_coord/snap_professional_email_seats_r8.txt` 7/7 OK.

VERDICT revision_8: task0=RED task1=RED charter=CG-12,CG-13

## revision_12

## charter_global_frozen (revision_12)
- No revisions 9–11 of this report exist. The worklog shows rounds 9, 10 and 11 ending `gates RED check_compute`, so they never reached audit. The REDs to verify are revision_8's CG-12 and CG-13.
- Entry: worklog tail reads `REWORK round 12: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r12.txt` (run by me, execute-only) prints all 7 gates OK. I read the round-12 claims section only for its item headings; no ids are cited in it.
- Hashes, all changed:
  - `email.extended.yaml` d56236807038235f5edc91f94e33a1b0462e1eeb7897215ba9f944e6e3a8306d;
  - `task_tools.py` df6194359cf86bcc729a73001f86fcc6b9d8f32dcc6d71d8a61bc690ab5f775f;
  - 0.view 998e36dbb0c1b5e04c6cccaf1c2a9ef40f430776913f43cd111eff5cf5aba5ab;
  - 1.view e2565db1628a35786e0e71a5385a98cd1236b40808582a943bdce9f72b1bff68.
  - Both views now carry scheduled_variant "Harborline Mail Starter".
- Charter-global sections are re-derived.
  - Base verbatim. Mechanical sweep clean (basis, overwrite, baseline and policy_source verbatim; compute keys equal basis keys).
  - Sentence-level diff against revision_8:
    - reactivation and term renewal now include renewals that carry a scheduled product, with a new renewal-product factor and price columns;
    - kept seats are removed;
    - the seat basis is reworked;
    - the catch-up regains a proration fraction;
    - the conversion gains an "annual start date" factor;
    - tools: the reactivation and late renewal apply the scheduled product, and the conversion picks the annual start date.

### round-8 REDs — closure
- **CG-12 closed.** Every kept-seat factor is gone, and the idle seats are folded into the seat-basis methods. Every remaining ladder has >= 3 distinct outcomes: seat basis (max(seat − idle, min(scheduled, seat)) / seat − idle / seat), catch-up span (1 / whole weeks / days over term), annual start (whole month / none / days to term end), renewal product (Starter / Plus / Basic / Standard / current).
- **CG-13 closed.** "where a scheduled seat count is set, the renewed seats are the lower of the scheduled seat count and the seat count on the subscription, but never fewer than the mailboxes in use, the seat count less the idle seats". Re-probe of the round-8 world (10 seats, 2 deleted, scheduled 8): max(8, min(8, 10)) = 8, so the customer's schedule is honoured and seats are never below the mailboxes in use. The catch-up target uses the same expression.

### new findings (revision_12)
- **CG-14 — SOURCE-POLICY RED (XF 13 framing fact no record holds, plus an undeclared departure from base email_plan_changes).**
  - Base email_plan_changes: "where retention_on_downgrade is true each mailbox must already fit the lower product's mailbox_storage_gb when the renewal runs, otherwise the change is skipped at that renewal."
  - Extended (reactivation and term renewal; email_plan_changes is in neither policy's base_policy_refs, and no overwrite exists): "Where retention_on_downgrade is true the mail system checks, when the renewal runs and before it is billed, that every mailbox fits the lower product's mailbox_storage_gb, and a change that fails the check is cleared from the subscription and skipped at that renewal, so a scheduled product still on record is one that passed it."
  - The "so …" clause presumes a check result for the very renewal being billed now ("before it is billed"). No record holds mailbox storage or any check outcome.
  - Demonstrated, same situation and different conclusions: a scheduled downgrade on record whose mailboxes exceed the lower product's storage.
    - Base: the change is skipped, so the renewal is priced at the current product.
    - Extended: it "passed", so the renewal is priced at the scheduled product.
    - Task 0's world is such a case on the persona's own facts (see 0.md r12).
  - Members: the sentence in email_ext_reactivation_renewal and the identical sentence in email_ext_term_renewal.
- **CG-15 — SOURCE-POLICY RED (XF 24 + tool contract: the conversion tool carries a factor's ladder and decides it).**
  - `convert_mail_to_annual_cfde09f1`'s docstring states "the current term start date where that date is fewer than 5 calendar days before today, else the current term end date where that date is 3 calendar days or fewer after today, else today". These are the concrete values of conversion_start_days and conversion_end_days. The body implements that tier choice itself (`if _Calc.days_between(t_start, today) < 5 … elif … <= 3`).
  - The factor conversion_annual_start's ladder is thereby published on the tool surface (the factor document is no longer the only place it is findable) and decided by the tool, not by the agent.
  - Members: convert_mail_to_annual_cfde09f1 (docstring and body).
- **CG-16 — SOURCE-POLICY RED (compute invents a condition the rule lacks).**
  - Rule: "The renewal product of a … renewal is read from the scheduled product on the subscription, which the base rule applies at the renewal that falls due on the term end date: a scheduled … makes that product the renewal product".
  - Compute: `renewal_product = … if (F('scheduled_variant') == … and DAYS(F('term_end_date'), NOW) >= 0) else … F('variant_name')`.
  - The term-renewal scope covers renewals "billed on or before its due date" (base auto-renew runs auto_renew_days_before_end = 7 days early). For such a renewal with a scheduled downgrade, the rule prices the scheduled product and the compute prices the current product.
  - Demonstrated: a Plus monthly subscription with Starter scheduled, renewed on time 7 days before its term end, is priced at the Plus monthly price by compute and at the Starter monthly price by the rule.
  - Members: term_renewal_product (divergent) and reactivation_renewal_product (the same invented condition, vacuous because a reactivation always follows the term end).
- Observations:
  - O18: the catch-up's all-baseline result is 0.00 in task 1, because the baseline fraction never drops below zero on an ended term. That is definite and different from gold, but not bookable.
  - O19: a Pro upgrade from a subscription just renewed down to Starter (task 0) is coherent given the tools, since there is no write to withdraw a scheduled product.
  - O2–O9, O11, O15, O16 and O17 stand where applicable.

### other classes re-checked (r12)
- Factor counts:
  - reactivation 6 (5p/1m);
  - Pro upgrade 5 (3p/2m; no account read);
  - catch-up 4 (2p/2m);
  - term renewal 5 (4p/1m);
  - conversion 5 (3p/2m).
  - Multi-source: seat basis, carried fees. Cross-difficulty: the account tier per task.
- Prerequisite edges: the late gate condition now uses the new renewed-seat expression, equal to the sentence's "the seats it renews". The catch-up target uses the same expression, so the gate is reachable. Acyclic. Effect texts are true.
- Owner (b) accepted. Trigger rule clean. Rounding placement matches. Ledgers: account + email only.
- Cross-charter (account_tier_benefits): only the tier percentage, never on fees, credits or the upgrade proration line. Clean.
- Words-only pricing: clean. Every replaced_by restates base, and the scheduled-product renewals are now priced by compute.

## closing_checklist (revision_12)
- Closed: CG-12, CG-13.
- Open:
  - CG-14 (retention_on_downgrade framing in reactivation and term renewal);
  - CG-15 (conversion tool docstring/body carry and decide the annual-start ladder);
  - CG-16 (renewal-product compute condition absent from the rule: term renewal, reactivation).
  - Task-local: F0-5.
- Task 0 RED (CG-14 -> F0-5). Task 1 RED (CG-15).
- Scope (5/5, disjoint), trees, owners (ruling (b)), ledgers, XF 21 and factor weight figure for figure (25/25): clean.
- Final sweep of every class raised in any revision across the whole charter:
  - framing fact / base departure: CG-14;
  - docstring values / tool deciding a factor: CG-15;
  - rule ≠ compute: CG-16;
  - ladder distinctness: clean;
  - seat-basis realism: clean;
  - cross-charter account_tier_benefits: clean;
  - baseline honesty: clean;
  - words-only pricing: clean;
  - tool vs schema seats: clean;
  - invented entitlements: clean;
  - condition vs sentence, unreachable gate, stale proof text, trigger rule, uuid: clean.
- Gates: `/tmp/erl0076_coord/snap_professional_email_seats_r12.txt` 7/7 OK.

VERDICT revision_12: task0=RED task1=RED charter=CG-14,CG-15,CG-16

## revision_13

## charter_global_frozen (revision_13)
- Entry: worklog tail reads `REWORK round 13: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r13.txt` (run by me, execute-only) prints all 7 gates OK. Claims read by item id only: CG-14, CG-15, CG-16, F0-5.
- Hashes:
  - `email.extended.yaml` ba4581ac8dab8036090a809988ccef10aa9d6ba5734f4b31e981aa0a9d1bcd40 (changed);
  - `task_tools.py` f267ea766ffff19d7ac48aa45b72f38b655f1e4e0b00084fbddd40a021fa08d5 (changed);
  - 0.view 777d97f572889db8a2f4daaac061749f76950236fa7bf81b7aba68fc10a73640 (persona line changed);
  - 1.view e2565db1… (unchanged since revision_12).
- Re-derived. Base verbatim. Mechanical sweep clean.
- Sentence-level diff against revision_12, limited to:
  - reactivation and term renewal: email_plan_changes added to base_policy_refs with a new overwrite; the retention framing sentence replaced; the renewal-product condition rewritten in rule and compute;
  - the conversion tool takes an `annual_start_date` argument.
  - Every other rule, compute, param and ladder is identical to revision_12.

### round-12 REDs — closure
- **CG-14 closed.**
  - The base sentence is now retired by a declared overwrite in both policies: superseded "where retention_on_downgrade is true each mailbox must already fit …"; replaced_by "At every renewal other than a reactivation renewal or a term renewal, where retention_on_downgrade is true each mailbox must already fit … otherwise the change is skipped at that renewal".
  - The rule states what happens instead: "At a reactivation renewal a scheduled lower product is applied even where a mailbox does not fit the lower product's mailbox_storage_gb: such a mailbox is full and, where send_block_at_full is true, stops sending until space is freed".
  - No fact is presumed from a missing record any more.
  - Sibling overwrites (XF 16): both tails exclude "a reactivation renewal or a term renewal" by name.
  - Realism: applying a downgrade and leaving over-quota mailboxes send-blocked is a published practice, using base send_block_at_full.
- **CG-15 closed.** The conversion tool takes `annual_start_date` ("Fixed-format class — the date the new 12-month annual term starts, as YYYY-MM-DD"). The docstring carries no thresholds, and the body no longer chooses the tier; it validates the date format only. The annual-start ladder lives only in the policy.
- **CG-16 closed.**
  - The compute condition is now `COUNT('email_charges', charge_type='upgrade_proration', period_end=F('term_end_date')) == 0`.
  - The rule states it: "otherwise, where no product is scheduled or an upgrade line whose period end is the term end date belongs to the current term, since a move down never takes effect at the renewal that closes a term in which the subscription was moved up, the renewal product is the subscription's current product".
  - The term-end-passed condition is gone, so an on-time term renewal applies the scheduled product as the rule says.
  - Rule and compute are equivalent. The ladder's fall-through names the new case.

### new findings (revision_13)
- None at charter level. The new tool argument is examined per task (see 1.md r13).
- Class sweep over every class raised in revisions 1–12: clean.
  - The two overwrites of email_plan_changes retire a genuinely conflicting clause and restate the in-force content for every other renewal.
  - The new condition reads a record that the upgrade tool writes (upgrade_proration, period_end = the term end).
  - Factor counts are unchanged (6/5/4/5/5). Owner (b), ledgers, trigger rule and rounding are unchanged.

## closing_checklist (revision_13)
- Closed: CG-14, CG-15, CG-16, F0-5. No charter-level RED remains.
- Task 0 PASS. Task 1 RED on task-local items only: F1-3 (persona lacks the new annual_start_date argument of the customer-run tool) and F1-4 (proof claims "starting today").
- Scope (5/5, disjoint), trees, owners (ruling (b)), ledgers, XF 21, and factor weight figure for figure (25/25): clean.
- Final sweep of every class raised in revisions 1–13 across the whole charter: clean. That covers:
  - framing facts / base departures;
  - docstring values / tool-decided tiers;
  - rule ≠ compute;
  - ladder distinctness;
  - seat-basis realism;
  - account_tier_benefits;
  - baseline honesty;
  - words-only pricing;
  - tool vs schema seats;
  - invented entitlements;
  - condition vs sentence;
  - unreachable gates;
  - trigger rule;
  - uuid / docstring / composite args.
  - The only stale-proof member is task-local (F1-4).
- Gates: `/tmp/erl0076_coord/snap_professional_email_seats_r13.txt` 7/7 OK.

VERDICT revision_13: task0=PASS task1=RED charter=CLEAN

## revision_14

## charter_global_frozen (revision_14)
- Entry: worklog tail reads `REWORK round 14: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r14.txt` (run by me, execute-only) prints all 7 gates OK. Claims read by item id only: F1-3, F1-4.
- Hashes:
  - `email.extended.yaml` ba4581ac… and `task_tools.py` f267ea76…, both identical to revision_13;
  - 0.view 777d97f5… (unchanged);
  - 1.view df3a913f00f9d37b98e6f324637306171c9d4bb2b1de969cc2a221ac6940cda3 (persona only).
- Charter and tools are unchanged, so every charter-global section of revision_13 is carried forward by reference, on these two hashes. No charter-level RED is open.
- Class sweep across the whole charter (every class raised in revisions 1–13) re-confirmed against the unchanged charter: clean.

## closing_checklist (revision_14)
- The per-task files 0.md and 1.md correspond one to one with the tasks, revisions 1–14 are kept, and both revision_14 comparisons PASS.
- Coverage and scope: 5/5 extended policies covered, scopes disjoint (task 0 = reactivation + Pro upgrade; task 1 = catch-up + term renewal + conversion). Task tools are closed, and the uuid8s are independent and frozen.
- Trees:
  - task 0: n = 1, 1 value_input;
  - task 1: n = 2, 1 value_input + 1 state_gate;
  - each holds one owner=user write accepted under owner_ruling (b) (PayPal checkout, in-person necessity in the persona);
  - the difficulty's prerequisite graph is acyclic.
- Factors:
  - every computation has a self-sufficient baseline and 4–6 factors (>= 2 parameter, >= 1 method);
  - per task there is >= 1 multi-source and >= 1 cross-difficulty factor (the account tier);
  - ladders have >= 3 distinct tiers, all stated in the rule;
  - all 25 factors bear weight, verified figure for figure against GT.
- Seeded worlds: account + email ledgers reproduce under the charter. XF 21 clean.
- Gates on the final form: `/tmp/erl0076_coord/snap_professional_email_seats_r14.txt` 7/7 OK. check_traceability is deferred to the coordinator.
- Final sweep of every class raised in revisions 1–14 (CG-1..CG-16, F0-1..F0-5, F1-1..F1-4, renderer F1–F4, XP-1), across the whole charter and both tasks: no member open.
- Standing observations (not grounds for rework): O2–O9, O11, O15–O19 where still applicable.

VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN

## revision_15

## charter_global_frozen (revision_15)
- Entry: worklog tail reads `REWORK round 15: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r15.txt` (run by me, execute-only) prints all 7 gates OK. Claims read by item id only: G1–G5, the renderer findings of audits/render_source/professional_email_seats/render_r3.md (read in full; no scored values in it).
- Hashes:
  - `email.extended.yaml` 35f667eb027b4d84de0a5bad3199b4e4a98ee87993452b790f53577ee3465e76 (changed);
  - `task_tools.py` ff9caa38c0330975ad25ff90babbfd9a70ea401fea2c6713dc037023cde32a0f (changed);
  - views 777d97f5… / df3a913f… (both unchanged since revision_14).
- Charter-global sections are re-derived. Base verbatim. Mechanical sweep clean. The sentence-level diff against revision_13 is limited to the G1–G4 edits and the tool docstring and body edits (G1, G5).

### renderer findings G1–G5 (render_r3.md) — closure check
- **G1 closed.**
  - The catch-up line is now "one added-seat line for the current term on record, from the term start date to the term end date, on every billing plan".
  - "The catch-up months are the calendar months from the term start date to the term end date, the months the line covers"; compute `catch_up_months = MONTHS(term_start, term_end)` on every plan.
  - The tool books `period_start=term_start, period_end=term_end` on every plan, so the line is counted by "the seats on added-seat lines whose period end is the term end date". The late gate is reachable and the catch-up cannot repeat.
  - On annual_monthly_billing the line now prices seat_price_annual_monthly_billing × 12 × the days-to-term-end fraction, coherent with a line that covers the rest of the term.
- **G2 closed.**
  - Compute: `credit_basis` = the opening amount (or the list credit), `credit_count` = term months on annual_monthly_billing (else 1), `term_credit = RND((credit_basis − carried fees) × credit_count × fraction)`.
  - Rule: "The term credit is the credit basis less every fee taken off it, times the months it is counted for…"; "…the credit basis is its amount, counted for each of the calendar months…".
  - Fees are taken off the instalment once, before it is multiplied, matching "a fee is … never of what a term is credited".
- **G3 closed.** The rule's first clause and every scheduled-product ladder tier now carry "where no upgrade line whose period end is the term end date belongs to the current term", in both reactivation and term renewal. The ladder, rule and compute agree, with first-match order preserved.
- **G4 closed.**
  - `scheduled_seats` is now in the bindings of reactivation_seat_basis, term_renewal_seat_basis and catch_up_seat_basis.
  - Mechanical sweep over all five policies: the only plain binding read solely by factor bindings is the Pro upgrade's `open_charge_date`. It is shared by two factors (carried late fee, carried reinstatement) and defined once by its own sentence, which is correct under XF A2/A3 and accepted by the renderer.
  - No factor binding reads another factor's binding.
- **G5 closed.** The `pay_late_mail_renewal_a889cd52` docstring now reads "Collect … the renewal of an active email subscription that falls due on its term end date, whether it is billed on or before that due date or, overdue, after it went unpaid", which matches the term-renewal scope.

### class sweep (revision_15)
- Every class raised in revisions 1–14, plus the renderer classes F1–F4 and G1–G5, was re-checked across the whole charter: clean.
- Factor counts are unchanged (6/5/4/5/5), each with >= 2 parameter and >= 1 method. Owner (b), trigger rule, uuid8s, docstring format-only and rounding are unchanged.

## closing_checklist (revision_15)
- Renderer findings G1–G5 are closed.
- Both task comparisons PASS. 5/5 policies are covered with disjoint scopes.
- Trees and owner (b) are as revision_14. All 25 factors bear weight. Ledgers are complete. XF 21 clean.
- Gates: `/tmp/erl0076_coord/snap_professional_email_seats_r15.txt` 7/7 OK. check_traceability is deferred to the coordinator.
- Final sweep of every class raised in revisions 1–15 and of the renderer findings: no member open.
- Disclosed: in revision_15 the per-task freeze sections were written after tasks/*.json were opened. The derivations carry forward unchanged inputs from revision_12–14.

VERDICT revision_15: task0=PASS task1=PASS charter=CLEAN

## revision_16

## charter_global_frozen (revision_16)
- Entry: worklog tail reads `REWORK round 16: gates 7/7 green`. Snapshot `/tmp/erl0076_coord/snap_professional_email_seats_r16.txt` (run by me, execute-only) prints all 7 gates OK. Claims read by item id only: SR-1, BL-1, the src items of audits/policy_kb/professional_email_seats/VERDICT.md revision_2 (read in full; no scored values).
- Hashes:
  - `email.extended.yaml` 86f1a7059a16c99a267aa8f214e846f974db0bf69cc2d2f12b689d141453d74d (changed);
  - `task_tools.py` ff9caa38… (unchanged since revision_15);
  - 0.view f77e9880db7798b5c93714be46abe9bdbf298a0ba3f35c2ba8d34a9af2897502;
  - 1.view f095db52f71f9049f0729ed478de8ea84cf0e9320a6aa15dbc46724f6e85653e (both re-seeded: account ledger only).
- Charter re-derived. Base verbatim. Mechanical sweep clean. The sentence-level diff against revision_15 is limited to the Pro upgrade's opening-charge-date selection (BL-1). Every other rule, compute, param and ladder is identical.

### BL-1 closure
- The plain binding `open_charge_date` and its sentence ("The opening charge date is … ; a fee is part of what that charge billed but never of what a term is credited") are removed.
- Each fee factor now carries the selection inside its own sentence: "…to the charge date of the opening renewal charge (the renewal charge whose period start is the term start date)…". Compute `late_fee_days` and `suspended_days_then` each read the `LATEST(...)` selection directly.
- Nothing on the computation-document surface now signals the fee factors. **BL-1 closed.**
- Observation O20: the same selection is now stated twice, once in each fee factor's sentence, rather than once as a shared plain binding (XF A2). I record this as an observation, not RED. The render rule requires each factor document to stand alone, and BL-1 required the selection off the baseline surface, so the two requirements are met together only this way. Both statements are identical and give the same row.

### SR-1 closure (seeded ledgers) and self-disclosure
- Self-disclosure: SR-1 is a member of the credit-first ledger class I raised in revision_1 (F1-2). I missed it in revisions 12–15. The scheduled Starter downgrade, introduced in round 12, made each October on-time attempt cheaper than the credit on record:
  - task 0: 17 seats at the Starter monthly price with Bronze, below 73.35;
  - task 1: 21 seats at the Starter monthly price with Bronze, below 73.34.
  - So the account charter's "Every auto-renew charge in any category tries credit first … Credit pays a charge only when credit_balance covers the whole charge" would have paid them, and the seeded declines could not occur.
- The rework adds an `account_credit_withdraw` of the whole remaining balance before the attempts:
  - task 0: 2026-09-24, against the 2026-04-10 deposit;
  - task 1: 2026-09-30, against the 2026-04-08 deposit;
  - balances become 0.00.
- Checked against account_withdrawals:
  - account active;
  - one withdrawal per deposit (original_credit_entry_id set);
  - inside withdrawal_window_days = 180 (day 167 and day 175);
  - amount = the deposit's unused remainder (500 − 5 × 85.33 = 73.35; 500 − 6 × 71.11 = 73.34), at or above withdrawal_min_amount 5.00;
  - returned to the original card (funding_method card).
- account_balance_sync gives credit_balance 0.00. Bronze qualification is unaffected (account_msr_deposits_365d subtracts only charge-backs).
- With credit 0.00, each October attempt goes to the card and is declined, as seeded. **SR-1 closed.**
- Class sweep of the credit-first ledger class (every seeded charge in both tasks against credit-first and "credit only when the customer chooses" for in-conversation charges): clean.
  - Task 0: 04-01 auto-renew by card (before the deposit); 05-01..09-01 from credit, each covered; 04-20 added seats by card (not an auto-renew); 10-01 attempt with credit 0.
  - Task 1: 03-13 by card (before the deposit); 04-13..09-13 from credit; 10-13 attempt with credit 0.

### other classes (r16)
- Every class raised in revisions 1–15 and the renderer and KB items, re-checked across the whole charter: clean.
- Factor counts are unchanged (6/5/4/5/5).

## closing_checklist (revision_16)
- KB src items SR-1 and BL-1 are closed.
- Both task comparisons PASS. 5/5 policies are covered with disjoint scopes.
- Trees and owner (b) are as before. All 25 factors bear weight. Ledgers (account + email) reproduce under the charters, including credit-first and the new withdrawals. XF 21 clean.
- Gates: `/tmp/erl0076_coord/snap_professional_email_seats_r16.txt` 7/7 OK. check_traceability is deferred to the coordinator.
- Final sweep of every class raised in revisions 1–16, plus renderer F1–F4, G1–G5 and KB XP-1, SR-1, BL-1: no member open.
- New observation: O20 (the shared opening-charge selection is stated in both fee factors).

VERDICT revision_16: task0=PASS task1=PASS charter=CLEAN
