# Policy-task audit — renewals_transfers_and_early_exit / charter-global

## charter_global_frozen

- Frozen: 2026-09-24T17:27Z (revision_1, first audit of this difficulty; no earlier revision exists).
- Auditor: Claude, erl-task-policy-audit subagent, independent of the authoring agents; no answer was supplied to it.
- Freeze hashes:
  - `tasks/renewals_transfers_and_early_exit/term.extended.yaml` sha256 `ef3c178a43d14139fdd15104574a2d2b277b3a48650daabce2210592893bc7ac`
  - `tasks/renewals_transfers_and_early_exit/task_tools.py` sha256 `e690c7305f51fc57570a8454b34935bb7edc207a8a14bc85cdb2af0e2f74e9ad`
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (tool list and write bodies), `blueprint/products/term.yaml`, the `lease.yaml` late-fee / returned-payment / credit rules (to check the cross-difficulty seed rows), the whole extended charter and tool module, `erlbench`/`check_compute.py` expression semantics (COUNT/LATEST are scoped to the term, X* aggregates to the customer, `within_months` = `0 <= MONTHS(date, NOW) < n`, `RND` = Python `round`).
- Masked, not read before this file was written: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, db-closure fields, `worklog.md`, and every other audit directory. Nothing here derives from a revealed GT.
- Entry conditions (Step 0): the brief carries the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred to the render stage) and the masked views with hashes. Both view hashes were recomputed and match (`0.json` d14c0c63…, `1.json` 06de60dc…). Entry conditions met.
- Base copy: lines 1–1151 of the extended charter are byte-identical to `blueprint/products/term.yaml` (diff empty).

Policy shorthand used in this and the task files:

| Short | Policy id | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| A | term_ext_offer_line_correction | reissue_renewal_offer_line_9239b766 (agent) | offered_rent | [] |
| B | term_ext_like_program_renewal_rent | sign_renewal_term_7151ccb7 (user) | contracted_rent | A, value_input, state form |
| C | term_ext_break_concession_recapture | book_concession_recapture_8b577669 (agent) | amount | [] |
| D | term_ext_break_notice_shortfall | book_exit_notice_charge_a2fdf71c (agent) | amount | [] |
| E | term_ext_lease_break_quote | sign_lease_break_agreement_f74cee5b (user) | quoted_amount | C and D, value_input, state form |

### policy_conflict_scan

- Subjects: A = term_renewal_offer; B = term_create (renewal into the same program); C and D = term_fee_assessment with distinct fee_codes (concession_recapture, insufficient_notice_charge); E = term_early_termination + term_fee_assessment (reletting_fee). No two extended policies write the same fee_code or the same row kind, so there is no overlap between extended policies.
- Triggers and eligibility: A (state_due) needs a current term whose like-program line is above the effective cap; B (on_request) inherits base offer-open, one-pending-term and no-past-due gates; C, D (state_due) need an open lease-break request, C further on a new-lease term whose program recaptures; E (on_request) needs ETO unavailable and no documented statutory release. These are compatible with the base route order in term_early_termination_rule (statutory release, then ETO, then lease break).
- Time anchors: every extended computation reads the handling date (NOW) or recorded dates; none reads a future date.
- Cross-category reads: lease (A, B, C, D, E), parking (B, E), pet (E). lease and parking belong to the sibling difficulties rent_ledger_and_delinquency and parking_licenses_and_ev_charging; pet belongs to no difficulty.
- Terminal states: A leaves the error line on file and adds one line; B writes a pending renewal term; C, D add one charge line each; E sets the request to signed, the term to terminated_early and adds the reletting fee line. No terminal state of one policy contradicts another's.
- Scope partition (read from the prerequisite graph, before any reveal): the graph has exactly two connected components, {A→B} and {C, D→E}. With M=2, the only partition that is complete and disjoint is one component per task. The worlds agree: task 0 holds an expiring Standard term with a like-program line above cap (component {A, B}); task 1 holds an open lease-break request (component {C, D, E}). Confirmed against `charter_scope` in each task file's comparison.

### rule_compute_equivalence

Check 2 over all five extended policies (sentence ↔ `compute_basis` ↔ expression, both directions):

