# Policy-task audit — rate_lock_management / charter-global

## charter_global_frozen

- Frozen: 2026-10-04T23:39Z (UTC), before any task's GT was revealed. Auditor: erl-task-policy-audit (independent auditor agent, not the instantiator).
- Inputs and hashes (sha256, recomputed by the auditor; all match the brief's MANIFEST):
  - `tasks/rate_lock_management/lock.extended.yaml` df866ba50a04f82875c6b655c38bbf98fb054f44f789303c3a6a9b1de7d1c6ad
  - `tasks/rate_lock_management/task_tools.py` 273c1b5d662106a5f67cfb80b7b2de1aa1e778b02fb02dd34abb5b3ca568cb3e
  - masked views `audits/_views/policy_task/rate_lock_management/0.view.json` c4adca0f…a05177, `1.view.json` 1df3c74e…ff4a18
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/lock.yaml`, `blueprint/share_tools.py`, the table list of `blueprint/db_schema.json`, the extended charter, `task_tools.py`, and (for cross-category parameter values and state vocabularies) `blueprint/products/{purchase,homesite,warranty,insurance}.yaml` by explicit-file grep.
- Masked and not read: every task field outside task_id / frozen_time / user_scenario / initial_state (evaluation_criteria, computations, db_closure*, design_rationale, prerequisite_closure, solvability_contract, charter_scope, required_documents); `tasks/rate_lock_management/worklog.md`; `env/env_0033_national_homebuilder/worklog.md`; any other audits.
- Entry conditions (Step 0): the gate snapshot came with the brief (check_extended OK, check_task_tools OK, replay OK, solvability OK, compute OK, grounding OK, cache-diff INFO, cross_fire SCOPE OK, traceability NOT OK with the stated reason: hidden task-tool names awaiting the published KB). Masked views and hashes came with the brief. Entry conditions are complete; the traceability gate is cited, not re-run.
- Base-copy check: `diff <(head -n 677 lock.extended.yaml) blueprint/products/lock.yaml` differs only by one trailing blank line — the base section is a verbatim copy.

### policy_conflict_scan

Extended policies (7) and their write subjects:

| policy | subject | target_tool (owner) | computes | base refs |
| --- | --- | --- | --- | --- |
| lock_ext_builder_delay_relock | lock_relocked | relock_expired_lock_fa041ac0 (agent) | relock_fee | lock_expiry_relock |
| lock_ext_extension_days | lock_extended | extend_rate_lock_f01da2c0 (user) | extension_days | lock_extensions |
| lock_ext_extension_charge | lock_charge_assessed (extension_fee) | assess_extension_charge_dd0de570 (agent) | amount | lock_extensions, lock_float_down_option, lock_expiry_relock, lock_terms_change |
| lock_ext_builder_delay_waiver | lock_charge_waived | waive_builder_delay_charge_8eed57d4 (agent) | amount | lock_builder_delay_waiver |
| lock_ext_loan_resize | lock_terms_changed | resize_lock_loan_amount_2f4542ba (agent) | loan_amount | lock_term_eligibility, lock_terms_change |
| lock_ext_upfront_fee | lock_fee_paid | pay_upfront_lock_fee_7a2ad3ba (user) | amount | lock_fee_and_pricing |
| lock_ext_lock_confirmation | lock_confirmed | confirm_rate_lock_a056ffb5 (agent) | locked_rate | lock_fee_and_pricing |

- Overlapping subjects: `lock_charge_assessed` is touched by the extension-charge policy (charge_type extension_fee) and, as a side write of the relock tool, by the relock policy (charge_type relock_fee). The two book different charge types and price different quantities; no conflict. `lock_terms_changed` is governed by base lock_terms_change / lock_term_eligibility and the extended resize: the resize only lowers the amount, and base "A decrease in the loan amount never re-prices" is restated in the extended rule; no conflict. `lock_fee_paid` and `lock_confirmed`: the base amount / rate sentences are superseded by declared overwrites (see override_declarations).
- Eligibility / time anchors inherited from base and not weakened: one open lock per agreement; financed ratified agreement; term eligibility gates; fee deadline (3 business days after request, counting from the next business day); extension only on a locked lock; relock window (expired date = day one); terms change only on requested/locked; waiver dedup. None is restated differently by an extended rule, docstring or the tools.
- Cross-category read boundaries: the extended policies read purchase (agreement fields, purchase_events deposits / incentives / charges / closing_date_notice), homesite (occupancy_intent, variant_name, prequal_letter_date of the converted reservation), warranty (coverage status) and insurance (policy status). All reads; no extended policy writes another category.
- Terminal states: relock -> status locked with a new expiration date and a relock_fee charge; extension -> new expiration date, counters raised; extension charge -> extension_fee row; waiver -> lock_charge_waived row; resize -> new loan_amount and ltv_pct; fee payment -> lock_fee_paid row; confirmation -> status locked with lock_date / locked_rate / lock_expiration_date. Compatible.
- One base-vs-extended conflict on a scored quantity was found and is not declared — see findings F1.
- Scope exclusivity / completeness (from the prerequisite graph alone; per-task confirmation is in each task file): the graph has two connected components, {relock -> extension_days -> extension_charge -> waiver} and {loan_resize -> upfront_fee -> lock_confirmation}; with M=2, the two trees cover all 7 extended policies and share none. Exclusive and complete, provided task 0 and task 1 each claim one component (checked after reveal in the task files).

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and every rule sentence back against compute.

- lock_ext_builder_delay_relock: lapse_day (expired date = day one, relock date counted) = `DAYS(expired_date, NOW)+1`; lapse ladder 15 / 8 / else; relock LTV = loan / contract price x 100; LTV-score ladder (> 85 and < 720 / > 85 and >= 720 / else); occupancy via the converted reservation of the lock's agreement; homeowner credit (active / transferred or expired / else); closing overhang = scheduled closing − (relock date + relock_term_days), ladder > 15 / 1..15 / none; reminder lead = latest expiry reminder -> expired lock's expiration date, ladder none / < expiry_notice_days_before / else; fee % = relock_fee_pct + add-ons − credit; round half up to cent, floor relock_fee_min_usd, x multiplier, round half up. All quoted, all implemented. Observation O1: `owner_status: CFIELD('warranty','status')` carries no restriction to "another home" which the rule states; on a world with one coverage on the lock's own home the compute would take a credit the rule withholds. No task world here has such a coverage (both are checked per task), so no consequence is demonstrable.
- lock_ext_extension_days: days to cover, six cushions, round up to whole increments, two caps. All quoted and implemented. `lapse_len` uses `expired_date` which the relock tool leaves on the record, consistent with the rule's "a lock that has been relocked and whose expired date lies …".
- lock_ext_extension_charge: increments priced = (extension_days_used − extension_days on extension_fee charges) / increment; step-up (relock_fee charge on ledger / prior increments / else); length; allowance (after the extension, both / either caps used); lead = extension date -> expiration as it stood before (compute: `DAYS(NOW, lock_expiration_date) − new_days`, equal to the rule when the charge is booked on the extension date); fee held = paid − refunded − forfeited − credited; binder credit; first-unit rule; total rounded half up. Equivalent.
- lock_ext_builder_delay_waiver: latest extension_fee charge; builder share (ratio / zero / one) with buyer move days = closing_extensions_used x collection closing_extension_days; lapse gap = latest closing_date_notice -> expired date with relocked condition; reminder lead = reminder -> day before expired date; fee-standing goodwill (fee due on base upfront_fee_pct with floor, fee lag); core rounded half up, plus goodwill, capped at the charge. Equivalent.
- lock_ext_loan_resize: requested LTV on current contract price; four point ladders; price basis (whole excess above 6 % / half excess above 2 % / contract price); allowed LTV capped at max_ltv_pct; limit rounded down to the dollar (`int`). Equivalent. The new-LTV sentence ("resized loan amount divided by the contract price, rounded half up to two decimals") feeds a tool argument, not `computes`, and is unambiguous.
- lock_ext_upfront_fee: fee share (both / one / neither incentive type); lock lead; fee LTV; deposit standing; plan changes; letter age with score; fee % assembly; zero when upfront_fee_pct is zero; floor; x share; round. Equivalent.
- lock_ext_lock_confirmation: confirmation LTV grid; buydown share on loan amount; paid share; term premium proration (short by > 60 / short by 1..60 padded and capped / else) — `days_needed < lock_term − 60` / `< lock_term` matches the prose; lag (> 3 / 2..3 / else); price band; jumbo / government; floor at par; round half up to 3 decimals. Equivalent.
- No factor tier lives only in compute or only in the rule: every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding (mechanically confirmed: every `decides` and every binding exists in compute; every ladder has 3 tiers).

Result: rule <-> compute lossless in both directions (one observation, O1).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are 7 distinct pairs on 7 distinct tools; no tool is claimed by two policies.
- Docstrings name no other tool and state no position in a sequence. Every docstring carries "The buyer can afterwards see …" — an ordering word about the buyer's later view of the record, not about the action's place among writes (observation O2). The extension docstring says "any fee for the extension is booked separately on the lock ledger", which tells the reader that a separate charge write exists without naming it or ordering it (observation O3).
- Tool bodies (read in full): none validates a status, a fee, a prerequisite or an amount; every tool performs its write unconditionally (relock does not check status expired; confirm does not check that a fee is on the ledger; waiver does not check that the charge exists). The tool layer judges no prerequisite.
- uuid8s: fa041ac0, f01da2c0, dd0de570, 8eed57d4, 2f4542ba, 7a2ad3ba, a056ffb5. No shared prefix, no sequence, no copied head with a new tail. Observation O4: two pairs share their last byte — fa041ac0 / f01da2c0 (both also start with `f`) and 2f4542ba / 7a2ad3ba — and in each pair the two tools are adjacent writes of the same chain (relock / extend; resize / pay fee). For seven independent 32-bit draws the chance of two such pairs is about 0.3 %. This is suggestive of non-independent generation but not demonstrable as batch derivation; recorded as an observation.

### prerequisite_graph

- `prerequisite` is filled on all 7 policies (`[]` on relock and loan_resize).
- Edges: E1 extension_days <- builder_delay_relock (state_gate, gate rate_locks.status); E2 extension_charge <- extension_days (value_input, gate new_increments); E3 builder_delay_waiver <- extension_charge (value_input, gate charge_amount); E4 upfront_fee <- loan_resize (value_input, gate fee_loan); E5 lock_confirmation <- upfront_fee (value_input, gate paid_share).
- Every `problem` is another extended policy id of this file; none points at a base policy or itself; the graph is two chains, acyclic.
- Every `policy_source` is verbatim in the blocked policy's own rule (mechanically confirmed after whitespace normalisation).
- `form: state` on all five edges; no `fallback_reason` anywhere, as required.
- `kind` vs `gate`: E1 `state_gate` -> rate_locks.status is a real eligibility gate (base lock_extensions `extension_state`: "An extension is written only on a lock whose status is locked."). E2–E5 `value_input` gates `new_increments`, `charge_amount`, `fee_loan`, `paid_share` all exist as compute bindings of the blocked policy.
- `resolved_by` is the depended-on policy's `target_tool` in every edge, and the tool's effect makes the gate hold (E1: status locked + relocks_used+1; E2: extension_days_used raised; E3: extension_fee row; E4: loan_amount rewritten; E5: lock_fee_paid row).
- `condition` neither strengthened nor weakened relative to the sentence (E1 "status locked and relocks_used ≥ 1 on a lock whose expired_date is set" = "for a lock whose record carries an expired date … status … reads locked again and its relocks used count includes that relock"; E3 "extension_days equal the days the latest extension added" = "the extension charge for the days added to reach the moved closing date"; E5 "lock_fee_paid rows … add up to the upfront lock fee due on the lock's current loan amount" = "the buyer's upfront lock fee payment for the full upfront fee").
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any prerequisite field.

### prerequisite_sentences

Four-point test per edge, then the reader's derivation.

- E1 "For a lock whose record carries an expired date, the extension days are worked out only once its status on record reads locked again and its relocks used count includes that relock." Connective "only once"; record-visible state (status, relocks used); no tool / id / snake_case; scope limited to locks carrying an expired date, as the condition. Derivation: a reader looks for the write that returns an expired lock to locked and raises relocks used -> only the relock policy's rule ("A lock in status expired is relocked …") and the relock tool's effect produce it; the confirmation tool also sets `locked` but does not raise relocks used, so the conjunction singles out the relock. One reading. Wording observation O5: "that relock" has no antecedent inside the sentence; the reader resolves it as "the relock that made it locked again" — no second reading.
- E2 "The extension fee is fixed only after the lock record carries the extension it prices, its days counted in the extension days used beyond the extension days already charged on the lock ledger." Connective "only after"; state = extension days used exceeding charged days; only the extension (user tool) raises extension_days_used. One reading.
- E3 "The builder-delay waiver is not fixed until the lock ledger carries, under its own charge number, the extension charge for the days added to reach the moved closing date." Connective "not … until"; state = an extension_fee charge row; only the extension-charge tool writes it (the relock tool writes a relock_fee row, which the sentence excludes by "extension charge"). One reading.
- E4 "The upfront lock fee is fixed only after the loan amount on the lock is no more than the resized loan limit worked out on the purchase agreement's current contract price." Connective "only after"; state = loan amount <= limit; only the resize tool changes loan_amount. One reading.
- E5 "The locked rate is not set until the lock ledger carries the buyer's upfront lock fee payment for the full upfront fee." Connective "not … until"; state = a lock_fee_paid row for the fee; only the fee-payment tool writes one. "The full upfront fee" is read against the upfront-fee rule, which defines the upfront lock fee as the floored amount already multiplied by the buyer's fee share; a second reading ("full" = the pre-share amount) is recorded as observation O6 — the defining sentence of the depended-on rule fixes the first reading.
- No blocked rule carries a second wording of its dependency, a tool name, or another problem's id (mechanically checked for policy ids and tool names). No depended-on rule restates the sentence.
- Undeclared cross-problem order in an extended rule: none. The extension-charge rule ("A lock has been relocked when its ledger carries a relock_fee charge") and the waiver rule ("on a relocked lock") read the relock's ledger row as a value without an ordering connective; their order is entailed transitively by E1–E3.
- Base rule sentences that state a cross-problem order (observation O7, grounding no edge here because every edge has its own extended sentence): lock_fee_and_pricing "A request whose fee is not paid in time is not confirmed …"; lock_extensions "An expired lock cannot be extended and may only be relocked."

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (and against every base sentence that governs a quantity an extended policy scores).

- lock_expiry_relock -> lock_ext_builder_delay_relock: reminder sentence, expiry sentence, max_relocks, window, day-one counting, "After the window closes a new lock must be requested" — followed. Relocked-rate sentence and relock-term/fee sentence — replaced, both named in `overwrite` (the term clause is carried verbatim into the extended rule as a separate sentence, so nothing is lost). Declared.
- lock_extensions -> lock_ext_extension_days: increment / caps / status sentences followed; base fixes no extension length, so the cushion rule overrides nothing. `overwrite: []` correct for this policy's quantity.
- lock_extensions -> lock_ext_extension_charge: the per-increment fee sentence including first_extension_free is replaced and named. Declared.
- lock_extensions sentence "When the extension is needed because the purchase agreement's closing date moved for a builder delay, builder_delay_waiver_pct percent of the extension charge is waived under lock_builder_delay_waiver." — governs the waiver amount scored by lock_ext_builder_delay_waiver, states it as builder_delay_waiver_pct (100 on every term) percent of the extension charge, and is named in **no** `overwrite` (the waiver's refs are only lock_builder_delay_waiver; the extension-charge policy's overwrite names only the fee sentence). **Undeclared override -> F1.**
- lock_builder_delay_waiver -> lock_ext_builder_delay_waiver: the condition/amount clause is replaced and named; "relock, float-down and program change charges are never waived", "Each waiver names the charge number", dedup sentence — followed. Declared. (The replaced_by drops the base condition "the extension was needed to reach the new closing date"; the extended prerequisite sentence's "the days added to reach the moved closing date" carries it. No consequence.)
- lock_term_eligibility / lock_terms_change -> lock_ext_loan_resize: base states the LTV ceiling and that a decrease never re-prices; the extended limit is never above max_ltv_pct; no base sentence fixes a resized amount. No conflict.
- lock_fee_and_pricing -> lock_ext_upfront_fee: fee-amount sentence replaced and named; payment methods and deadline followed. Declared.
- lock_fee_and_pricing -> lock_ext_lock_confirmation: locked-rate sentence replaced and named; expiration / roll sentence restated verbatim. Declared.
- Disguised forms: no anonymous intermediate (every add-on is named in the replaced_by "fee percent"); no 0/1 multiplier on a base-fixed quantity; no dropped branch (jumbo / government branches of the locked rate survive in compute).
- Cross-charter note (observation O8, outside this audit's four artifacts): blueprint/products/purchase.yaml purchase_builder_delay states "Where builder_delay_lock_extension_paid is true, rate lock extension charges caused by a builder delay are borne by Calloway and waived on the lock", and builder_delay_lock_extension_paid is true for every collection. It points the same way as F1's base sentence (whole charge waived).

### factor_ladders

Per policy: factors, label, decides, tier outcomes, multi-source (tiers beyond the fall-through being conjunctions/disjunctions over distinct records), cross_difficulty. Every ladder has 3 pairwise-disjoint tiers, every tier is stated in the rule and implemented in compute, every fall-through equals the factor's `baseline`, no two tiers of a ladder share an outcome.

- builder_delay_relock (6): lapse_add P (0.125/0.0625/0); ltv_score_add P multi-source (lock loan + purchase contract price + lock score), xd purchase; occupancy_add P xd homesite; owner_credit P xd warranty; overhang_add P xd purchase; reminder_mult labelled **M**, tiers "multiplied by missing_reminder_mult (0.5)" / "multiplied by late_reminder_mult (0.75)" / "charged as figured" (x1).
- extension_days (6): funding_lag P xd purchase; slip_cushion labelled **M**, tiers "slip_cushion_days counted twice (4)" / "once (2)" / "none (0)"; buyer_cushion P xd purchase; lapse_cushion P (relocked AND expired-date age — two fields of the lock row); notice_cushion P xd purchase; gap_cushion P xd purchase.
- extension_charge (6): step_mult labelled **M**, tiers "relocked_step_mult (2) times" / "extended_step_mult (1.5) times" / "the per-increment fee" (x1); length_add P; allowance_add P (increment cap AND day cap); lead_credit P; held_credit P; binder_credit P xd insurance.
- builder_delay_waiver (4): builder_share M (tier 1 computes slip/(slip+buyer move days) from the records; tiers 2–3 constants) xd purchase, multi-source (closing extensions AND slip); lapse_rate P multi-source (relock_fee row on the lock ledger AND purchase closing_date_notice) xd purchase; reminder_goodwill P; standing_goodwill P (payments total AND lag).
- loan_resize (5): layer_points P multi-source (lock score AND LTV on purchase price); class_points P xd homesite; horizon_points P xd purchase; deposit_points P xd purchase; price_basis M (tiers 1–2 compute a deduction from the incentive rows; tier 3 the contract price) xd purchase.
- upfront_fee (6): fee_share labelled **M**, tiers "floored fee multiplied by both_credits_share (0.5)" / "by one_credit_share (0.75)" / "in full" (x1) xd purchase; early_credit P xd purchase; ltv_add P xd purchase; standing_credit P (no returned payment AND deposit count); plan_add P xd purchase; refresh_add P multi-source (homesite letter date AND lock score) xd homesite.
- lock_confirmation (6): grid_add P multi-source xd purchase; buydown_cut P xd purchase; paid_cut P; term_premium M (tiers 1–2 prorate on days needed; tier 3 the full premium) xd purchase; lag_add P; price_adj P xd purchase.

Label honesty (test: does a tier change how the quantity is computed, or only substitute a constant into one formula?):
- Honest `method`: builder_share, price_basis, term_premium — at least one tier computes a record-dependent quantity the other tiers do not.
- **Mislabelled `method`** (F2): reminder_mult, slip_cushion, step_mult, fee_share — every tier substitutes a constant (a multiplier or a count of a constant) into the same formula; these are `parameter` factors. Counting only honest labels, builder_delay_relock, extension_days, extension_charge and upfront_fee each have **0** `method` factors (bound: 1).

Baseline self-sufficiency (test: from `baseline.rule` + `baseline.params` alone, with no factor sentence, is there a definite number?):
- Definite: extension_days (additive "plus every cushion below" -> none), loan_resize ("starts at max_ltv_pct", "price basis is the contract price"), lock_confirmation ("term premium starts at rate_premium_pct"; additive adjustments -> none).
- **Indefinite** (F3): builder_delay_relock ("multiplied by the expiry reminder multiplier" — no value in baseline.rule or baseline.params); extension_charge ("times the step-up multiplier" — no value); builder_delay_waiver ("times the builder share, times the lapse rate" — no value); upfront_fee ("multiplied by the buyer's fee share" — no value). The default (1) appears only in the factor's `baseline` field and in the fall-through tier of the factor's own ladder, i.e. only in the factor document.
- Every baseline sentence is verbatim in its policy's rule (mechanically confirmed).

Realism of conditions and outcomes: every condition is one a builder-affiliated lender plausibly weighs (LLPA-style LTV/score and occupancy grids, IPC price-basis deduction, dry-funding states AZ/CA, buydown, lag, relationship credits, affiliated-insurance credit in a world whose purchase charter already ties incentives to affiliates). Observation O9: the upfront-fee plan-change add-on (lock fee percent raised by the count of builder plan_change_fee charges) is the weakest — not demonstrably a treatment no lender would publish. No condition holds of every customer who reaches its write.

Counts per policy, in the order relock / extension_days / extension_charge / waiver / loan_resize / upfront_fee / confirmation (raw label -> after F2): parameter 5->6, 5->6, 5->6, 3->3, 4->4, 5->6, 5->5; method 1->0, 1->0, 1->0, 1->1, 1->1, 1->0, 1->1. Every policy declares 4–6 factors. Cross-difficulty factors per policy: 4, 5, 1 (insurance), 2, 4, 6, 4 — categories read: purchase, homesite, warranty, insurance. Multi-source factors exist in every policy (listed above).

### findings

- **F1 — SOURCE-POLICY RED (undeclared override).** Symptom: two clauses govern the builder-delay waiver amount. Root cause: base lock_extensions keeps "When the extension is needed because the purchase agreement's closing date moved for a builder delay, builder_delay_waiver_pct percent of the extension charge is waived under lock_builder_delay_waiver." (builder_delay_waiver_pct = 100 on every term), while lock_ext_builder_delay_waiver scores "builder_delay_waiver_pct percent of the extension charge, times the builder share, times the lapse rate, rounded half up to the cent, plus the reminder goodwill and the fee-standing goodwill, never more than the extension charge itself." The base sentence is named in no `overwrite` (lock_ext_builder_delay_waiver.base_policy_refs = [lock_builder_delay_waiver] only; lock_ext_extension_charge's overwrite names only the per-increment fee sentence). Consequence: any task whose waiver's builder share x lapse rate is below one, without goodwill restoring it, has a second defensible answer (the whole charge). Affected: lock.extended.yaml base lock_extensions rule vs extended_policies[lock_ext_builder_delay_waiver]. Bears on: the task that claims the waiver (demonstrated in that task file). O8 (purchase charter) corroborates the base reading.
- **F2 — SOURCE-FACTOR RED (mislabelled method).** relock_expiry_reminder_multiplier, construction_slip_cushion, extension_step_up and builder_fee_share are labelled `method` but every tier only substitutes a constant into one formula (ladder text: "multiplied by missing_reminder_mult" / "by late_reminder_mult" / "charged as figured"; "slip_cushion_days is counted twice" / "once" / "no slip cushion"; "relocked_step_mult times" / "extended_step_mult times" / "at the per-increment extension fee"; "multiplied by both_credits_share" / "by one_credit_share" / "in full"). Consequence: builder_delay_relock, extension_days, extension_charge and upfront_fee each fall below the 1-`method` bound. Bears on: the task(s) claiming those computations.
- **F3 — SOURCE-FACTOR RED (incoherent baseline).** baseline.rule of builder_delay_relock, extension_charge, builder_delay_waiver and upfront_fee each multiply by a quantity (expiry reminder multiplier; step-up multiplier; builder share and lapse rate; buyer's fee share) to which neither baseline.rule nor baseline.params gives a value; a reader of the computation document alone reaches no definite number. Bears on: the task(s) claiming those computations.
- Observations O1–O9 above; none is grounds for rework on its own.

## closing_checklist

Written after both reveals (2026-10-04T23:40–23:41Z). The sections above were frozen at 2026-10-04T23:39:27Z (sha256 25f6d4cc…3f97) and contain nothing derived from GT. **The difficulty does not close.**

- Per-task files: `0.md`, `1.md`, one per task, with `_difficulty.md` alongside; no earlier revision exists. Comparison verdicts: task 0 RED (SOURCE-POLICY, SOURCE-FACTOR); task 1 RED (SOURCE-FACTOR). Not every comparison carries a PASS.
- Coverage and scope: charter_scope task 0 = {lock_ext_builder_delay_relock, lock_ext_extension_days, lock_ext_extension_charge, lock_ext_builder_delay_waiver}, task 1 = {lock_ext_loan_resize, lock_ext_upfront_fee, lock_ext_lock_confirmation}: the 7 extended policies are covered, pairwise disjoint, each tree whole. Task tools and GT are closed (each GT write calls its tree's tools; every tool belongs to exactly one task). uuid8s unique; O4 (two shared-last-byte pairs) stays an observation.
- Trees: task 0 has 3 prerequisites / 2 value_input / user write = extension; task 1 has 2 prerequisites / 2 value_input / user write = fee payment; acyclic; the difficulty's prerequisite graph is two disjoint chains — a DAG.
- Factors: every computation declares 4–6 factors and a baseline; but F2 (four mislabelled `method` factors -> relock, extension_days, extension_charge, upfront_fee have 0 honest `method`), F3 (four baselines not self-sufficient) and the per-task reds T0-4 (ltv_pct stamp agrees with the relock LTV tier) and T0-6 / T1-3 (sensitivity figures 1887.70 and 6.562 contradict the rule's half-up rounding) stand. Every factor bears weight on its world; every fall-back number differs from gold.
- Policy: F1 (undeclared override of the builder-delay waiver amount in base lock_extensions) stands and is demonstrated on task 0 (1061.82 vs 1005.07).
- Gate re-run on the final form: not performed — the difficulty does not reach closing; the brief's instantiation gate snapshot is cited in § charter_global_frozen.

Findings carried by task: F1 -> task 0 (T0-1); F2 -> task 0 (T0-2), task 1 (T1-1); F3 -> task 0 (T0-3), task 1 (T1-2).

## revision_2

### charter_global_frozen (revision 2)

- Re-audit requested by the coordinator (round 2), 2026-10-05. Auditor: erl-task-policy-audit (independent; same auditor as round 1).
- Inputs (sha256 recomputed, matching the round-2 MANIFEST): `lock.extended.yaml` 3025636c9dfa007854c536c08a63ba2b30a5465515d269280ff5f1468f3d4cda (changed from df866ba5…); `task_tools.py` 76e0f64958c8c5a0941004dd8b4165d2048d08a74f438dec111e4642967cb409 (changed from 273c1b5d…); views 0.view.json a85e7b7b…5a51 (changed), 1.view.json 1df3c74e…4a18 (unchanged). blueprint/products/lock.yaml unchanged (base section still a verbatim copy; the only diff is the trailing blank line). blueprint/products/purchase.yaml unchanged.
- Both shared inputs changed, so every charter-global section is re-derived in full below (not carried forward).
- Gate snapshot cited from the brief: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, TRACEABILITY NOT OK (deferred until the KB is published). Entry conditions complete.
- Masked and unread before the freeze: every masked task field, both worklogs.
- contamination_disclosure: round 1 revealed the round-1 GT of both tasks (sections above). This section rests on the charter, schema and tool contracts alone and uses no GT value.

### policy_conflict_scan (r2)

Same 7 extended policies, same subjects, same two disjoint chains; new tool names relock_expired_lock_4b9eda82, extend_rate_lock_1be9088d (user), assess_extension_charge_644b0045, waive_builder_delay_charge_21040a50, resize_lock_loan_amount_60b17697, pay_upfront_lock_fee_77612280 (user), confirm_rate_lock_760b1890. Inherited eligibility, time anchors, cross-category reads (read-only) and terminal states as in round 1; no new overlap. One new internal conflict on a scored quantity inside lock_ext_builder_delay_waiver's own rule — N1 below.

### rule_compute_equivalence (r2)

Swept again in both directions. Changes since round 1, each checked:
- relock: high_ltv_above_pct 88; reminder multiplier late tier = late_reminder_floor_mult + lead / (2 x expiry_notice_days_before) — `K('late_reminder_floor_mult') + reminder_lead / (2 * P('expiry_notice_days_before'))`; "the expiry reminder multiplier starts at one" stated. `owner_status` now excludes a coverage on the lock's own agreement (`CFIELD('warranty','purchase_id') != F('purchase_id')`) — O1 closed. `+ 0.0000001` before every RND makes half-cent ties round up, matching "rounded half up".
- extension_days: slip cushion tier 1 = ceil(slip / slip_week_days) — `int((slip_days + 14 − 1) // 14)` = "one day for every slip_week_days days of slip, any part counted as a whole".
- extension_charge: step-up tier 1 = 1 + count of relock_fee charges, tier 2 = 1 + prior_increment_step x prior increments; "the step-up multiplier starts at one" stated.
- waiver: "The builder share starts at one and the lapse rate starts at one." added; new sentence "Calloway bears only the part of an extension charge that the builder delay caused: the part that a buyer-requested closing move or the buyer's own lapse of the lock made necessary is not waived." — has no compute counterpart and contradicts the goodwill terms the compute adds (N1).
- loan_resize: deposit share now says "reservation funds transferred to it included" — T1-O3 closed.
- upfront_fee: fee share = 1 − min(rate_buydown_credit / 2 / floored fee, cap), cap both_credits_cap or one_credit_cap; "the buyer's fee share starts at one" stated; deposit-standing "reservation funds transferred to it counted as deposits".
- confirmation: unchanged except the prerequisite sentence (below).
Result: lossless both ways except N1 (a rule sentence whose conclusion the compute does not implement).

### action_binding_and_uuids (r2)

- 7 distinct `(target_tool, computes)` pairs. Tool bodies unchanged in effect; none validates anything.
- Docstrings: "afterwards" removed from all seven (O2 closed); the extension docstring no longer mentions a separately booked fee (O3 closed). No tool names, no ordering words.
- uuid8s: 4b9eda82, 1be9088d, 644b0045, 21040a50, 60b17697, 77612280, 760b1890. No shared prefix or sequence. Observation O4-r2: 60b17697 (resize) and 760b1890 (confirm) share the 4-hex run `60b1`; for 7 random draws the chance of any pair sharing a 4-hex run is about 1 %. The round-1 shared-last-byte pairs are gone. Not demonstrable as batch derivation; observation.

### prerequisite_graph (r2)

Unchanged in shape: E1 extension_days <- relock (state_gate, rate_locks.status), E2 extension_charge <- extension_days (value_input, new_increments), E3 waiver <- extension_charge (value_input, charge_amount), E4 upfront_fee <- loan_resize (value_input, fee_loan), E5 confirmation <- upfront_fee (value_input, paid_share). All `policy_source` verbatim in the blocked rule (mechanically re-checked), all `form: state`, no fallback, every `resolved_by` = the depended-on policy's new `target_tool`, every value_input gate an existing binding, acyclic.

### prerequisite_sentences (r2)

- E1 now ends "… its relocks used count includes the relock that returned it to locked." — the antecedent is explicit (O5 closed); same single reading (only the relock tool returns an expired lock to locked and raises relocks used).
- E5 now reads "The locked rate is not set until the lock ledger carries the buyer's payment of the upfront lock fee due from the buyer, after the buyer's fee share." — the "full fee" second reading is gone (O6 closed).
- E2, E3, E4 unchanged; four-point test still passes; no tool name, policy id or second wording in any rule (mechanically re-checked).
- O7 (base order sentences) unchanged, still grounding no edge.

### override_declarations (r2)

- lock_ext_builder_delay_waiver now lists base_policy_refs [lock_builder_delay_waiver, lock_extensions] and names in `overwrite` the base lock_extensions sentence "When the extension is needed because the purchase agreement's closing date moved for a builder delay, builder_delay_waiver_pct percent of the extension charge is waived under lock_builder_delay_waiver." with the formula sentence as replacement. **F1 closed**: no base sentence fixing the waiver amount remains undeclared.
- All other declarations as in round 1 (relock rate and fee; per-increment extension fee; upfront fee amount; locked rate), all `superseded_clause` verbatim in base and all `replaced_by` verbatim in the extended rule (re-checked).
- O8 (purchase_builder_delay "borne by Calloway and waived on the lock") is outside the four artifacts; the new waiver sentence "Calloway bears only the part … that the builder delay caused" now speaks to it directly — but see N1.

### factor_ladders (r2)

Label honesty (same test as round 1: a `method` needs at least one tier that computes a record-dependent quantity the other tiers do not):
- relock_expiry_reminder_multiplier: late tier 0.5 + lead/20 depends on the reminder lead — honest. Observation O10: at lead 0 (reminder on the expiration day) it equals missing_reminder_mult (0.5), a single-point coincidence.
- construction_slip_cushion: tier 1 ceil(slip/14) depends on the slip — honest; tier 1 >= 3 for slip > 30, distinct from tier 2's flat 2.
- extension_step_up: tier 2 (1 + 0.5 x prior increments) depends on the count — honest. Observation O11: tier 1 (1 + relock_fee charges) can only ever be 2, because max_relocks is 1 on every term (base lock_expiry_relock "An expired lock may be relocked at most max_relocks times").
- builder_fee_share: tiers compute 1 − min(buydown/2/fee, cap) — record-dependent, so the label is honest — but see N2.
- builder_share, builder_incentive_price_basis, term_premium_proration: unchanged, honest.
- **F2 closed** for the four factors named in round 1.

Baselines: relock ("the expiry reminder multiplier starts at one"), extension_charge ("the step-up multiplier starts at one"), waiver ("The builder share starts at one and the lapse rate starts at one"), upfront_fee ("the buyer's fee share starts at one") now state the default; every baseline sentence is in its rule. Each baseline yields a definite number from the records. **F3 closed.**

Ladder reality:
- **N2** builder_fee_share tier 2 "only one of the two incentives granted" is a disjunction; in its closing_cost_credit-only branch Calloway's part is half of a rate_buydown_credit of zero, so the buyer's share is 1 — the fall-through outcome. That branch of the tier selects the same value as "otherwise", and the closing_cost_credit condition taken on its own is not weighed by the outcome.
- Every other ladder: three disjoint tiers, distinct outcomes, conditions and outcomes plausibly weighed (as in round 1; O9 unchanged).

Counts after these tests: method factors per policy 1/1/1/1/1/1/1 (builder_fee_share counted only if N2 does not strike it — it does, see N2); parameter counts unchanged; cross-difficulty and multi-source factors as in round 1.

### findings (r2)

- **N1 — SOURCE-POLICY RED (new; introduced by the rework).** lock_ext_builder_delay_waiver's rule now carries two sentences that decide the waiver amount differently. "Calloway bears only the part of an extension charge that the builder delay caused: the part that a buyer-requested closing move or the buyer's own lapse of the lock made necessary is not waived." caps the waiver at charge x builder share x lapse rate. "The builder-delay waiver is builder_delay_waiver_pct percent of the extension charge, times the builder share, times the lapse rate, rounded half up to the cent, plus the reminder goodwill and the fee-standing goodwill, never more than the extension charge itself." adds the goodwill on top, waiving part of the buyer-caused share whenever a goodwill is above zero. Bears on task 0 (demonstrated there).
- **N2 — SOURCE-FACTOR RED (new; introduced by the rework).** builder_fee_share ladder: tier 2's closing_cost_credit-only branch yields share 1 = the fall-through. A ladder tier that, for part of its stated condition, selects the fall-through's value is not a real tier for that part; the factor fails the ladder test and is struck, which leaves lock_ext_upfront_fee with 0 `method` factors (bound 1). Bears on task 1.
- Round-1 items: F1 closed, F2 closed, F3 closed; O1, O2, O3, O5, O6 closed; O4 replaced by O4-r2; O7, O8, O9 unchanged (observations).

### closing_checklist (r2)

Written after the round-2 reveals. **The difficulty does not close.**

- Per-task files 0.md and 1.md each carry `## revision_2` appended after the untouched round-1 text; this file likewise.
- Round-1 REDs: F1 closed (declared overwrite) but N1 opened in its place; F2 closed for the four factors named (N2 then strikes builder_fee_share on a different ground); F3 closed; T0-4, T0-6, T1-3 closed; T0-5 resolved.
- Remaining / new: N1 (SOURCE-POLICY, task 0), N2 (SOURCE-FACTOR, task 1), T1-6 (SOURCE-CHAIN proof figure, task 1 — a regression of the fee-share rework not carried into the proof fields).
- Coverage and scope unchanged: 7 policies, two disjoint trees, task tools closed per task, uuid8s unique (O4-r2 observation). Trees: 3 and 2 prerequisites, value_input floors met, user writes present, graph a DAG.
- Every factor bears weight on its world against an honest, self-sufficient baseline; every fall-back differs from gold.
- Gate re-run on the final form: not performed (the difficulty does not close); the brief's round-2 snapshot is cited.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit requested by the coordinator (round 3), 2026-10-05. Same independent auditor.
- Inputs (sha256 recomputed, matching the round-3 MANIFEST): `lock.extended.yaml` c7cd19c8075ff08eb0d361ec55e2a2a94daf940576cabc5b9e86799ac93e8149 (changed from 3025636c…); `task_tools.py` 188955cba135ec03e479db6d4312c390a59312a0bc5cadaa6f5d8a66a112d4cb (changed from 76e0f649…); views unchanged since round 2 (a85e7b7b…, 1df3c74e…). blueprint/products/lock.yaml and purchase.yaml unchanged; the base section is still a verbatim copy.
- Both shared inputs changed, so the charter-global checks were re-run over the whole file (mechanical: baseline sentences in rule, prerequisite sentences verbatim, resolved_by = target_tool, overwrite clauses verbatim in base and extended, factor bindings in compute, 3-tier ladders, no policy id / tool name in any rule), and the changed passages were read in full.
- Gate snapshot cited from the brief (all OK; CACHE-DIFF INFO; TRACEABILITY deferred until the KB is published).
- contamination_disclosure: rounds 1 and 2 revealed both tasks' earlier GT. This section uses no GT value.

### changes found and checked (r3)

- lock_ext_builder_delay_relock: missing_reminder_mult 0.5 -> 0.4, so the missing-reminder tier no longer equals the late tier at lead 0 (late tier ranges 0.5–0.95) — **O10 closed**. Everything else as in round 2.
- lock_ext_extension_charge: step-up tier 1 is now "one plus the number of relock_fee charges on the lock ledger plus prior_increment_step for each increment written before this extension" (`1 + relock_charges + K('prior_increment_step') * prior_increments`), so with max_relocks 1 the tier still varies with prior increments (2, 2.5, 3, …) and stays above tier 2 (1 + 0.5 x prior) by the relock count — **O11 closed**; rule, compute_basis and ladder agree.
- lock_ext_builder_delay_waiver: the sentence "Calloway bears only the part of an extension charge that the builder delay caused: the part that a buyer-requested closing move or the buyer's own lapse of the lock made necessary is not waived." is removed. The rule now has a single statement of the amount (the formula with goodwill), matching the declared overwrites of both base sentences — **N1 closed**; F1 stays closed (both base sentences still named in `overwrite`). O8 (purchase_builder_delay "borne by Calloway and waived on the lock", outside the four artifacts) remains an observation.
- lock_ext_upfront_fee: builder fee share tier 2 is now "where it carries a rate_buydown_credit and no closing_cost_credit"; a closing_cost_credit-only agreement falls to "otherwise" (share one). Tiers: both credits -> 1 − min(buydown/2/fee, both_credits_cap = 0.6); buydown only -> 1 − min(…, one_credit_cap = 0.25); otherwise -> 1. Rule, compute (`closing_credits == 0 and buydown_credits > 0`) and ladder agree. No branch of a tier now selects the fall-through's value by construction — **N2 closed**; the factor is an honest `method` (record-dependent quotient), so lock_ext_upfront_fee has 1 `method`. Observation O12: tiers 1 and 2 share the quotient and differ only in the cap, so they coincide whenever Calloway's part is at or below 0.25; the closing_cost_credit is weighed only through the cap.
- lock_ext_lock_confirmation: target_tool renamed confirm_rate_lock_90ad719f; E5 `resolved_by` unchanged (pay tool); rule and compute unchanged.
- task_tools.py: confirm tool renamed; bodies still validate nothing; no ordering words, no tool names in docstrings. uuid8s 4b9eda82, 1be9088d, 644b0045, 21040a50, 60b17697, 77612280, 90ad719f: no shared head or tail byte, no shared 3-hex run — **O4-r2 closed**.

### status of every charter-global check (r3)

- policy_conflict_scan: no conflict on any scored quantity (N1 gone); scope still two disjoint chains covering all 7 policies.
- rule_compute_equivalence: lossless both ways.
- action_binding_and_uuids: 7 distinct pairs; uuids independent-looking; tools judge nothing.
- prerequisite_graph / prerequisite_sentences: unchanged from round 2, all pass.
- override_declarations: all conflicts declared; merged semantics unique.
- factor_ladders: every policy 4–6 factors, >= 2 parameter and exactly 1 honest method; every baseline self-sufficient and in its rule; no tier, or branch of a tier, repeats another tier's outcome by construction; multi-source and cross-difficulty factors as before.
- Charter-global findings open: none. Observations: O7, O8, O9, O12.

### closing_checklist (r3)

Written after the round-3 reveals.

- Per-task files 0.md and 1.md correspond one-to-one with the tasks; each carries revision_2 and revision_3 appended after the untouched earlier text; every revision_3 comparison carries a PASS on all four relationships.
- Extended policies fully covered: task 0 = {builder_delay_relock, extension_days, extension_charge, builder_delay_waiver}, task 1 = {loan_resize, upfront_fee, lock_confirmation}; pairwise disjoint; task tools and GT closed per task; uuid8s independent-looking (O4-r2 closed).
- Trees: task 0 has 3 prerequisites with 2 value_input edges, task 1 has 2 with 2; each has an owner=user write (extension; fee payment); the difficulty's prerequisite graph is two disjoint chains — a DAG.
- Factors: every computation declares a self-sufficient baseline (stated in its rule) and 4–6 factors with >= 2 parameter and 1 honest method; every task has multi-source and cross-difficulty factors on seeded rows; every ladder has three disjoint tiers, distinct in outcome, with conditions and outcomes the line of business holds (O9, O12 observations); every factor bears weight on its world, and every all-baseline fall-back differs from gold (figures in the task files).
- Policy: all base/extended conflicts declared; no rule states two amounts for one quantity; every prerequisite stated in the state form in the blocked rule.
- Gates on the final form: the orchestrator's round-3 snapshot (cited in the brief) is EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; TRACEABILITY NOT OK is deferred by design until the KB is published and must be re-run then. This auditor cites the snapshot and did not run the gates.
- **Source-layer audit: PASS for both tasks** (policy self-consistency, problem tree, factors and unique solution), conditional on the traceability gate passing once the KB is rendered.
