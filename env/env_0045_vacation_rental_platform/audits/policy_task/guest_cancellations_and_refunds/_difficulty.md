# Policy-task audit — guest_cancellations_and_refunds / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. This auditor did not write the audited artifacts.
- Freeze time of this section: 2026-10-07T19:19:44Z. Written before any task's GT was revealed. Nothing below derives from `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract` or `worklog.md`.
- Frozen inputs (sha256, matching the coordinator's SHA256SUMS):
  - `tasks/guest_cancellations_and_refunds/stay.extended.yaml` `8b4135a71c747a261f85110775e1e0b542bde3a7daf0fecfa75e34706873b202`
  - `tasks/guest_cancellations_and_refunds/task_tools.py` `a280571e861a4d61089f7665a52f0aafbcf6e9fcda182d0a7a768f3c5ca1d82e`
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (tool list), `blueprint/products/stay.yaml`, `blueprint/products/rewards.yaml` (variants, events, policies), `blueprint/products/payout.yaml` (`payout_evt_release` only), the extended charter, `task_tools.py`, the masked views `/tmp/erl45_views/r1/guest_cancellations_and_refunds/task_{0,1}.view.json` (frozen_time, user_scenario, initial_state), and the compute DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`).
- Fields masked and not read: every task JSON under `tasks/guest_cancellations_and_refunds/tasks/`, `worklog.md` (difficulty and scenario), any other scenario, any sibling difficulty's tasks directory, prior audits.

### Entry conditions (Step 0)

Gate snapshot supplied with the brief (`/tmp/erl45_views/r1/guest_cancellations_and_refunds/gate_snapshot.txt`): check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability NOT OK (declared expected before KB rendering). Masked views and hashes supplied; recomputed sha256 of both views and both shared artifacts match SHA256SUMS. Entry conditions complete. A green gate is only the qualification for this manual audit.

Base-copy check: `diff <(head -1328 stay.extended.yaml) blueprint/products/stay.yaml` differs only by the trailing blank line; the base section is a verbatim copy.

### policy_conflict_scan

Extended policies (7), their target tools and the problem each solves:

| id | target_tool (owner) | computes |
| --- | --- | --- |
| stay_ext_departure_notice_charge | pay_notice_charge_caff8891 (user) | amount |
| stay_ext_departure_pet_fee_refund | refund_pet_fee_41a7068c (agent) | amount |
| stay_ext_departure_extra_guest_fee_refund | refund_extra_guest_fee_b492f389 (agent) | amount |
| stay_ext_departure_service_fee_refund | refund_service_fee_f4bed6e4 (agent) | amount |
| stay_ext_first_installment_payment | pay_first_installment_26275b3d (user) | amount |
| stay_ext_travel_issue_nightly_refund | refund_travel_nightly_d238de09 (agent) | amount |
| stay_ext_travel_issue_service_fee_refund | refund_travel_service_fee_041715de (agent) | amount |

Subjects and triggers: the four departure policies all hang on a guest cancellation (refund_reason guest_cancellation, no request); the three travel/installment policies hang on an approved travel_issue request and a declined installment 1. The two groups do not overlap on charge component + refund_reason (departure: pet_fee / extra_guest_fee / guest_service_fee x guest_cancellation; travel: nightly / guest_service_fee x travel_issue), so the base dedup keys (`one_guest_refund_per_component`) never collide between groups.

Time anchors: departure policies anchor on `stays.cancelled_at` vs `check_in_date` (date part); travel policies on `stay_requests.submitted_at` vs `check_in_date`; first installment on the failed-payment grace period (`stay_evt_payment_schedule.lapse_after_grace`, inherited, not overwritten). Compatible.

Cross-category reads: every extended policy reads the Rewards category (active tier's `dedicated_concierge` / `priority_support_line`, and `rewards_transactions` redeemed / reinstated / earned). Rewards is a product with no difficulty of its own in `blueprint.yaml` (difficulties: stay, listing, host, payout, protect). See finding F-8.

Overlaps resolved by the charter:
- Base `stay_agg_service_fee_refund_cap` is not overwritten anywhere; the departure service-fee policy supersedes only the clause of `stay_evt_guest_cancellation_refund` that ended "always subject to stay_agg_service_fee_refund_cap". The cap policy is a separate base policy still in force over every guest-cancellation service-fee refund, so the merged semantics are: compute per the departure rule, then apply the cap. Unique; observation only (F-9).
- The credit-funded part (card share of a refund) in five extended policies vs base `stay_evt_refund_settlement` ("Roamhaven never pays a stay refund in cash, travel credit or to another card"): the Rewards charter's own `rewards_evt_reinstatement` already returns redeemed credits "in the proportion that the refunded amount bears to the stay's total_price"; the extended card share `1 - redeemed/total_price` is exactly that split, so the credit part goes back to the means it was paid with. Read as consistent with existing cross-charter logic; observation (F-10).

Scope partition (derived from the prerequisite graph, before reveal): two connected components — {notice_charge, pet_fee_refund, extra_guest_fee_refund, service_fee_refund} and {travel_issue_service_fee_refund, travel_issue_nightly_refund, first_installment_payment}. With M=2 these are the natural two task scopes; they are disjoint and together cover all 7 extended policies. To be confirmed against `charter_scope` after the reveal.

Claimed scope vs blueprint: event types claimed are stay_guest_cancelled, stay_payment_lapse_cancelled, stay_altered, stay_payment_collected, stay_refund_issued. The task tools write only stay_payment_collected and stay_refund_issued; nothing in this difficulty writes stay_guest_cancelled, stay_payment_lapse_cancelled or stay_altered. Coverage of the claim is a blueprint/instantiation matter, not one of the four relationships; recorded as observation O-5.

### rule_compute_equivalence

Swept every compute binding of every extended policy back to its `compute_basis` quotation and the quotation to the rule (mechanical check: every `policy_source`, every `replaced_by` and every `baseline.rule` sentence is verbatim in the policy's own rule; every `superseded_clause` is verbatim in its base rule). Results per policy:

- notice_charge: every binding has a basis. `installments_collected` = collections minus installment 0 rows matches "every installment collected on the stay covers installment_nights nights" read with base's event definition ("0 for an alteration increase"). `kept_nights = cancel_offset + 1 + notice_count` matches "the nights up to and including the cancellation date plus the notice nights counted". `notice_tax` three branches match the three-tier sentence. Equivalent.
- pet_fee_refund / extra_guest_fee_refund: equivalent. Charter-global edge (no task bearing): on a monthly stay cancelled well before check-in, `pet_refundable_nights = nights - cancel_offset - 1 - notice` grows past `nights` (cancel_offset negative), so the tier-1 share exceeds 1; the rule says the same ("the nights dated after the cancellation date and before the check-out date"), so rule and compute agree, and base `stay_evt_refund_settlement` caps at the amount collected. Observation O-1.
- service_fee_refund: compute equivalent to the ladder, but the rule's opening sentence scopes the policy to "a guest cancellation dated on or after the check-in date", while the `refunded_fee_base` ladder carries a tier "on a cancellation dated before the check-in date". The superseded base clause covered every cancellation outside the full window; its replacement names only on/after check-in. A pre-check-in partial-window cancellation is therefore governed only by a tier of a policy whose scope sentence excludes it. No consequence in either task world (task 0 is cancelled on the check-in date; task 1 is not a cancellation). Finding F-7 (observation for these tasks).
- first_installment_payment: `nights_carried` is `nights_booked` for every non-monthly stay, including pay-part-now, so the flat per-night tax on a pay-part-now installment 1 counts every night in full, while the rule says "the flat amount for each night installment 1 carries" and base says installment 1 "collects pay_part_now_deposit_pct of every component". Ambiguous on pay-part-now stays in a flat-tax jurisdiction (TN-NASHVILLE only); no bearing on task 1 (CO-DENVER, exempt, monthly). Observation O-2.
- travel_issue_nightly_refund: on pay-part-now stays `covered_affected_nights` is fractional and the first affected night is still taken whole at `arrival_night_pct`; the rule says "it covers the affected nights at pay_part_now_deposit_pct percent" and "the first affected night is treated on its own" without saying whether the deposit percentage reaches the first night. Ambiguous on pay-part-now only; no bearing on task 1 (monthly). Observation O-3.
- travel_issue_service_fee_refund: equivalent.

Every factor ladder: each tier the `ladder` names is a sentence of the rule and a branch of the `decides` binding, and each branch is a tier of the rule (checked per factor, 32 factors). No tier lives only in compute.

Rounding: rules say "half up"; the DSL's `RND` is Python `round` on binary floats. On both task worlds no computed amount lands on an exact half cent (checked by computing both ways), so no consequence.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (7 tools, 7 policies).
- Tool bodies (`task_tools.py`): each body looks up the stay's guest, makes an id, and creates one `stay_transactions` row with the values passed. No body checks eligibility, prerequisite state, amount, order or ownership; none raises or hints. The module docstring says so explicitly.
- Docstrings name no other tool, state no position in a sequence. `pay_first_installment_26275b3d` says "for example after the automatic collection of that installment was declined by their card" — an ordering word attached to a business event, not to another write; observation O-4. `refund_travel_nightly_d238de09` and `refund_travel_service_fee_041715de` describe their `stay_id` argument as "the stay ... whose pet fee is refunded" (copy-paste from the pet-fee tool); misleading wording, no change to any answer; observation O-4.
- uuid8s: caff8891, 41a7068c, b492f389, f4bed6e4, d238de09, 041715de, 26275b3d — seven distinct values, no shared prefix or tail, no sequential pattern. Pass.

### prerequisite_graph

Edges (problem <- prerequisite):

| blocked policy | prerequisite problem | kind | gate | form |
| --- | --- | --- | --- | --- |
| departure_notice_charge | departure_pet_fee_refund | state_gate | stay_transactions.charge_component | state |
| departure_notice_charge | departure_extra_guest_fee_refund | state_gate | stay_transactions.charge_component | state |
| departure_notice_charge | departure_service_fee_refund | state_gate | stay_transactions.charge_component | state |
| departure_service_fee_refund | departure_pet_fee_refund | value_input | sf_addon_refunds | state |
| departure_service_fee_refund | departure_extra_guest_fee_refund | value_input | sf_addon_refunds | state |
| travel_issue_service_fee_refund | travel_issue_nightly_refund | value_input | travel_fee_nightly_refunds | state |
| travel_issue_nightly_refund | first_installment_payment | value_input | travel_installments_collected | state |

- `prerequisite` is filled on every policy (`[]` on pet, extra, first_installment). Every `problem` is an extended policy id of this file, never a base policy, never itself. The graph is acyclic (two components, depth 2 and 2).
- Every `policy_source` is verbatim in the blocked policy's own rule (mechanical check). `form: state` on all seven; no `fallback_reason` anywhere, none required.
- `resolved_by` equals the depended-on policy's `target_tool` on all seven edges.
- `value_input` gates name real bindings: `sf_addon_refunds` (service_fee compute), `travel_fee_nightly_refunds` (travel SF compute), `travel_installments_collected` (travel nightly compute). The three `state_gate` edges point at a field path (`stay_transactions.charge_component`) rather than at an eligibility entry; extended policies carry no eligibility list, so the gate is the prerequisite sentence itself. Observation only.
- Conditions: neither strengthened nor weakened relative to the sentences (each departure condition adds "whenever the ... refund the departure rules give is above 0.00", which is what "the refund owed" means once base's "A component whose refund comes to 0.00 posts no row" is applied). No authoring-viewpoint phrasing.

### prerequisite_sentences

Four-point test on each sentence:

1. "The notice charge is not collected until the stay's ledger carries the guest-cancellation refund owed on the stay's pet fee." — connective "not ... until"; waited-on state = a guest-cancellation pet_fee refund row on the stay's ledger (record-visible, words of the ledger); no tool / id / snake_case; strength matches condition. The one write of this difficulty that books a guest-cancellation pet-fee refund is the pet-fee policy's (its rule: "part of the pet fee is refunded ... as a pet-fee refund"). Single reading.
2. Same for extra-guest fee -> the extra-guest-fee policy. Single reading.
3. Same for "the guest-cancellation refund owed on Roamhaven's guest service fee" -> the departure service-fee policy (the travel SF policy books refund_reason travel_issue, not a guest-cancellation refund). Single reading.
4. "The guest-service-fee refund on a cancellation is fixed only after the stay's ledger carries the pet-fee refund that cancellation owes." — "only after"; state form; single writer (pet-fee policy).
5. Same for extra-guest fee.
6. "The nightly refund of a travel issue is not fixed until the stay's ledger carries the collection of every installment whose first night has arrived." — "not ... until"; state = collection rows for every installment whose first night is on or before today. Writers in this difficulty that create collection rows: `pay_first_installment` (first_installment policy) and `pay_notice_charge` (notice-charge policy, which by its own rule applies only to a stay already cancelled by the guest). On a live checked-in stay only the first-installment policy's rule ("the guest pays installment 1 ... recorded as installment 1") brings the state about. Single reading.
7. "The service-fee refund of a travel issue is fixed only after the stay's ledger carries the nightly refund of that travel issue." — single writer (travel nightly policy).

No depended-on rule restates any of these sentences; no rule names another policy id or tool. No undeclared cross-problem order found in any extended or base rule (base sentences such as "installments not yet collected are cancelled" state no order between this difficulty's problems).

Realism of the prerequisite settings (brief's priority): (a) charging a departure notice only once the departure refunds are on the ledger, and fixing the service-fee refund only once the add-on refunds it is a percentage of are booked, are ordinary settle-then-charge practice; (b) requiring the declined installment 1 to be collected before a travel-issue nightly refund is fixed follows existing base logic — `stay_evt_refund_settlement`: a refund "never exceeds the amount of that component collected on the stay net of earlier refunds of it". The blueprint's own difficulty summary routes "a missed monthly installment on a stay already in progress" to a human (POLICY_NOT_COVERED); a stay checked in on the day its declined installment 1 is still inside the 48-hour grace period sits at the edge of that sentence. The charter (not the summary) governs and the extended rule covers the case explicitly; observation O-6.

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry.

- notice_charge (refs: payment_schedule, alteration, guest_cancellation_refund, booking_terms). Declared: "installments not yet collected are cancelled and never collected"; the "lesser of collected" clause; "Money is collected only on a confirmed or checked-in stay." Not declared: `stay_evt_payment_schedule` "the cleaning, pet and extra-guest fees are collected with installment 1, and each installment carries the guest service fee and occupancy tax attributable to the amounts it collects" together with `stay_booking_terms` "The guest service fee is guest_service_fee_pct of the service-fee base when the stay's fee_structure is split_fee". The notice charge is, by its own rule, "booked as the installment that covers the first unpaid notice night"; the Rewards relief (`rewards_fee_relief`, 50 or 100 percent off the notice charge's guest service fee) makes that installment carry less than the fee attributable to what it collects. Undeclared override -> F-1.
- pet / extra (refs incl. refund_settlement): declared the add-on proportional sentence. Deep-clean / linen share, Rewards courtesy, monthly share and credit-funded part all act on the quantity that sentence governed. Merged semantics unique. The credit-funded part vs `stay_evt_refund_settlement` handled in policy_conflict_scan (consistent with `rewards_evt_reinstatement`).
- service_fee (refs incl. cap, booking_terms): declared the proportional SF sentence and the two travel / MDE eligibility clauses (replaced by supersets). Base full-window sentence ("every component is refunded in full, the guest service fee included") not hit and still in force; the extended tier for pre-check-in cancellations gives standard_refund_fee_pct x (all refunded components) which equals the fee on the full base up to rounding, so no conflict in full-window cases. Scope contradiction F-7.
- first_installment (refs: payment_schedule, alteration, booking_terms), `overwrite: []`. Not declared: the same base sentence as above ("each installment carries the guest service fee ... attributable to the amounts it collects") and `stay_evt_payment_schedule` "Under pay_in_full the whole total_price is collected as installment 1"; the extended rule spares Rewards members 50 or 100 percent of installment 1's guest service fee. Undeclared override -> F-1. (Credits taken off installment 1 are consistent with `rewards_evt_redemption`: "on a monthly-installment stay they apply to installment 1 only".)
- travel nightly: declared the affected-nights / percentage sentence; uplifts, first-night treatment, coverage and credit part act on that quantity. Unique.
- travel SF: declared the SF / tax proportion sentence. Unique.

No anonymous intermediate factor, 0/1 multiplier or dropped branch found beyond F-1.

### factor_ladders

Counts per computation (declared): notice 6 (3 parameter / 3 method); pet 5 (3/2); extra 5 (3/2); SF 4 (2/2); first installment 4 (2/2); travel nightly 6 (4/2); travel SF 4 (2/2). Every ladder has 3 tiers, pairwise disjoint as stated, fall-through equal to the baseline binding. Bindings within a policy are disjoint; `decides` is never `result`. Every tier is stated in the rule and implemented in compute. `cross_difficulty: rewards` on 2-3 factors per policy.

Multi-source (every non-fall-through tier a compound over distinct records): pet/extra `*_refund_share` (stays.payment_plan + stay_transactions collections), all `*_credit_funded_part` (redeemed rows + reinstated rows), SF `arrival_night_courtesy` and travel SF `travel_fee_arrival_courtesy` (cancellation/submission date + Rewards tier), travel SF `travel_fee_base_by_issue` tier 2. Each component has at least one.

Label honesty: all `method` factors change the algorithm (coverage scope, fee-base composition, tax treatment, share formula, card-share formula); all `parameter` factors change a number. `travel_first_night_treatment` (parameter) has a fall-through "the same share as the other affected nights" — a reference rather than a number, still a value. Pass.

Real-ladder tests (conditions that business weighs, tiers no reaching customer can occupy, outcomes no business would publish):

- **notice_charge — ladders restating the policy's scope (F-2).** A notice-charge write exists only when an unpaid notice night exists on a stay already in progress. By the charter: monthly installments exist only on Long-Term (`monthly_installments_available: true` only there; Long-Term `pay_part_now_available: false`); a pay-in-full stay collects every night at confirmation; a pay-part-now balance is due `balance_due_days_before_check_in` (14-35) days before check-in and an unpaid balance lapses the stay after `failed_payment_grace_hours` (48) — before check-in, since pay-part-now needs a 21+ day lead. So every customer who reaches a notice-charge write is on a Long-Term stay (>= long_term_min_nights) paid in monthly installments. Then: `notice_length` tier 1 ("long_term_min_nights nights or more") holds of every such customer and its tiers 2 and 3 are never occupied; `notice_night_coverage` tier 1 ("paid in monthly installments") holds of every such customer, tier 2 (pay-part-now, balance uncollected) is never occupied on an in-progress stay and tier 3 always yields a zero charge; `notice_fee_rate` tier 2's part "long_term_min_nights nights or more" holds of every such customer and the fall-through (standard 14.20 for shorter stays) is never occupied; `notice_fee_base` tier 2 (pay-part-now) is never occupied and tier 1's part "paid in monthly installments" holds of every such customer. Surviving factors: `notice_tax_exemption` (method; stays of 28-29 nights or in FL/HI with 180+ exempt minimums are genuinely non-exempt) and `rewards_fee_relief` (parameter); `notice_fee_base` survives at most as a two-tier split (installment 1 collected or not). That is 2 (at most 3) factors and 1 parameter — below 4 factors and 2 parameters. SOURCE-FACTOR RED on the notice-charge computation.
- **service_fee — fall-through contradicting the rule's own reason (F-3).** `refunded_fee_base` tier 1 includes pet and extra-guest refunds for a monthly stay "whose collections have begun and so prepaid its pet and extra-guest fees"; the fall-through (any other cancellation on or after check-in, i.e. every pay-in-full stay) counts nightly refunds only. Base: "Under pay_in_full the whole total_price is collected as installment 1 when the stay is confirmed" — a pay-in-full stay prepaid its pet and extra-guest fees too, and base `stay_booking_terms` charged the guest service fee on them ("service_fee_base_components: [nightly_subtotal, cleaning_fee, pet_fee_total, extra_guest_fee_total]"). The condition that switches add-on refunds into the fee base (payment plan) is not what the business weighs, by the rule's own stated reason, and the fall-through withholds the service fee on refunded add-ons from the most ordinary customer. SOURCE-FACTOR RED (unreal ladder) on the SF computation; demonstration in task 0's file.
- **travel nightly — non-monotone first-night tier (F-4).** `travel_first_night_treatment` tier 2: "when it was submitted on the day after the check-in date, the first affected night is refunded at arrival_next_day_pct percent" (75), while the fall-through gives the same share as the other nights. For a no_access or uninhabitable issue (`severe_issue_refund_pct` 100) reported the day after check-in, every affected night is refunded at 100 except the first, at 75 — a guest who could not get in is refunded less for the first night they were locked out than for the later ones. No rental business publishes that treatment. SOURCE-FACTOR RED (unreal tier outcome), charter-global; task 1 sits on tier 1, and after striking this factor its computation still has 5 factors (3 parameter / 2 method), so the bound survives there.
- Observations (not RED): Rewards-tier courtesies keyed to "includes a dedicated concierge" / "includes the priority support line" are proxies for the tier name (Diamond/Ambassador, Gold/Platinum); the travel SF misrepresented tier adds the whole cleaning fee to the fee base although the cleaning fee itself is not refunded for that category, justified in the rule ("Roamhaven answers for the listing it published"); the departure SF arrival-night courtesy adds part of an unrefunded night to the fee base. Goodwill policies a marketplace could publish. O-7.

Cross-difficulty: every policy's cross-category factor reads the Rewards category, which no difficulty of this scenario claims (F-8, observation).

### findings

- **F-1 SOURCE-POLICY RED — undeclared override of the installment service-fee sentence.** Symptom: two extended collections reduce the guest service fee base says an installment carries. Root cause: `stay_ext_departure_notice_charge` (rule: "Roamhaven Rewards members get relief on the guest service fee of a notice charge ...", with "The notice charge is booked as the installment that covers the first unpaid notice night") and `stay_ext_first_installment_payment` (rule: "Roamhaven Rewards members get a courtesy on the guest service fee of installment 1 ... spared installment_fee_courtesy_priority_pct percent of it") deviate from base `stay_evt_payment_schedule` "each installment carries the guest service fee and occupancy tax attributable to the amounts it collects" (and, for pay-in-full, "the whole total_price is collected as installment 1"), and neither `overwrite` names that sentence (notice_charge names only "Money is collected only on a confirmed or checked-in stay." from that policy; first_installment has `overwrite: []`). Bears on: task 0 (notice charge) and task 1 (installment 1); consequences demonstrated in each task file.
- **F-2 SOURCE-FACTOR RED — notice-charge ladders restate the write's scope.** As above. Bears on task 0 (root computation).
- **F-3 SOURCE-FACTOR RED — departure SF fee-base fall-through.** As above. Bears on task 0.
- **F-4 SOURCE-FACTOR RED — travel first-night tier 2 outcome.** As above. Bears on task 1 (declared factor of its computation; bound survives after striking).
- F-5 (observation) — parallel order on the credit-funded part: tier 2 of every `*_credit_funded_part` divides by "the stay's total price less the amounts already refunded on it", so when credits have been partly reinstated the pet-fee and extra-guest-fee refunds (no edge between them) depend on which is posted first. Neither task world has a reinstatement row on the target stay, so no task has two terminal states. Charter-level latent defect.
- F-6 (observation) — the credit-funded part "goes back as credits", but no write of this difficulty reinstates credits; the terminal state will show the card refund but no `rewards_credit_reinstated` row. Not scored; not a second answer.
- F-7 (observation for these tasks) — departure SF scope sentence vs pre-check-in tier (see rule_compute_equivalence).
- F-8 (observation) — `cross_difficulty: rewards`: Rewards is a product of the blueprint but no difficulty claims it, so "another difficulty's records" is satisfied only in the sense of another product's records.
- F-9 (observation) — the superseded SF clause carried "always subject to stay_agg_service_fee_refund_cap"; the cap remains in force through its own base policy. Task 0's count is checked in its file.
- F-10 (observation) — credit-funded card share vs `stay_evt_refund_settlement` "never ... travel credit": consistent with `rewards_evt_reinstatement`; no second answer.
- O-1 .. O-7: see sections above.

## closing_checklist

Written 2026-10-07T19:25:37Z, after both tasks' comparisons. Everything above this heading was frozen at 19:23:26Z (sha256 2353c5e6788cdb61e1bab4956e8937e12eef9c0c5bf58fa79acbe7804a063125) before any reveal and is unchanged.

**The difficulty does not close: neither task passes all four relationships.**

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (F-1: 115.33 vs 121.86) | tree holds; SOURCE-CHAIN RED on a false proof assertion (installment-0 row omitted) | SOURCE-FACTOR RED (F-2, F-3) | equal to GT apart from F-1; SOURCE-TASK RED on a false proof assertion (958 vs 953.97 h) | RED |
| 1 | SOURCE-POLICY RED (F-1: 3648.80 vs 3857.60) | PASS | SOURCE-FACTOR RED (F-4, charter-global, no numeric consequence) | equal to GT apart from F-1 | RED |

Checklist state:
- Per-task files: `task_0.md`, `task_1.md`, one per task, next to this file; revision 1, no older revision. Neither comparison section carries a PASS.
- Coverage and scope: the 7 extended policies are fully covered; `charter_scope` of task 0 {notice, pet, extra, SF} and task 1 {first installment, travel nightly, travel SF} are pairwise disjoint and match the two connected components of the prerequisite graph; task tools and GT are closed; 7 independently generated uuid8s. Met.
- Problem trees: task 0 n=3 with 2 value_input edges, task 1 n=2 with 2; each has an owner=user write; the difficulty's prerequisite edges form a DAG. Met (task 0's proof field defect noted).
- Factors: not met — the notice-charge computation falls below 4 valid factors and 2 parameters (F-2); the departure SF fee-base ladder (F-3) and the travel first-night ladder (F-4) fail the real-ladder test. All declared factors bear weight numerically on their worlds and every baseline alone gives a definite non-gold number (figures agree with GT to the cent).
- Gate re-run on the final form: not applicable — the artifacts are unchanged since the brief's snapshot (hashes re-verified) and the difficulty is not closing; this audit does not run the instantiation gates.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent auditor as revision 1. Started 2026-10-07T21:09:28Z; this section was written 2026-10-07T21:11:53Z, before any round-2 task JSON was opened. Revision 1 above is left untouched.
- Inputs (sha256 recomputed and matching the coordinator's SHA256SUMS): `stay.extended.yaml` `ed0b001cffbc1812f0c37669d55a2e0f2ee24ddc36bdc6883da825773d6014a1` (changed from 8b4135a7…), `task_tools.py` `bbb8e9e19907e10f7c5362550562f2d10da39a1a554e865e51daa5de3264b7bb` (changed from a280571e…). Both shared inputs changed, so the charter-global sections are re-derived in full below, not carried forward.
- Masked views: `/tmp/erl45_views/r2/guest_cancellations_and_refunds/task_0.view.json` `4c7fe623…7a` (changed; the only difference from r1 is `stay_transactions.01eb841f….amount` 3990.08 -> 3772.04), `task_1.view.json` `0cf409af…56` (unchanged from r1).
- Gate snapshot (r2/gate_snapshot.txt): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, TRACEABILITY NOT OK (expected before rendering). Entry conditions complete.
- Base copy still verbatim (`diff` against `blueprint/products/stay.yaml`: trailing blank line only).
- contamination_disclosure: the round-1 GT of both tasks was revealed to this auditor in revision 1 (19:24:22Z), so the r1 gold values and r1 conventions are known. The round-2 task JSONs have not been opened. Wherever a round-2 figure below equals an r1 gold figure, it was recomputed from the r2 charter and r2 views, not copied.

### re-derived charter-global checks (revision 2)

Mechanical (temporary script, since removed): every `policy_source` is verbatim in its own rule; every `superseded_clause` is verbatim in its base policy; every `replaced_by` is verbatim in the extended rule; every `baseline.rule` sentence is in the rule; every ladder has 3 tiers. Factor counts: notice 6 (5 parameter / 1 method), pet 5 (3/2), extra 5 (3/2), service fee 4 (3/1), first installment 4 (2/2), travel nightly 6 (4/2), travel SF 4 (2/2).

- **policy_conflict_scan.** Same 7 policies, tools and two connected components as in revision 1; scopes partition the same way. Policy overlaps: unchanged except as below.
- **rule_compute_equivalence.** Swept every changed binding:
  - notice charge (rewritten): kept nights = nights through the cancellation date + notice nights + `later_kept_pct` of the later nights; paid nightly by plan (monthly: collected installments x installment_nights; pay-part-now: deposit share until installment 2; otherwise the whole subtotal; 0 before installment 1); owed nightly = kept price - paid, floored at 0; owed fees and credit offset only when installment 1 was never collected; fee relief = Rewards + returning-guest relief, capped at 100. Every binding has its quotation; no empty promise.
  - pet / extra: `MN(nights_booked, …)` caps the refundable nights at the stay's nights, matching "the nights dated after the cancellation date and before the check-out date" (O-1 closed). The tier-2 card share is now `1 - (redeemed - reinstated) / total price` in rule and compute.
  - service fee (rewritten): fee base = nightly + cleaning + pet + extra guest-cancellation refunds ("every amount the guest service fee was charged on"); share returned 50 / 75 / 100 by cancellation date; arrival courtesy added in full; matches the rule. The rule also says "always subject to the service-fee refund cap"; compute does not evaluate the cap, which lives in base `stay_agg_service_fee_refund_cap` (in force, not overwritten). Observation R2-O1 (rule sentence with no counterpart in this policy's compute; no consequence where the count is below 3).
  - first installment: `nights_carried` on pay-part-now = nights x deposit %, now stated in the rule ("a pay-part-now installment 1 carrying pay_part_now_deposit_pct percent of each night's flat amount") — O-2 closed. Courtesy limited to monthly stays in rule and compute.
  - travel nightly: pay-part-now covers "every affected night, the first included, at pay_part_now_deposit_pct percent" and `arrival_in_scope` = deposit share — O-3 closed. First-night tier 2 = `MX(75, share)` in rule and compute.
  - travel SF: credit tier 2 changed as above; otherwise unchanged.
- **action_binding_and_uuids.** Same 7 `(target_tool, computes)` pairs, same 7 uuid8s. Tool bodies still only create the row (no `if`/`raise` anywhere in `task_tools.py`). Docstrings: the two travel tools now describe `stay_id` as the stay "whose travel-issue nightly / service-fee refund is booked"; `pay_first_installment` no longer carries "for example after …" (O-4 closed). `pay_notice_charge` docstring restates the filing rule ("1 when no installment was ever collected on the stay"), which matches the policy rule; observation only.
- **prerequisite_graph / prerequisite_sentences.** Edges, kinds, gates, forms, `resolved_by`, conditions and sentences are unchanged from revision 1 and re-verified verbatim. Gate bindings still exist (`sf_addon_refunds`, `travel_installments_collected`, `travel_fee_nightly_refunds`). Acyclic. The single-writer argument still holds; the notice charge can now also be filed as installment 1 on a stay whose installment 1 was never collected, but it is collected only on a stay already cancelled by the guest, so it never brings about the travel-nightly sentence's state on a live stay.
- **override_declarations.**
  - notice charge now declares base `stay_evt_payment_schedule` "each installment carries the guest service fee and occupancy tax attributable to the amounts it collects" (replaced by the same sentence with the notice-charge relief exception) and `stay_booking_terms` exemption sentence (replaced with the kept-nights exception); the "lesser of" clause replacement keeps the clause and adds the after-check-in nightly rule (collected less the price of the nights kept), which reproduces base's after-check-in refund (unspent - notice nights) x after_check_in_refund_pct when the stay is fully paid.
  - first installment now declares the same base sentence (exception: monthly installment 1 less the Rewards courtesy, "following the guest's Rewards tier active when installment 1 is collected").
  - service fee replaces the proportional clause with "Outside the full-refund window and grace period … as a percentage of the refunded fee base, always subject to the service-fee refund cap"; the full-window sentence is still inherited.
  - **F-1: closed.** No remaining undeclared sentence governs either collection's guest service fee.
- **factor_ladders.**
  - **F-2: closed.** The notice rule now covers "a guest who checked in while the collection of installment 1 was still declined and leaves before paying it" (`paid_nightly` = 0, owed fees). That admits short stays of any tier and plan to the notice-charge write, so `notice_length` (30 / 0 / 1), `later_nights_kept` (0 / 100 - pct / 100) and `notice_fee_rate` (host-only / Long-Term split / 14.20) each divide customers who reach the write. `notice_night_coverage` and `notice_fee_base` are no longer factors (coverage is part of the baseline method). The case is legitimate under the charter: base `stay_lifecycle_progression` checks a confirmed stay in automatically on its check-in date, and base `lapse_after_grace` keeps it alive for 48 h after a failed collection; task 1's world is an instance. `later_nights_kept` restates the base after-check-in refund (`after_check_in_refund_pct`) as "kept" nights — a real ladder. `returning_guest_relief` (25 / 10 / 0 by credit earnings in 24 months): goodwill, distinct values, reads Rewards. Counts: 6 factors, 5 parameter, 1 method. Pass.
  - **F-3: closed.** `refunded_fee_base` is gone; the fee base is every refunded component the fee was charged on, for every payment plan. New factor `late_cancellation_fee_share` (on or after check-in 50; under 7 days before 75; otherwise 100): conditions are dates a marketplace weighs for late cancellations, all three tiers reachable (the policy now spans every cancellation outside the full window), distinct values. Pass.
  - **F-4: closed.** Tier 2 is now "arrival_next_day_pct percent or at the share of the other affected nights, whichever is higher", a 75 % floor, so the first affected night is never refunded less than the later ones. Observation R2-O2: where the share is >= 75 (e.g. a severe issue at 100) tier 2 gives the same value as the fall-through, as tier 1 already did at a 100 share; the tiers still differ as rules, so this is not a duplicated tier.
  - **F-5: closed** (the tier-2 card share no longer reads "amounts already refunded", so no parallel-order dependency remains).
  - F-6, F-8, F-10, O-5, O-6, O-7: not claimed changed; re-read, conclusions unchanged (O-6 is partly addressed by the first-installment rule's new "still confirmed or checked in").
  - **F-7: closed** (service-fee scope sentence now "Outside the full-refund window and grace period", covering pre-check-in cancellations).
  - **F-9:** the rule now says the cap applies; the cap is still evaluated only by its base policy (R2-O1).
- New defects found in the shared charter: none that changes a scored value or admits a second reading. Observations R2-O1, R2-O2 above.

### closing_checklist (revision 2)

Written 2026-10-07T21:14:13Z, after both revision-2 comparisons. The revision_2 charter-global section above was frozen at 21:13:14Z (file sha256 9fcce649…7445) before the round-2 reveal and is unchanged.

| task | policy self-consistency | problem tree | factors | unique solution | revision 2 verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS (F-1 closed) | PASS (proof fields corrected) | factors PASS (F-2, F-3, F-5 closed); SOURCE-FACTOR RED on one proof sentence (false counterfactual in design_rationale) | PASS (958 h corrected to 953.97 h) | SOURCE-FACTOR RED (proof field only) |
| 1 | PASS (F-1 closed) | PASS | PASS (F-4 closed) | PASS | PASS |

Round-1 claims checked: F-1, F-2, F-3, F-4, F-5, F-7, O-1, O-2, O-3, O-4, the task-0 proof fields (prerequisite_closure ledger statement; elapsed hours) and tier_taken labels — all closed as claimed. F-9 changed only in wording (the rule now states the cap; enforcement remains in base `stay_agg_service_fee_refund_cap`; R2-O1). Unclaimed items F-6, F-8, F-10, O-5, O-6, O-7 unchanged (observations). No regression: task 1's values are unchanged; task 0's pet and extra values are unchanged; task 0's SF and notice values moved only through the new declared rules (30.91, 114.02), and the reseeded installment 1 (3772.04) agrees with the declared installment-1 courtesy.

Checklist state:
- Per-task files and this file carry revision_1 untouched and revision_2 appended.
- Scope: 7 extended policies covered; task scopes pairwise disjoint; same 7 independently generated uuid8s; tools validate nothing. Met.
- Trees: task 0 n=3 / 2 value_input, task 1 n=2 / 2 value_input; one owner=user write each; the difficulty graph is acyclic. Met.
- Factors: every computation has 4-6 factors with >= 2 parameter and >= 1 method, every ladder 3 real tiers stated in its rule, every factor bears weight against an honest baseline, and each baseline alone gives a definite non-gold number (notice 6423.55, pet/extra 0.00, SF 58.27, installment 1 8692.64, travel nightly 6480.00, travel SF 302.80); multi-source and Rewards cross-category factors present per task. Met.
- **The difficulty does not yet close:** task 0 carries one SOURCE-FACTOR RED on a proof sentence (its scored solution is correct and unique). Gate re-run on the final form: the coordinator's r2 snapshot is green apart from the expected TRACEABILITY; this audit does not run gates.

## revision_3

### charter_global_frozen (revision 3)

- Same auditor. Started 2026-10-07T21:45:23Z; written before any round-3 task JSON was opened. Revisions 1 and 2 above are untouched.
- Inputs recomputed: `stay.extended.yaml` `ed0b001cffbc1812f0c37669d55a2e0f2ee24ddc36bdc6883da825773d6014a1` and `task_tools.py` `bbb8e9e19907e10f7c5362550562f2d10da39a1a554e865e51daa5de3264b7bb` — both identical to revision 2. Views `task_0.view.json` `4c7fe623…7a` and `task_1.view.json` `0cf409af…56` — identical to revision 2. Gate snapshot (r3/gate_snapshot.txt): green except the expected TRACEABILITY NOT OK.
- Because both shared inputs are unchanged, every charter-global section of revision 2 (§ revision_2, re-derived checks, including R2-O1 and R2-O2) is **carried forward by reference**, with these two hashes as the grounds. No charter-global section is re-derived.
- Both task JSONs were rewritten at 2026-10-07T21:44:56Z (file mtime); per-task proof fields are therefore re-judged in each task file after the reveal.
- contamination_disclosure: round-1 and round-2 GT of both tasks are known to this auditor from revisions 1-2; the round-3 JSONs are unopened at this point.

### closing_checklist (revision 3)

Written 2026-10-07T21:46Z, after both revision-3 comparisons; the revision-3 frozen section above was written before the reveal and is unchanged.

| task | policy self-consistency | problem tree | factors | unique solution | revision 3 verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS (revision-2 proof-sentence RED closed) | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

- Every round-1 and round-2 RED is closed; claimed-unchanged items (task 1, R2-O1, R2-O2, F-6, F-8, F-10, O-5, O-6, O-7) are unchanged and remain observations only.
- Per-task files and this file carry revisions 1-3, earlier text untouched.
- Coverage and scope: 7 extended policies, scopes pairwise disjoint, 7 independently generated uuid8s, tools validate nothing — met.
- Trees: task 0 n=3 with 2 value_input edges, task 1 n=2 with 2; one owner=user write each; difficulty graph acyclic — met.
- Factors: 4-6 per computation with >= 2 parameter and >= 1 method, real three-tier ladders stated in the rules, every factor bears weight against an honest baseline, every baseline alone definite and non-gold, multi-source and Rewards cross-category factors per task — met.
- Gates: the coordinator's r3 snapshot on the final form is green except TRACEABILITY NOT OK, which is expected until docs/ is rendered and must be re-run after rendering; this audit does not run gates.
- **The difficulty passes the source-layer audit (all four relationships PASS for both tasks).**

## revision_4

### charter_global_frozen (revision 4)

- Same auditor. Started 2026-10-07T22:37:38Z; written before any round-4 task JSON was opened. Revisions 1-3 above are untouched.
- Context: round 3 left no RED. This round re-checks a rework made for the scenario load check (`/tmp/erl45_validate/validate_r1.txt`: "frozen_time '2026-10-07T17:05:00' must start with YYYY-MM-DD" for both tasks; `validate_r2.txt`: VALID).
- Inputs recomputed: `stay.extended.yaml` `ed0b001c…14a1` (unchanged); `task_tools.py` `562618ae0f611c3e94a90d90fb91fee1a44436a7d1694fd80bc03cbd7dc19347` (changed from bbb8e9e1…). Views: `task_0.view.json` `ff88818f…f6c1`, `task_1.view.json` `ce62b22c…2dc`. A view diff against r3 shows exactly one change per task: frozen_time "2026-10-07T17:05:00" -> "2026-10-07 17:05:00 CDT" (task 0) and "2026-10-07T19:30:00" -> "2026-10-07 19:30:00 MDT" (task 1); user_scenario and initial_state are byte-identical in content. Gate snapshot: all green including TRACEABILITY OK.
- Charter unchanged, so the charter sections of revision 2 (as carried in revision 3) are **carried forward by reference** on its hash. The tool module changed, so § action_binding_and_uuids is re-derived:
  - Diff in substance: every task tool now sets `posted_at = str(ctx.now())[:19].replace(" ", "T")`. `erlbench/determinism.py` `Clock.now()` returns the task's frozen_time verbatim ("e.g. '2025-11-14 03:40:00 EST'"), so the booked posted_at is "2026-10-07T17:05:00" / "2026-10-07T19:30:00", the same ISO local string the tools wrote under the r3 frozen_time and the same form as every seeded `stay_transactions.posted_at`. The receipt docstrings still promise "YYYY-MM-DDTHH:MM:SS". posted_at is not an input of any `make_id` call, so row ids are unchanged.
  - Bodies still validate nothing (no `if`/`raise`); signatures, owners, docstring Args and the 7 uuid8s are unchanged. Pass.
- Time-zone check on the new stamps: TX-AUSTIN is US Central and CO-DENVER US Mountain; on 2026-10-07 both are on daylight time (US DST ends 2026-11-01), so CDT and MDT are correct, and they match the local, zone-less seed timestamps (cancelled_at 13:40, request submitted 17:45 / decided 18:20).
- Compute impact: the DSL takes `NOW = str(frozen_time)[:10]` (`check_compute.build_env`), which is "2026-10-07" under both forms; every compute reads dates only (DAYS, MONTHS, within_months), so no binding can move.
- contamination_disclosure: rounds 1-3 GT known from earlier revisions; round-4 JSONs unopened at this point.

### closing_checklist (revision 4)

Written 2026-10-07T22:39Z, after both revision-4 comparisons; the revision-4 frozen section above predates the reveal and is unchanged.

| task | policy self-consistency | problem tree | factors | unique solution | revision 4 verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS | PASS |

- Round 3 left no RED; the round-4 rework (frozen_time in "YYYY-MM-DD HH:MM:SS <TZ>" form; tools normalising posted_at to the ISO form) moves no scored value, no proof field, no ledger timestamp format and no row id; the zone abbreviations (CDT for Austin, MDT for Denver, 2026-10-07) are correct.
- Carried items (R2-O1, R2-O2, F-6, F-8, F-10, O-5, O-6, O-7) unchanged and still observations only.
- Coverage, scope, uuid8s, trees and factor bounds as in the revision-3 checklist — met.
- Gates on the final form (coordinator r4 snapshot): all OK including TRACEABILITY OK; validate_scenario VALID (`/tmp/erl45_validate/validate_r2.txt`).
- **The difficulty passes the source-layer audit at revision 4.**