- A: every binding has a verbatim basis and is implemented as the basis states (tenure months to the error line's date, 3-tier loyalty, 3-tier standing, month-of-expiry season, last-rent-change relief, `MX(0, …)` company cap, rent-period fitting with <365 prorate / ≥730 compound / otherwise flat, CA/WA statutory limit, a single final rounding). No invented basis. PASS.
- B: every binding matches; the one-step subtraction and single rounding match the `result` basis. PASS.
- C: every binding matches (open lease-break request, concession total, 3 unearned-month conventions with no intermediate rounding, four shares, one rounding). PASS.
- D: **FAIL on `shortfall_days`** (finding F1). Its `compute_basis` quotes the rule sentence "the shortfall days, which are the term program's notice to vacate days less the calendar days from the date the request was received to the requested termination date, never fewer than zero", which is `MX(0, P('notice_to_vacate_days') - DAYS(received_date, exit_date))`. The expression instead is `MX(0, required_notice_days - notice_days_given)`, the floor-plan requirement minus the weekend-adjusted count. No sentence of D's rule says the shortfall days are "the notice an exit requires" less "the days of notice given". Those two terms appear only in the trigger sentence ("leaves fewer days of notice than the notice an exit requires carries an insufficient notice charge"). Every other binding of D matches its basis.
- E: every binding matches, including the two-stage rounding (rate part rounded, then surcharges added, then the total rounded). PASS.
- Observation O1 (all policies): the rule text says "rounded half up to the cent", but `RND` is Python `round` on a float, which rounds a binary tie half-to-even. No gold figure in either task lands on a half-cent tie (see the task files), so no consequence can be shown. Two counterfactual figures do: the task-1 D factor substitutions 2917.575→2917.57 and 2139.555→2139.55.
- Observation O2 (A, B, C, D, E): each rule carries its `baseline.rule` sentences verbatim, as the framework requires, and later sentences refine them. In A, B, C and E, and for D's daily rent, each refinement links back to the baseline by name: "The lower of the rent-period cap and the statutory increase cap … is the effective cap", "From that offered rent are subtracted …", "applied once to the unearned concession", "to give the reletting fee", "The daily rent is worked out by …". So the refined reading is the only coherent one. D's shortfall days is the exception, recorded as F1.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (five distinct tools). PASS.
- uuid8s: 9239b766, 7151ccb7, 8b577669, a2fdf71c, f74cee5b. They share no common prefix, are not sequential and have no common tail. Each appears once and looks independently generated. PASS.
- Tool bodies validate nothing (no status, prerequisite or balance check): lines 38–49, 80–93, 119–129, 158–170 and 201–216 only find, create and update. The share tools write only `identity_verifications` and `handoffs`, so the task tools are the sole writers of term_offers, lease_terms, term_charges and term_change_requests.
- Docstrings carry no ordering word tied to another tool. Observation O3: the `sign_renewal_term_7151ccb7` Args text says the offer_id comes "as returned by the renewal offer lookup or by the delivery receipt of a re-issued offer line", and the `reissue_renewal_offer_line_9239b766` text ends "can accept the new line by its own reference number". Neither names another tool, but both point to the re-issue → accept flow.

### prerequisite_graph

Check 7:
- `prerequisite` is filled on all five (A, C, D `[]`). Edges: B→A; E→C; E→D. Every `problem` is an extended id of this file, none is base or self, and the graph is acyclic (the sources A, C, D have no out-edges).
- Every `policy_source` is verbatim (whitespace-normalised) in the blocked policy's own `rule`: B's sentence is in B's rule, and E's two sentences are in E's rule. All are `form: state` with no `fallback_reason`. PASS.
- `resolved_by` equals the depended-on `target_tool` in all three edges. `gate` names a real binding: B `line_rent`, E `recapture_on_request` and `notice_charge_on_request`. All `kind: value_input`, matching a value binding. PASS.
- `condition` text: B's condition ("most recently delivered … line … carries an offered_rent no higher than the in-place contracted rent raised by the effective cap") matches its sentence. E's conditions add "at the amount the recapture rule gives / the exit notice shortfall rule gives", which is what "owed" in the sentence means. Neither is strengthened nor weakened. No authoring-viewpoint phrasing. PASS.
- Effects: B-edge effect names both `line_rent` and `renewing_lines` (the re-issue makes the like-program line count two). This is consistent with B's compute.

### prerequisite_sentences

Check 6, four-point test per edge:

| Edge | Sentence | Connective | Waited-on state (record-visible) | No tool/id/snake_case | Strength vs condition |
| --- | --- | --- | --- | --- | --- |
| B→A | "The contracted rent of a like-program renewal is fixed only after the offer line standing for the renewing term program is priced within the effective cap of the renewal offer rules." | only after | the standing (latest) term_offers line of the renewing program priced within the effective cap | yes | equal |
| E→C | "The total quoted on a lease-break agreement is fixed only after the term account carries the concession recapture owed on the open lease-break request." | only after | a concession_recapture term_charges line on the open request | yes | equal |
| E→D | "The lease-break agreement is not quoted for signature until the term account carries the insufficient notice charge owed on the open lease-break request." | not … until | an insufficient_notice_charge term_charges line on the open request | yes | equal |

- One write per state: only `reissue_renewal_offer_line_9239b766` creates term_offers rows. Only `book_concession_recapture_8b577669` creates concession_recapture lines. Only `book_exit_notice_charge_a2fdf71c` creates insufficient_notice_charge lines. The reletting-fee writer and the share tools create neither. PASS for all three.
- Derivation, B→A: B's sentence names a state ("priced within the effective cap of the renewal offer rules"). The effective cap is defined in A's rule. A's rule says a like-program line "above the effective cap … is re-issued before acceptance as a new line … at the corrected offer rent". So the resolving action is A's re-issue, in one reading.
- Derivation, E→C / E→D: E's sentences name "the concession recapture owed" / "the insufficient notice charge owed" on the open request. C's rule "sets the concession recapture booked on the term account for an open lease-break request". D's rule sets the charge an open lease-break request "carries … on the term account". Each resolves to one booking, in one reading.
- No blocked rule carries a second wording, a tool name or another policy id.
- Observation O4 (cross-problem order in a depended-on rule): A's rule says the error line "is re-issued before acceptance" (a phrase inherited from base term_evt_renewal_offers: "is corrected before acceptance"). C's and D's rules say their charge is "booked against that request when the request is quoted". These state the same direction as the declared edges B→A and E→C/E→D and ground no other order, so they are not undeclared dependencies. They are second wordings of the dependency in the depended-on rules.

### override_declarations

Check 1, finding half. Sentence by sentence against each `base_policy_refs` entry:

- A vs term_evt_renewal_offers:
  - "delivered only on a term that is current": followed.
  - Lead days / options / "each open for renewal_offer_valid_days": A's re-issued line keeps the original last acceptance date, so it is open fewer than renewal_offer_valid_days from its own date. Observation O5: it does not touch A's scored quantity.
  - Exclusions while notice / default / past-due: followed.
  - The effective-cap sentence: declared overwrite.
  - "Each offer line's offered_rent is that 12-month-equivalent rent adjusted by the offered program's rent_adjustment_pct (with its rent_adjustment_min_amount floor)": **handled differently and not named** (finding F2). A's corrected like-program rent is "the in-place contracted rent of the expiring term raised by the effective cap", with no rent_adjustment_pct. The two coincide only where the expiring program's rent_adjustment_pct is 0 (Standard). For Short-Term (+0.15, floor 150), Flexible (+0.08, floor 75), Extended (−0.01) and Long-Term (−0.02) like-program lines they differ.
  - "Revenue management may offer less … corrected before acceptance": followed.
- A vs term_agg_tenancy_chain: the loyalty sentence is a declared overwrite; the chain measurement is followed.
- B vs term_evt_term_pricing:
  - The contracted-rent sentence is a declared overwrite.
  - Start day, term_end_rule, "written only from a renewal offer line", no past-due, pending→current: inherited.
  - The offer-open window "offer date plus the offer's validity days" has two readings for a re-issued line (its own offer_date + valid days, or its stored expiration date). Observation O5 again: task 0 falls inside both.
- B vs term_agg_multi_holding, term_mtm_conversion, term_transfer_rule, term_agg_tenancy_chain: followed or not engaged.
- C vs term_early_termination_rule: the recapture sentence is a declared overwrite; "Only one … concession recapture … per early termination request" is followed ("once per request"). C vs term_agg_tenancy_chain: the unearned-concession sentence is a declared overwrite; "never recaptured once the new-lease term has run to its term_end_date" is restated. C vs statutory release / transfer (no recapture on those routes): followed.
- D (overwrite: []) vs its refs: the base lease-break sentence lists reletting fee, lease-break rent and recapture, and excludes no other charge, so D adds a charge without contradicting a ref sentence. Observation O6: D computes a fee_code (insufficient_notice_charge) whose base definition sits in term_notice_to_vacate_rule, which is not in D's refs. That rule's sentence ("an insufficient_notice_charge is assessed for the days short (insufficient_notice_charge_basis daily_contracted_rent: contracted_rent times 12 divided by 365 …)") is scoped to notices to vacate. The same base rule says an earlier date on a fixed term is "never a notice", so it does not govern a lease-break request. D's CA/WA /30 and TX/GA ×12/364 conventions therefore override no base sentence on D's own subject, although `parameter_schema.insufficient_notice_charge_basis` describes the basis generically.
- E vs term_early_termination_rule: the reletting-fee / lease-break-rent sentence is named in `overwrite`. Its `replaced_by` restates the baseline sentence (program rate × rent) rather than the rate ladder and surcharges that actually deviate. Because the base sentence is named, the replacement is declared, and the merged semantics is E's full rule. Observation O7. The route order, "takes effect only when the resident signs it" and lease-break rent accrual are followed.

### factor_ladders

Counts (effect label), multi-source factor, cross-difficulty factors:

| Policy | Factors | parameter / method | Multi-source (every non-fall-through tier a conjunction over distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- |
| A | loyalty_cap_reduction, standing_cap_reduction, expiry_season_cap_reduction, increase_relief_cap_reduction, rent_period_cap_fitting | 4 / 1 | standing (lease_payments returns × leases.autopay_enrolled) | loyalty (lease), standing (lease) |
| B | early_renewal_discount, early_renewal_clock_start, violation_discount_share, on_time_renewal_credit, parking_bundle_credit | 4 / 1 | on_time (lease_charges late fees × leases.autopay_enrolled) | violation (lease), on_time (lease), parking (parking) |
| C | unearned_month_convention, conduct_share, partnership_share, clean_record_share, commitment_share | 4 / 1 | conduct (returns × autopay) | conduct, partnership, clean_record (lease) |
| D | notice_day_count, exit_notice_requirement, state_daily_rent_convention, exit_season_share, lapsed_request_multiplier | 3 / 2 | none (notice_day_count's tier 2 conjoins two dates of the same request row) | exit_notice_requirement (lease), state_daily_rent_convention (lease) |
| E | remaining_term_reletting_rate, reletting_month_count, collection_surcharge, parking_release_surcharge, floor_plan_turnover_allowance, pet_turnover_surcharge | 5 / 1 | collection (leases.balance_due × lease_charges late fees) | collection (lease), turnover (lease), parking_release (parking); pet reads pet, which is no difficulty, so `null` is correct |

- Every factor has a 3-tier ladder whose tiers are pairwise disjoint as stated. `decides` is always an input binding, never `result`. Binding sets are disjoint within each policy. Each ladder's fall-through equals the factor's `baseline`. Every tier (condition and value/method) is stated in the policy's rule prose and implemented in `compute`.
- Labels: every `method` factor changes the algorithm (prorate/compound, counting origin, month convention, weekend count rule, daily-rent divisor, reletting month count). Every `parameter` factor substitutes a number. PASS.
- `baseline.rule` of each policy is self-sufficient: every sentence is in the rule, and it yields a definite number with no factor applied.
- Tier distinctness is program-dependent in two ladders (observation O8, latent):
  - A's loyalty tier 2 (the program's loyalty_increase_cap_reduction_pct) is 0.00 for Month-to-Month and Short-Term, so for a Short-Term like-program line tier 2 = the fall-through (0).
  - B's early_renewal_discount tier 2 (the program's early_renewal_discount_monthly) is 0.00 with a 0-day window for Month-to-Month and Short-Term, so for a Short-Term like-program renewal tier 2 = the fall-through.
  - Both are distinct for Flexible and above. Neither task in this difficulty sits on a Short-Term program (task 0 is Standard).
- Realism: most tiers (loyalty / off-season renewal caps, early-renewal and bundle credits, military or employer partnership relief, seasonal reletting relief, remaining-term reletting rates, floor-plan turnover, pet turnover) are recognisable apartment-industry treatments. Observation O9:
  - D's TX/GA daily rent "contracted rent times 12 is divided by 364" and D's lapse multiplier (a larger notice charge because earlier exit requests were withdrawn) are unusual.
  - E's collection surcharge added to a reletting fee is also unusual.
  - None of the three can be shown to be a treatment no business in the line would publish, so they are not red.
- Rule/compute of D's lapse filter (observation O10, latent): the rule counts "the earlier exit requests on the same term that were withdrawn or expired". `lapsed_requests` counts every term_change_requests row on the term with status withdrawn or expired, with no request_type filter (a withdrawn unit_transfer or renewal_rescission would count) and no "earlier" filter. `inputs.history` also lists only the `withdrawn` filter. No task of this difficulty seeds a lapsed non-exit request, so no consequence can be shown.

### findings

- **F1 — SOURCE-POLICY RED (charter-global, D `shortfall_days`)**
  - Symptom: D's rule gives the shortfall days in one sentence as "the term program's notice to vacate days less the calendar days from the date the request was received to the requested termination date, never fewer than zero". D's compute gives them as `MX(0, required_notice_days - notice_days_given)`, the floor-plan requirement minus the weekend-adjusted count.
  - Root cause: the factor sentences refine "the notice an exit requires" and "the days of notice given", which appear only in the trigger sentence. No sentence carries those refinements into "the shortfall days". The `compute_basis` for `shortfall_days` quotes the sentence the expression does not implement.
  - Evidence: term.extended.yaml, D rule, lines 1784–1794; compute line 1821; compute_basis line 1838.
  - Consequence: the two passages give different shortfall days wherever the lease is Three-Bedroom / Penthouse / Studio / One-Bedroom, or wherever a weekend enters the count. Bears on **task 1**, where the demonstration is carried.
  - Affected: D rule, D compute_basis.shortfall_days, D compute.shortfall_days.
- **F2 — undeclared override, latent (charter-global, A vs term_evt_renewal_offers)**
  - Symptom: base prices every offer line as the capped 12-month-equivalent rent adjusted by the offered program's rent_adjustment_pct. A prices the corrected like-program line as the in-place contracted rent × (1 + effective cap), with no program adjustment, and the base sentence is not named in A's `overwrite`.
  - Consequence: for a Flexible expiring term, base gives the capped 12-month-equivalent × 1.08 (at least +75) and A gives in-place × (1 + cap). Two answers for the same line.
  - Bears on no task of this difficulty: task 0 is a Standard term, rent_adjustment_pct 0.00. Recorded as a charter defect with no task demonstration, so it enters no task verdict.
  - Affected: A `overwrite` (missing entry), A rule sentence "The corrected offer rent of a like-program line is …".
- Observations O1–O10 as above: rounding mode, baseline-in-rule structure, docstring flow hints, depended-on-rule order wording, re-issued line validity, D notice-basis scope, E replaced_by wording, program-dependent tier collapse, unusual tiers, D lapse filter. None changes a verdict.

## closing_checklist

(Written after all task reveals; see below.)

(Checklist written 2026-09-24T17:31Z, after both reveals. The charter-global section above was written before any reveal and has not been edited.)

- Audit files: `_difficulty.md`, `0.md` and `1.md` exist, one per task (tasks 0 and 1). This is revision_1, so there is no older revision. Each task file carries a frozen derivation followed by a comparison.
  - The freeze headers carry estimated clock times (17:40Z / 17:52Z). The real order is by mtime: `_difficulty.md` 17:28:23Z, `0.md` 17:29:18Z, `1.md` 17:30:17Z, then the reveal at 17:30:20Z. Each task file records this as a clerical correction; the frozen text was not changed.
- Comparison verdicts:
  - Task 0: PASS.
  - Task 1: **SOURCE-POLICY RED** (F1).
  - Not every comparison section carries a PASS, so **the difficulty does not pass the source-layer audit**.
- Coverage and scope: all five extended policies are covered. Task 0 holds {A, B}; task 1 holds {C, D, E}. The two scopes are disjoint and span their whole trees (charter_scope confirmed at reveal).
- Tools: each task tool is used by exactly one policy and one task. Each uuid8 is independent (see action_binding_and_uuids).
- Problem trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge, a user write (sign_renewal_term).
  - Task 1: 2 prerequisite problems, 2 value_input edges, a user write (sign_lease_break_agreement).
  - Both are acyclic. The difficulty-wide graph {B→A, E→C, E→D} is a DAG with no cross-task edge.
- Factors:
  - Every computation declares a self-sufficient baseline and 5–6 factors with at least 2 parameter and at least 1 method.
  - Task 0: multi-source = standing and on_time; cross-difficulty = lease and parking.
  - Task 1: multi-source = conduct and collection; cross-difficulty = lease and parking.
  - Every factor bears weight on its world, and every whole-baseline figure is definite and differs from gold: 2311.20 / 2220.21 (task 0); 1242.96 / 639.45 / 7068.34 (task 1).
  - The program-dependent tier collapse (O8) is latent; neither task sits on a Short-Term program.
- Open charter findings: F1 (red, borne by task 1). F2 (undeclared override of the base offer-line adjustment for non-Standard like-program lines) is latent: no task of this difficulty instantiates it.
- Gates: the instantiation-stage gate snapshot that came with the brief is all green (rc=0). The audited artifacts have not changed since: term.extended.yaml ef3c178a…, task_tools.py e690c730…, tasks/0.json 348a092e…, tasks/1.json 52dacdcd…. The auditor did not re-run the gates (Step 0: the gates are supplied, not run). A green gate does not clear F1: the compute is self-consistent with gold, and it is the rule text that diverges from it.

## revision_2

### charter_global_frozen (revision_2)

- Written 2026-09-24T18:12Z, before any round-2 task GT was opened. Auditor: Claude, erl-task-policy-audit subagent, as in round 1.
- Hashes moved since round 1, so every charter-global section below is **re-derived in full**, not carried forward:
  - `term.extended.yaml`: ef3c178a… → `1bc9ae6aa1a737cdc11c508cdb676c18588fc7b0057c803bedf390540e8c587c`
  - `task_tools.py`: e690c730… → `4598c925f2aa962596d874a16d190408d701fe852d9f7269d4f4602648576c18`
- Base section: lines 1–1151 are still byte-identical to `blueprint/products/term.yaml`.
- Read: the full extended section and the full tool module, both reread in round 2.
- Masked until the task derivations are frozen: round-2 task GT fields, all reworker notes, `worklog.md`.
- Entry conditions: the gate snapshot came with the brief (all rc=0). The r2 view hashes were recomputed and match: `0.json` eb771be8…, `1.json` 81a2e04f….
- The round-1 text above is preserved unedited.

What changed, read from the artifacts (not from the reworker's claims):

- **A** (`term_ext_offer_line_correction`):
  - A scope sentence limits A to the Flexible, Standard, Extended and Long-Term programs.
  - The trigger is now "above the corrected offer rent".
  - The re-issued line is "dated the handling date and open for the program's renewal offer validity days counted from that date like any offer line".
  - The corrected offer rent now includes the program rent adjustment (premium with minimum-premium floor, or discount), with a new binding for the capped 12-month-equivalent rent and a new binding for the program adjustment.
  - `half_up_guard` added.
- **B**: the same scope sentence (Flexible and above); the prerequisite `condition` reworded to "the corrected offer rent … adjusted by the program's rent adjustment"; `half_up_guard` added.
- **C**: "when the request is quoted" removed ("booked against that request once per request"); `half_up_guard` added.
- **D**:
  - New sentence "The shortfall days are the notice an exit requires less the days of notice given, never fewer than zero."
  - New baseline sentence "The notice an exit requires is the term program's notice to vacate days, and the days of notice given are the calendar days …"; `compute_basis.shortfall_days` now quotes the new sentence.
  - `term_notice_to_vacate_rule` added to `base_policy_refs`, with a scope sentence ("A notice to vacate keeps its own insufficient notice charge … this rule sets only the charge on a lease-break request, which is never a notice").
  - The lapse rule is now "the other lease-break and Early Termination Option requests on the same term that were withdrawn or expired", with compute filtered to those two request types.
  - "when the request is quoted" removed; guards added.
- **E**: the `overwrite.replaced_by` text is now the sentence that actually deviates (rate part plus the four surcharges); guards added.
- **Tools**:
  - `reissue_renewal_offer_line_9239b766` gained an `offer_expiration_date` argument and writes it; its docstring no longer says the resident "can accept the new line".
  - The `sign_renewal_term_7151ccb7` offer_id text no longer mentions "the delivery receipt of a re-issued offer line".
  - C, D and E tool bodies are unchanged. No body validates anything.

### policy_conflict_scan (revision_2)

- Subjects, triggers, time anchors and terminal states are unchanged from round 1, except A's added program scope and its validity-window terminal field. No extended policies overlap.
- The scope sentences of A and B send Short-Term like-program lines and renewals back to the base rules. That is consistent with base term_evt_renewal_offers and term_evt_term_pricing.
- The partition is still {A, B} and {C, D, E}, with two components and M = 2.

### rule_compute_equivalence (revision_2)

Every `compute_basis` quotation of all five policies is verbatim in its rule (checked mechanically after whitespace normalisation). Sweep in both directions:

- **A**: `capped_equivalent_rent` = contracted × (1 + effective cap). `program_rent_adjustment` = MX(cer × pct, min) for a premium, cer × pct otherwise. `result` rounds cer + adjustment. Every one matches its sentence. PASS.
- **B, C, E**: unchanged apart from the guard. PASS.
- **D**:
  - `shortfall_days = MX(0, required_notice_days - notice_days_given)` now has its own sentence: "The shortfall days are the notice an exit requires less the days of notice given, never fewer than zero."
  - "The notice an exit requires" and "the days of notice given" are each defined twice by name. First comes a baseline sentence (the program's notice-to-vacate days; calendar days). Then comes the ladder sentence ("… is set by the floor plan …, any other floor plan requires the term program's notice to vacate days"; "… are counted in one of three ways …").
  - The ladder sentence contains the baseline value as its fall-through. This is the same named-refinement structure as A's two "effective cap" sentences (O2). The operative reading is the ladder.
  - `lapsed_requests` counts withdrawn or expired `lease_break` and `early_termination_option` requests, matching "the other lease-break and Early Termination Option requests … withdrawn or expired".
  - PASS. **F1 is closed at the charter level.** It is demonstrated closed on task 1's world in `1.md` revision_2.
- Guard, observation O11 (new, latent):
  - Every rounding now adds `K('half_up_guard') = 0.000001` before `RND`. This gives half-up for binary ties: the round-1 counterfactuals 2917.575 and 2139.555 now give 2917.58 and 2139.56, as the rule states. **O1 is closed.**
  - The guard is not a rule quantity. It would also round up a true value within 1e-6 below a half cent.
  - No gold or counterfactual figure of either task lies in that band (task files), so no consequence can be shown.

### action_binding_and_uuids (revision_2)

- The five `(target_tool, computes)` pairs are unchanged and each is claimed once. The uuid8s are unchanged, distinct and not derived from one another. PASS.
- The new `offer_expiration_date` argument of the re-issue tool is determined by A's rule: "open for the program's renewal offer validity days counted from that date like any offer line". The base counting rule applies: "counted as calendar days starting the day after the offer date, and the offer can be accepted through the last counted day". The expiration is therefore the handling date plus renewal_offer_valid_days.
- Docstrings: the two flow hints (O3) are gone. The re-issue docstring's closing sentence describes only the resulting state. **O3 is closed.**

### prerequisite_graph (revision_2)

- The edges B→A, E→C and E→D are unchanged. `policy_source` is verbatim in the blocked rule. All edges are state form with no `fallback_reason`. `resolved_by` equals each target_tool, and the gates exist in compute. The graph is acyclic.
- B's `condition` now reads "no higher than the corrected offer rent of the renewal offer rules (the in-place contracted rent raised by the effective cap and adjusted by the program's rent adjustment)", while the sentence says "priced within the effective cap of the renewal offer rules".
- These are equivalent. In base term_evt_renewal_offers, a line is within the cap exactly when its 12-month-equivalent rent does not exceed in-place × (1 + cap). That holds exactly when the line does not exceed that capped rent adjusted by the program's adjustment, whether the minimum-premium floor binds or not.
- So the condition is neither strengthened nor weakened. PASS.

### prerequisite_sentences (revision_2)

- The four-point test on the three sentences passes as in round 1, since the sentences are unchanged. Each state still has exactly one writer.
- O4: C and D no longer tie their booking to "when the request is quoted". A still says a line in error "is re-issued" (the word "before acceptance" is gone). **O4 is closed.** The depended-on rules no longer carry a second wording of the order.

### override_declarations (revision_2)

- **A vs term_evt_renewal_offers**:
  - "Each offer line's offered_rent is that 12-month-equivalent rent adjusted by the offered program's rent_adjustment_pct (with its rent_adjustment_min_amount floor), rounded half up to the cent" is now **followed**. A's corrected rent is the capped 12-month-equivalent rent adjusted by the program's rent adjustment, with the floor ("adds the larger of its rent adjustment percentage … and its minimum monthly premium"). For a hypothetical Flexible like-program line the two now agree: in-place × (1 + cap) × 1.08, or + 75 if larger.
  - "each open for renewal_offer_valid_days" is now followed by the re-issued line.
  - **F2 is closed. O5 is closed.**
- **B**: unchanged; declared overwrite only.
- **C**: unchanged.
- **D**: `term_notice_to_vacate_rule` is now a ref, and D states that it sets only the lease-break charge. The base sentence stays scoped to notices, so there is no undeclared override. **O6 is closed.**
- **E**: `replaced_by` now names the deviating sentence. **O7 is closed.**

### factor_ladders (revision_2)

- Counts are unchanged: A 5 (4p/1m), B 5 (4p/1m), C 5 (4p/1m), D 5 (3p/2m), E 6 (5p/1m). Multi-source factors (standing, on_time, conduct, collection) and cross-difficulty factors are as in round 1.
- **O8 is closed**: A and B now apply only to programs where the middle loyalty and early-renewal tiers are above zero (Flexible 0.01 / 15.00; Standard 0.02 / 25.00; Extended 0.02 / 30.00; Long-Term 0.02 / 35.00). Tier 2 therefore always differs from tiers 1 and 3.
- **O9 is unchanged**: the TX/GA 364-day convention, the lapse multiplier and the collection surcharge remain. As in round 1 it cannot be shown to be a treatment no business would publish, and it stays an observation.
- **O10 is closed** (lapse filter, above). Observation O12 (new, minor): D's `inputs.history` still lists only the `withdrawn` filters, not `expired`. This is declared metadata only; compute counts both.

### findings (revision_2)

| Round-1 item | Round-2 status | Evidence |
| --- | --- | --- |
| F1 (SOURCE-POLICY RED, D shortfall days) | **closed** | new sentence "The shortfall days are the notice an exit requires less the days of notice given"; compute_basis quotes it; the refinement is by name |
| F2 (latent undeclared override, A) | **closed** | A now follows the base program-adjustment sentence |
| O1 rounding | closed | guard gives half-up on ties; new latent O11 recorded |
| O2 baseline-in-rule structure | unchanged by design, and now uniform | D's refinement of the notice-requirement / notice-given baseline now links by name like the others; not a defect |
| O3 docstring hints | closed | — |
| O4 order wording in depended-on rules | closed | — |
| O5 re-issued line validity | closed | rule plus the tool's `offer_expiration_date` argument |
| O6 D notice-basis scope | closed | — |
| O7 E replaced_by | closed | — |
| O8 tier collapse on Short-Term | closed | scope sentences on A and B |
| O9 unusual tiers | kept (reworker's choice) | observation only |
| O10 D lapse filter | closed | O12 (metadata) noted |

- New defects found in the charter or tool module: none red. O11 and O12 are observations.
- Regression check: the tool bodies still validate nothing, and no prerequisite sentence, uuid or factor count moved.

### closing_checklist (revision_2)

Written 2026-09-24T18:14Z, after both round-2 reveals. The revision_2 charter-global section above was written before the reveals and not edited afterwards.

- The audit files correspond one to one with tasks 0 and 1. Round-1 text is preserved, and each file carries a `## revision_2` with a frozen derivation followed by a comparison.
- Both round-2 derivations carry a contamination disclosure: the round-1 GT had been seen. All values were recomputed from the round-2 charter on the r2 worlds.
- Comparison verdicts:
  - Task 0: **PASS**.
  - Task 1: **PASS**.
- Round-1 REDs: F1 is **closed**, and no other red existed. F2 is also closed.
- Round-1 observations: O1, O3, O4, O5, O6, O7, O8 and O10 are closed; both seed observations are closed. O2 is structural and unchanged, not a defect. O9 was kept by the reworker and remains an observation.
- New items, all observations and none red:
  - O11: the half-up guard band.
  - O12: D's `inputs.history` lacks the `expired` filters.
  - A stale "before acceptance" quotation in task 0's design_rationale.
- Coverage and trees: all five extended policies are covered, with disjoint scopes {A, B} and {C, D, E}. The trees have 1 and 2 prerequisite problems, with value_input edges ≥ max(n − 1, 1). Each tree has a user write. The difficulty-wide graph is a DAG.
- Factors: 5/5 (task 0) and 5/5/6 (task 1). Parameter and method minimums are met. Each task has multi-source and cross-difficulty factors (lease, parking). Every factor bears weight, and every whole-baseline figure is definite and differs from gold.
- Tools: uuid8s unchanged and independent; bodies validate nothing.
- Gates: the brief's round-2 snapshot is all rc=0. The audited artifacts match the brief's hashes: term.extended.yaml 1bc9ae6a…, task_tools.py 4598c925…. The auditor did not re-run the gates (supplied input).
- **All four relationships PASS for both tasks. The difficulty passes the source-layer audit in revision_2.**
