# Policy-task audit — maturity_due_and_payable_cases / charter-global

## charter_global_frozen
- Frozen: 2026-10-15T07:14Z (written before any task GT was revealed). Auditor: independent erl-task-policy-audit agent (did not author the artifacts).
- Hashes (sha256 prefix): `maturity.extended.yaml` 5d78a8b0068173d1, `task_tools.py` 5fd6ea8653de2143, base `blueprint/products/maturity.yaml` d51f918a2af539cd. They match the coordinator snapshot.
- Read: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/*.yaml` sections that own the seeded rows), the extended charter, `task_tools.py`, the masked views `.audit_views/policy/maturity_due_and_payable_cases/{0,1}.json` (frozen_time, user_scenario and initial_state only), and the gate snapshot `snapshot_r1.txt`.
- Masked and not read before the freeze: `tasks/maturity_due_and_payable_cases/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure). No recursive search touched `tasks/*/tasks/`.
- Entry conditions: the gate snapshot came with the brief. All gates are green except traceability (unlock tool-name provenance only) and validate_scenario (INVALID only because "required document not found"). The coordinator says both are expected before the KB is rendered. The masked-view hashes match the brief (af27c92acbc0bbab, 5a15699daa40adbe).

### policy_conflict_scan
- The base section of the extended charter is byte-identical to `blueprint/products/maturity.yaml`. I checked this by diffing everything before `extended_policies:`.
- Six extended policies:

  | policy | target tool | computes |
  |---|---|---|
  | maturity_ext_successor_runway (R) | reclassify_case_to_death_eeacbce3 | runway_days_added |
  | maturity_ext_successor_response_window (W) | mail_successor_due_notices_bb6e23d7 | response_window_days |
  | maturity_ext_successor_evidence_window (E) | declare_successor_intent_94ee6efc, owner=user | evidence_due_days |
  | maturity_ext_first_extension_sizing (F1) | grant_first_extension_77f15011 | extension_days |
  | maturity_ext_further_extension_ask (A) | supplement_extension_request_11bdc0c2, owner=user | requested_extension_days |
  | maturity_ext_further_extension_sizing (F2) | grant_further_extension_50c8b1d2 | extension_days |

- Overlapping subjects:
  - F1 and F2 both carry `maturity_extension_granted`. Their scopes are split explicitly: F1 covers "the first extension on a Summit loan's case whose borrower has died". F2 covers "a further extension on a Summit loan's case". Every other extension uses the plan's extension days.
  - A also lists `maturity_extension_granted` as its subject even though its write files a request. This is an observation; no conclusion changes.
- Shared quantities:
  - "Unrepaid property-charge advances / Summit Tax and Insurance Reserve not active" appears in R, W, E and F1, each with its own day values.
  - "Sale under way" (a received listing/financing request plus a latest accepted sell/retain declaration) appears in R, W and E.
  - These are separate computations on separate written quantities, so there is no cross-policy conflict.
- Time anchors:
  - R keeps the response deadline. W resets it to the mailing date plus the window.
  - E's acceptance window conflicts internally on the deadline day itself. See finding CG-1.
- Cross-category reads: residency (death notices, inspection findings), jumbo (principal_balance), propcharge (transactions), setaside (reserve status and balance) and payoff (terms, contract). All are reachable through share find_* tools.
- Scope exclusivity: the prerequisite graph has two components, {R, W, E, F1} and {A, F2}. That is consistent with a disjoint, complete two-task cover. The per-task claim is checked against charter_scope only after the reveal.

### rule_compute_equivalence
Every compute binding carries a `compute_basis` quotation that is a substring of its own rule. I checked each tier sentence against its compute branch:
- **R**:
  - phone_report_date reads phone death notices with no review-status filter, which matches "any earlier telephone report".
  - runway_start_offset tiers (≤10 days after phone / no phone and >30 days after death / otherwise) match the rule.
  - runway_length is 60/20/30.
  - equity_share is RND(balance/appraised·100, 2), or 100 with no appraisal. Equity days are 15/7/0.
  - charge_days are 10/5/0, gated on the reserve not being active.
  - underway_days are 7/3/0.
  - result is MX(0, …), which matches "never negative".
  - No invented basis.
- **W**:
  - base_count is 21/25/P(successor_response_days).
  - appraisal_days are 15/10/5/0, using P(appraisal_valid_months) and 4.
  - charge_days are 5/2/0.
  - counted_window: the mail branch is a closed-form business-day count. I verified it for weekday and weekend mailing days (for example, Saturday + 1 = Monday, 2 days). The portal branch rolls Saturday +2 and Sunday +1. Otherwise there is no move. Federal holidays count as weekdays, as stated.
- **E**:
  - evidence_window is 14/21/30.
  - clock_start_offset is response deadline / latest grant date when in extension_period / 0.
  - appraisal_allowance is 21/14/7/0 and charge_cut is 7/3/0.
  - result is MX(1, …), which matches "never less than 1".
- **F1**:
  - horizon_days: financing is deadline→commitment+60, listing is deadline→listing+180, otherwise P(extension_days).
  - Allowances: occupant 15/7/0, equity 14/7/0, charge 10/5/0, carried request 10/5/0, estate 14/21/0.
  - result is MN(P(extension_days), MX(0, …)), which matches "the smaller of the total and the plan's extension days; negative counts as zero".
- **A**:
  - ask_span: good-through date / contract received + 45 / plan days.
  - payoff_funds_days 21/7/0; occupant 10/3/0; appraisal 21/14/7/0; filing lead 5/2/0 (P(hud_extension_lead_days) = 15, ≤30).
  - reserve_days: active and short gives 7, depleted gives 14, otherwise 0.
  - result is MN(P(extension_days), MX(0, …)).
- **F2**:
  - document_current means dated ≤30 days before receipt.
  - measured_extension: financing to commitment+60, listing to listing+120, otherwise plan days.
  - Allowances: equity 14/7/0, used_cut 14/7/0, payoff 10/5/0, occupant 7/3/0, reappraisal 30/21/7/0.
  - result is MN(P, MX(0, …)).
- Every ladder tier in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and the reverse also holds. Result: rule and compute are equivalent in both directions. No RED under check 2.

### action_binding_and_uuids
- Each (target_tool, computes) pair is claimed once. F1 and F2 both compute `extension_days`, but on different tools.
- The uuid8 values (eeacbce3, bb6e23d7, 94ee6efc, 77f15011, 11bdc0c2, 50c8b1d2) share no prefix or sequence, and none is reused.
- Docstrings carry no ordering word (before/after/first/then/prior/until; a word-boundary grep returned nothing). They name no sibling tool and give no example values, so there is no gold leak.
- Tool bodies check only that the case exists. No tool judges a prerequisite:
  - reclassify does not check for a death notice.
  - mail does not check the variant.
  - declare does not check the response deadline or the profile type.
  - grant_first does not check the declared intent or the variant.
  - grant_further does not check that the document is current.
- One docstring inaccuracy is an observation only: the declare tool writes the declaration as `accepted` directly.

### prerequisite_graph
- `prerequisite` is filled for all six policies. R and A have `[]`.
- Edges:
  - W←R: state_gate, gate maturity_cases.variant_name, resolved_by reclassify ✓.
  - E←W: value_input, gate clock_start_offset, resolved_by mail ✓.
  - F1←E: value_input, gate estate_allowance, resolved_by declare ✓.
  - F1←R: value_input, gate horizon_days, resolved_by reclassify ✓.
  - F2←A: value_input, gate measured_extension, resolved_by supplement ✓.
- The graph is acyclic. No edge points at a base policy or at its own policy. Each `policy_source` is a verbatim sentence of the blocked policy's own rule. All edges are state form, so no fallback_reason is needed. Every value_input gate is a real compute binding.
- `condition` wording:
  - E←W condition: "The case's response_deadline is later than **the frozen date**, …" uses authoring-viewpoint wording. This is finding CG-2.
  - F1←R condition adds "and its resolution_deadline has been carried forward by the successor runway days", which goes beyond the sentence ("is not sized until the case's event type reads the death…"). The only write that sets the variant also moves the deadline, so no second reading results. Observation.

### prerequisite_sentences
Four-point test, all edges in state form:
- W←R: "…are not mailed, and the successor response window is not counted, **until** the case's event type is the death of the last surviving borrower."
  - The connective is "until". The state is the record-visible variant_name. It names no tool and no id.
  - Exactly one write in this difficulty sets the variant to Death: reclassify (R's rule describes it). A death case cannot be newly opened while the case is open, per the one_open_case dedup.
  - Derivation: the sentence plus the case's variant (Property Charge Default) plus R's rule ("the case is reclassified to the Death of Last Surviving Borrower plan") leads to reclassify. ✓
- E←W: "…are taken **only after** the case shows a response deadline that falls after the day of the declaration."
  - The state is maturity_cases.response_deadline. The one write that moves it later is W's mailing ("the case's response deadline becomes the mailing date plus that window"); R keeps it. ✓
  - The sentence contradicts E's own overwrite text. See CG-1.
- F1←E: "…granted **only after** the case records the resolution intent declared by a successor in interest of that borrower."
  - The state is successor_customer_id/successor_intent. The one write is declare (E's rule: "the declared intent is recorded on the case as the successor's intent"). ✓
- F1←R: "…is not sized **until** the case's event type reads the death of the last surviving borrower." ✓, same derivation as W←R.
- F2←A: "A further extension is not granted **until** the case carries an extension request awaiting a decision whose supporting document is dated no more than 30 days before the day that request was received."
  - The one write is A's re-filing (A's rule: "the re-filed request is recorded as received on the day it is filed"). ✓
- Checks across all edges:
  - No depended-on rule restates the blocked sentence. A's rule mentions that "any grant rests on the most recently received request awaiting a decision"; that is selection wording, not the prerequisite. Observation.
  - No extended rule states an undeclared cross-problem order.
  - A base sentence (maturity_extensions: "granted only to a … confirmed successor whose declared intent is sell_property or retain_property") states an order, but F1 carries its own prerequisite sentence, so this is an observation only.

### override_declarations
Sentence-by-sentence findings:
- **R** vs maturity_agg_multi_holding: the reclassification sentence is replaced; the deadline is carried forward and the response deadline kept. Declared ✓. maturity_case_opening is followed: event_date is the date of death per event_date_basis, and nothing else changes.
- **W** vs maturity_notices:
  - S1 (timing/recipients/method) is replaced. Declared ✓.
  - S2 (default notice), S3 (referral/extension letter/cure) and S4 (pre-confirmation caller) are followed.
  - S5 (once per date) is replaced by the pair dedup. Declared ✓.
- **W** vs maturity_call_due: the response_deadline clause is replaced. Declared ✓.
- **W** vs maturity_intent_appraisal: followed.
- **E** vs maturity_intent_appraisal: S2 (declaration on file, received) and S3 (window) are replaced. Declared ✓.
  - The rest is inherited: intent_options, no_response, "a later valid declaration replaces an earlier one", and appraisal ordering within appraisal_order_days.
  - Inside E, the replaced_by text ("the deadline day itself still counting") and E's own prerequisite sentence disagree. That is CG-1, not an undeclared override.
- **F1/F2** vs maturity_extensions:
  - S1 (adds extension_days), S-HUD and S-max are replaced. Declared ✓.
  - Inherited unchanged: "granted only against an extension request on file … received … evidence_type one of extension_evidence", "received no later than the current resolution deadline … request_after_deadline", and "The first extension moves the case to extension_period and every extension sets resolution_deadline to the extended_deadline; **when the appraisal is older than appraisal_valid_months, a new appraisal is ordered, per reappraisal_for_extension**."
  - That last inherited sentence is not touched by any overwrite. No tool in the difficulty or in share_tools orders or records an appraisal; share_tools has only find_*, verify_customer_identity and transfer_to_human_agent. Consequence: see task 1.
- **A** (`overwrite: []`) vs maturity_extensions: A sizes only what a re-filed request asks. No base sentence governs that quantity, and the base on-file, received and deadline gates are followed. ✓

### factor_ladders
Per policy: (label) decides; tiers; multi-source; cross-difficulty.
- **R** (5 factors):
  - household_runway (param) decides runway_length: 3 tiers 60/20/30; residency.
  - report_anchor (method) decides the start-date anchor: 3 tiers; multi-source (phone notice, accepted notice, date of death); residency.
  - equity_runway (param): 15/7/0; reads jumbo.
  - charge_runway (param): 10/5/0; multi-source (propcharge transactions AND setaside status); setaside.
  - underway_runway (param): 7/3/0; multi-source (request AND declaration).
  - Counts: 4 param, 1 method. Labels honest. Tiers distinct.
- **W** (4):
  - sale_underway_window (param): 21/25/30, multi-source.
  - appraisal_age_window (param): 15/10/5/0.
  - charge_window (param): 5/2/0, multi-source; setaside.
  - counting_convention (method): business days / weekend roll / plain calendar; residency.
  - Counts: 3 param, 1 method ✓.
- **E** (4):
  - on_file_evidence_window (param): 14/21/30, multi-source.
  - evidence_clock_anchor (method).
  - appraisal_evidence_allowance (param): 21/14/7/0.
  - charge_evidence_cut (param): 7/3/0, multi-source; setaside.
- **F1** (6):
  - document_horizon (method).
  - occupant_allowance (param): 15/7/0; residency.
  - equity_cushion (param): 14/7/0.
  - advance_exposure_cut (param): 10/5/0, multi-source; setaside.
  - carried_request (param): 10/5/0, multi-source; residency.
  - estate_resolution (param): 14/21/0.
- **A** (6):
  - sale_span (method); payoff.
  - payoff_funds_allowance (param): 21/7/0, multi-source (contract AND terms); payoff.
  - occupant_vacate_allowance (param): 10/3/0.
  - appraisal_currency_allowance (param): 21/14/7/0.
  - filing_lead_allowance (param): 5/2/0.
  - reserve_charge_allowance (param): 7/14/0; setaside.
- **F2** (6):
  - current_document_measure (method).
  - balance_to_value_days (param): 14/7/0.
  - prior_grant_cut (param): 14/7/0, multi-source.
  - payoff_readiness (param): 10/5/0, multi-source; payoff.
  - household_occupant_days (param): 7/3/0; residency.
  - reappraisal_allowance (param): 30/21/7/0.
- Every ladder is stated in full in its rule and implemented in compute, with no compute-only tier. Every fall-through is the policy baseline.
- **Reachability test.** Is every tier reachable by a customer who reaches this write, and does every part of a compound condition divide those customers? This fails for the class in CG-3. After striking the failing factors:
  - E keeps 3 factors and has no method.
  - F1 keeps 3 (occupant, equity, advance) and has no method.
  - F2 keeps 4 and has no method.
  - R, W and A keep their full counts.
- Realism: the domain conditions read as a plausible proprietary (Summit, non-FHA) servicing schedule: occupancy finding, equity cushion, unrepaid advances against a lapsed reserve, sale evidence, appraisal age and payoff readiness. Observations:
  - W's counting_convention keys the response-window counting rule to the channel through which the death certificate arrived. That is an unusual basis for a deadline convention. In addition, its "otherwise" fall-through is reachable only through an *accepted* phone death notice. The residency charter records a death "only from an accepted death_notice submission carrying the death certificate", and a phone report cannot carry one (task 0's seeded phone notice is rejected as supporting_document_missing). So the fall-through is very likely unreachable. I recorded this as an observation because the residency charter does not ban an accepted phone notice in so many words.
  - F1 and F2 allow "a negative total counts as zero", which means granting a zero-day extension that still consumes one of max_extensions. No servicer publishes that. It is not reached on either world, so it stays an observation.

### findings
**CG-1 — SOURCE-POLICY RED (E: internal contradiction on the response-deadline day).** Bears on task 0.
- Symptom: E's rule contains two sentences that decide the same declaration differently.
- Evidence (E.rule sentence 2, the overwrite replaced_by, verbatim): "…which is accepted only from a customer whose profile type is successor in interest linked to the deceased borrower and only when the day it is filed is no later than the case's response deadline, **the deadline day itself still counting**; … one filed later is declined as outside the response window…"
- Evidence (E.rule sentence 3, the prerequisite policy_source, verbatim): "A successor's intent declaration, and the evidence due date it carries, are taken only after the case shows a response deadline that **falls after the day of the declaration**."
- Demonstrated consequence: take a successor declaring on the day equal to the case's response deadline. Sentence 2 says accept it and record the intent, with the clock-anchor tier falling to tier 2 or 3. Sentence 3 says do not take it. Two outcomes: write vs refuse.
- Affected: E rule, prerequisite E←W, and the evidence_clock_anchor ladder (see CG-3a).

**CG-2 — SOURCE-POLICY RED (authoring-viewpoint text in a prerequisite).** Bears on task 0.
- Evidence: E.prerequisite[0].condition reads "The case's response_deadline is later than **the frozen date**, having been reset from the mailing…".
- "The frozen date" is benchmark-authoring vocabulary, not a business state. The skill makes such phrasing in `prerequisite` a red light. It also drifts from the sentence's "the day of the declaration".
- Affected: maturity.extended.yaml, maturity_ext_successor_evidence_window.prerequisite[0].condition.

**CG-3 — SOURCE-FACTOR RED (class: tiers or condition parts that hold for, or are closed to, every customer who reaches the write).** The rule or an inherited base gate already fixes the outcome for everyone who can reach the write, so the ladder restates scope rather than dividing customers. Unreachable fall-throughs make the baseline a treatment no customer at that write ever receives. All members:
- a. **E.evidence_clock_anchor** (method). By E's own prerequisite sentence, every successor declaration that is taken has "a response deadline that falls after the day of the declaration". So tier 1 ("the case's response deadline falls after the declaration date") holds for everyone, and tiers 2 and 3 (including the baseline "clock starts on the declaration date") are unreachable. In effect it is a one-tier ladder.
- b. **F1.document_horizon** (method), tier 3 "with any other document, or with no extension request awaiting a decision, the extension is the plan's extension days". The inherited base gate says "granted only against an extension request on file … received … whose evidence_type is one of the plan's extension_evidence" (listing_agreement and financing_commitment in every plan). The overwrite says "a request whose evidence is missing or of another kind is declined". The grant "rests on the most recently received extension request". So no grant can be on tier 3, and "an extension request is awaiting a decision" holds for everyone in tiers 1 and 2. That leaves two reachable tiers.
- c. **F1.estate_resolution**, tier 3 "otherwise". F1's prerequisite sentence requires the case to record the intent "declared by a successor in interest", and the inherited base requires the declared intent to be "sell_property or retain_property". So the most recent accepted declaration at grant time is always a non-borrower's sale or retention. The condition part "made by someone other than the borrower of record" holds for everyone, and tier 3 is unreachable. That leaves two reachable tiers.
- d. **F1.carried_request**, tier 2 part "and the case is a death case". F1's scope is "the first extension on a Summit loan's case whose borrower has died", and its prerequisite says it "is not sized until the case's event type reads the death of the last surviving borrower". So every case reaching the write is a death case, and the part restates scope. Tiers 1–3 themselves remain reachable.
- e. **F2.current_document_measure** (method), tier 3 "where no request is awaiting a decision or its document is not current or of another kind". F2's prerequisite sentence says it "is not granted until the case carries an extension request awaiting a decision whose supporting document is dated no more than 30 days before…", and the inherited evidence gate excludes other kinds. So tier 3 is unreachable, and "awaiting a decision" and "current" hold for everyone. That leaves two reachable tiers.
- f. **F2.prior_grant_cut**, tier 3 "where the case has no extension granted, nothing is taken off". A further extension presupposes a granted one: F1/F2's overwrite separates "the first extension" from "a further extension", and every other first extension takes plan days. Every accepted extension request rested on a listing agreement or financing commitment, per the base evidence gate. So "the case already has an extension granted" holds for everyone and tier 3 is unreachable. That leaves two reachable tiers.

Demonstrated consequence (charter level): once these are struck, E, F1 and F2 lose their only `method` factor, and F1 falls to 3 surviving factors (below 4). On each world, the fall-through or baseline of a, b, c, e and f is a treatment no customer at that write can be given, so the "baseline" substitution measures nothing the business would publish. Per-task figures are in 0.md and 1.md.

**CG-O (observations, no RED):**
- A's subject `maturity_extension_granted` is used for a request filing.
- F1←R condition is stronger than its sentence (benign).
- E.rule S1 "provided the declaration is one the base rule accepts" points at a base clause that E itself overwrites. Read with S2 it is unambiguous.
- The base reappraisal-on-extension sentence is inherited with no tool to perform it. Task 1 carries the consequence.
- W.counting_convention's fall-through reachability and its realism (above).
- The zero-day-extension clause in F1 and F2.

## closing_checklist
Written after both reveals. Nothing above this heading was changed after a reveal.
- Per-task files 0.md and 1.md correspond one-to-one with the tasks, and `_difficulty.md` sits alongside them. This is the first revision.
- Coverage and scope:
  - Task 0 charter_scope = {R, W, E, F1}. Task 1 = {A, F2}.
  - The two are pairwise disjoint and together cover all six extended policies.
  - Task tools are closed. The uuid8s are independent.
- Trees:
  - Task 0 has 3 prerequisite problems, 3 value_input edges, a user write (E) and no cycle.
  - Task 1 has 1 prerequisite problem, 1 value_input edge, a user write (A) and no cycle.
  - The whole graph is a DAG.
- Factors:
  - Every computation declares 4–6 factors with an honest baseline, and every factor moves its scored value on its world. All figures match GT.
  - **But** the reachability class CG-3 strikes the only method factor of E, F1 and F2, and leaves F1 at 3 factors.
  - Task 0's E computation has no near-miss.
- Not closed. Open REDs:
  - Charter-wide: CG-1 (SOURCE-POLICY), CG-2 (SOURCE-POLICY), CG-3 (SOURCE-FACTOR, members a–f).
  - Task 0: T0-F1 (SOURCE-FACTOR) and T0-C1 (SOURCE-CHAIN).
  - Task 1: T1-T1 (SOURCE-TASK).
- Gate re-run on the final form: not applicable, because the difficulty does not pass. Gates are to be re-run after rework.

task0=SOURCE-POLICY/SOURCE-CHAIN/SOURCE-FACTOR RED task1=SOURCE-FACTOR/SOURCE-TASK RED
charter=CG-1,CG-2,CG-3

## revision_2

### charter_global_frozen (revision 2)
- Frozen 2026-10-15, before any round-2 GT reveal.
- Hashes:
  - `maturity.extended.yaml` is now 113d161b97a4cd42 (changed from 5d78a8b0068173d1), so every charter-global section is re-derived.
  - `task_tools.py` is 5fd6ea8653de2143 (unchanged), so action_binding_and_uuids and the tools-judge-no-prerequisite finding carry forward by reference.
  - The base section is still byte-identical to `blueprint/products/maturity.yaml`.
- Gate snapshot `snapshot_r2.txt`: all green. Traceability shows unlock tool-name misses only; validate is INVALID only before render.
- Masked: `tasks/*/tasks/*.json` until both round-2 derivations below were on disk.

### re-derived checks (revision 2)
- **rule_compute_equivalence**: every compute binding has a basis.
  - Multi-sentence bases (the `result` of R, F1, A and F2) consist of sentences that are each verbatim in the rule.
  - New or changed branches checked against compute:
    - E clock_start_offset: extension_period gives the latest grant date; not in extension and resolution deadline minus response deadline ≤ 30 gives the declaration date; otherwise the response deadline.
    - W counted_window is now keyed on the latest inspection finding.
    - F1 horizon_days: financing, listing ≤ 180 days old at receipt, otherwise plan days.
    - F1 carried_request: the tier 2 "death case" part is dropped.
    - F1 successor_takeover: days from the latest accepted declaration to the grant, 14/7/0.
    - F1 and F2 results: MX(30, …), and 0 when no request is pending.
    - F2 measured_extension: financing with a payoff statement runs to good-through + 10; financing alone runs to commitment + 60; a listing gives plan days.
    - F2 used_cut: listing and more than 60 days since the last grant gives 14; listing ≤ 60 days gives 7; financing gives 0.
    - A's no-pending guard gives 0.
  - All match. PASS.
- **override_declarations**: F1 and F2 add a fourth overwrite replacing the base clause "when the appraisal is older than appraisal_valid_months, a new appraisal is ordered, per reappraisal_for_extension". For Summit extensions the new text is "not reordered at the grant … ordered when a payoff or sale is next evaluated, as the base appraisal rule provides". It is declared in both policies, and the merged meaning is unique. Every other sentence is unchanged from revision 1.
- **prerequisite_graph / prerequisite_sentences**:
  - Same five edges, still acyclic and all state form.
  - E's sentence now reads "…a response deadline that falls **on or after** the day of the declaration". It agrees with the overwrite's "the deadline day itself still counting". **CG-1 closed.**
  - E's condition now reads "falls on or after the day the successor declares". "Frozen date" has gone, and a sweep of the whole extended section finds no other authoring phrasing. **CG-2 closed.**
  - F1←E is now gated on `takeover_allowance`, a real binding. The single-reading derivations from revision 1 still hold.
  - **New: R2-N2** (below). F2←A `effect` still says "the measured extension runs to 60 days after the commitment date instead of falling back to the plan's extension days". That is now false whenever the loan has issued payoff terms, because F2's rule measures to the good-through date + 10 in that case.
- **factor_ladders (revision 2)**:
  - Counts:

    | policy | factors | parameter | method |
    |---|---|---|---|
    | R | 5 | 4 | 1 |
    | W | 4 | 3 | 1 |
    | E | 4 | 3 | 1 |
    | F1 | 6 | 5 | 1 |
    | A | 6 | 5 | 1 |
    | F2 | 6 | 5 | 1 |

  - All declared bindings are disjoint, and no factor's `decides` expression reads another factor's binding (checked by a script).
  - Shared, undeclared input: F2's statement_through is read by both current_document_measure (tier 1) and payoff_readiness (tiers 1 and 2), and is bound in neither. Observation O2-2.
  - CG-3 reachability re-test, member by member:
    - **a. E.evidence_clock_anchor: closed.** Tier 1 (extension period: a pre-death case already in extension, then reclassified, keeps its status), tier 2 (resolution deadline ≤ 30 days after the response deadline) and tier 3 (otherwise, which is the baseline) are all reachable under the sentence that now says "on or after".
    - **b. F1.document_horizon: reworded, but NOT closed. New member R2-N1.**
    - **c. estate_resolution: removed** and replaced by successor_takeover. Its tiers (≤ 7, 8–30, > 30 days since the latest accepted declaration) are reachable, because a successor may declare and request the first extension weeks apart. Closed.
    - **d. carried_request: closed.** Tier 2 is now "filed by someone other than the borrower of record".
    - **e. F2.current_document_measure: closed.** Tier 3 is a current listing agreement, which is reachable under the current-document gate.
    - **f. F2.prior_grant_cut: closed.** Tier 3 is "the request behind the last grant rested on a financing commitment", which is reachable.
    - A.filing_lead fall-through "> 30 days" is reachable. The no-pending guards now sit outside the ladders as plain refusal sentences.
  - Floors: "a total below 30 is raised to 30" replaces "negative counts as zero". The zero-day-extension observation is closed.

### findings (revision 2)
**R2-N1 — SOURCE-FACTOR RED (F1.document_horizon fall-through: unreachable or perverse).**
- Evidence (F1 rule): "…where it is a listing agreement dated no more than 180 calendar days before the request was received, the extension runs from the current resolution deadline to 180 calendar days after the listing date…; where it is a listing agreement dated more than 180 calendar days before the request was received, whose listing term had already run when the request arrived, the extension is the plan's extension days."
- Evidence (inherited, unchanged replaced_by): the extension "is granted only to a borrower or confirmed successor … who is actively marketing the property or obtaining financing".
- Both readings fail:
  - (i) If a listing whose term "had already run when the request arrived" does not show active marketing, then the grant is declined. Tier 3 (the baseline) is unreachable, and CG-3b persists.
  - (ii) If it is granted, the ladder is perverse. Take a request received 15 days before the deadline:
    - A listing dated 179 days before receipt gives deadline → listing + 180 = about −14 days, raised to the 30-day floor, so 30 days plus allowances.
    - A listing dated 181 days before receipt gives the full 90-day plan extension.
    - The expired listing therefore earns three times the time of a still-current one. No servicer would publish that treatment.
- Affected: maturity.extended.yaml, F1 rule (document_horizon sentence), factor document_horizon ladder tier 3.
- Bears on task 0 (charter level). Task 0 itself sits on tier 2 (listing 74 days old).

**R2-N2 — SOURCE-POLICY RED (stale `effect` assertion in F2's prerequisite).**
- Evidence: F2.prerequisite[0].effect reads "The re-filed request with a current financing commitment becomes the request awaiting a decision, so the measured extension runs to 60 days after the commitment date instead of falling back to the plan's extension days."
- Evidence: F2.rule reads "where it is a financing commitment and the loan has a payoff case whose terms are issued with a statement good-through date, the extension runs from the current resolution deadline to 10 calendar days after that good-through date".
- Consequence: on any world with issued payoff terms, including task 1, the effect sentence gives commitment + 60 (52 days on task 1) and the rule gives good-through + 10 (48 days). Two passages of the policy reach different values in the same situation.
- Affected: maturity.extended.yaml, F2.prerequisite[0].effect (and any closure that copies it).

**Observations (revision 2):**
- O2-1: W.counting_convention is now keyed to the latest occupancy inspection finding ("the household living there is given working days"). This is reachable on all three tiers, but it is still a thin business basis for choosing a deadline-counting rule. Observation, as in revision 1.
- O2-2: in F2, the payoff statement both sets the measure (good-through + 10, the "time for the payoff funds to post") and earns payoff_readiness +10 (terms issued plus contract). That grants the same closing and posting interval twice. Neither binding set declares statement_through. Not demonstrable as a second answer.
- O2-3: E tier 1 starts the evidence clock on a past grant date, so with the floor of 1 the due date can be tomorrow. Plausible, since the extension evidence was already on file.

### closing_checklist (revision 2)
Written after the round-2 reveal.
- GT reproduced exactly: task 0 33/29/14/87; task 1 81/79. All factor_sensitivity and baseline figures match.
- Scope: disjoint ({R, W, E, F1} | {A, F2}) and complete.
- Trees: task 0 has 3 prerequisites, 3 value_input edges and a user write; task 1 has 1 prerequisite, 1 value_input edge and a user write. Both acyclic.
- Round-1 REDs:
  - Closed: CG-1, CG-2, CG-3 a, c, d, e, f, T0-F1, T0-C1, T1-T1.
  - CG-3 b: superseded by R2-N1.
- Open:
  - **R2-N1** (SOURCE-FACTOR): F1 document_horizon fall-through, the expired-listing tier.
  - **R2-N2** (SOURCE-POLICY): stale F2←A `effect` text.
- No regression in R, W or A. E's re-keyed anchor is reachable and realistic.
- Not closed. Gates are to be re-run after the rework.

VERDICT revision_2: task0=SOURCE-FACTOR RED task1=SOURCE-POLICY RED charter=R2-N1,R2-N2

## revision_3

### charter_global_frozen (revision 3)
- Frozen 2026-10-15, before any round-3 GT reveal.
- Gate: worklog tail is `REWORK round 3: gates 7/7 green`. `/tmp/erl0064_coord/snapshot.sh maturity_due_and_payable_cases 3` was executed and wrote `snapshot_r3.txt`.
- snapshot_r3 against snapshot_r2:
  - Same greens: EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE (65.00 / 17.50 / 9 / 77), GROUNDING, SCOPE.
  - Traceability: unlock tool-name misses only (non-tool_name 0).
  - validate_scenario: INVALID with tasks_ok 10/10. I called `erlbench.validate.validate_scenario` read-only: all 28 errors are "required document … not found", i.e. before render. No gate is red beyond the allowed form.
- Hashes:
  - charter e50ab8651a75c75c (changed), so every charter-global section is re-derived.
  - task_tools 5fd6ea8653de2143 (unchanged), so action_binding_and_uuids carries forward.
  - masked 0.json 7f525bb60e89d379 (changed); 1.json 5a15699daa40adbe (unchanged).
  - The base section is still byte-identical to blueprint.

### re-derived checks (revision 3)
- **Changes from revision 2** (I diffed the R, W and E dumps against the revision-2 dump; A was compared clause by clause):
  - R, W, E: the replaced_by and rule sentences are restated general-first, then "for … and only for such …". The W assembly sentence becomes "the base count with every addition made and every deduction taken". The compute is unchanged and the merged meaning is unchanged.
  - A: unchanged.
  - F1:
    - The overwrites are restated general-first.
    - The baseline is now "runs from the current resolution deadline to 180 days after the date on the extension request's supporting document … raised to 30 when fewer and limited to the plan's extension days when more". This is self-sufficient and every sentence is in the rule.
    - document_horizon now has three tiers: financing to commitment + 60; listing older than 90 days at receipt to listing + 150 ("a month short of its six-month term so that its price is reviewed sooner"); listing no older than 90 days to listing + 180, which equals the baseline.
  - F2:
    - payoff_readiness is removed and replaced by sale_price_review: contract price ÷ case appraised value below 95 adds 14; 95–100 adds 7; otherwise 0.
    - statement_through is now bound to current_document_measure.
    - prerequisite `effect` is rewritten to name both commitment branches.
- **rule_compute_equivalence**: PASS, apart from observation O3-1 below.
  - The new tiers each have a rule sentence and a compute branch. The F1 compute falls back on `request_document_date or deadline_now`, which only matters for an empty evidence date, and such a request is declined anyway.
  - Bindings are disjoint across all six policies. No factor's bound expression reads another factor's binding (script check). `authoring` phrase sweep: none.
- **prerequisite_graph / sentences**: same five state-form edges. Each policy_source is verbatim in its own rule, each gate is a real binding, and the graph is acyclic.
  - **R2-N2 closed**: F2←A effect now reads "…running to 10 days after the payoff statement's good-through date when the loan has issued payoff terms and otherwise to 60 days after the commitment date, instead of the plan's extension days a listing request gives". This matches the F2 rule.
- **override_declarations**: F1 and F2 each restate the same base clauses general-first with mutual exceptions ("apart from a further extension on a Summit loan's case" / "apart from the first extension on a Summit loan's case whose borrower has died"). Read together, the merged meaning is unique, and further extensions keep "the same grant conditions". F1's text alone attaches "apart from" after the grant conditions; F2's text supplies them. Observation O3-2.
- **factor_ladders (revision 3)**:

  | policy | factors | parameter | method |
  |---|---|---|---|
  | R | 5 | 4 | 1 |
  | W | 4 | 3 | 1 |
  | E | 4 | 3 | 1 |
  | F1 | 6 | 5 | 1 |
  | A | 6 | 5 | 1 |
  | F2 | 6 | 5 | 1 |

  - **R2-N1 closed**: F1.document_horizon is now monotone in listing age. A listing older than 90 days (including an expired one) gets a shorter horizon (listing + 150), never the full plan days. All three tiers are reachable under the evidence gate, and the fall-through (fresh listing, listing + 180) is the baseline. The "price reviewed sooner" rationale is a plausible proprietary marketing-term rule.
  - **New: F2.sale_price_review.** See R3-N1.

### findings (revision 3)
**R3-N1 — SOURCE-FACTOR RED (F2.sale_price_review weighs a condition the business does not weigh on a sale that pays the loan in full).**
- Evidence (F2 rule): "The sale price share is the price on the accepted purchase contract on the loan's payoff file divided by the case's as-is appraised value …; where it is below 95, 14 calendar days are added for Cedarline's review of a sale below the appraised value; where it is at least 95 and below 100, 7 calendar days are added for that review; where it is 100 or more, or no accepted purchase contract is on the payoff file, nothing is added."
- Real practice: a reverse-mortgage servicer, HECM or a non-recourse proprietary product like Summit, reviews a sale price against the appraisal only when the sale proceeds will not repay the debt in full. HUD's rule lets the estate sell for the lesser of the loan balance or 95% of the appraised value (24 CFR 206.125(c); Mortgagee Letter 2008-38), so the 95%-of-appraisal test applies only to sales below the loan balance.
- When the contract repays the loan in full, the servicer has no exposure and no review step. A has the payoff-coverage test it needs ("net amount covers the required payoff amount"); F2's tiers lack it.
- The skill's test: one part of each non-fall-through tier ("price below 95 / below 100 of appraised value") is not weighed by this line of business for a sale that pays the loan off. Its outcome, days added "for Cedarline's review of a sale below the appraised value", is a review no servicer runs on a full payoff.
- Consequence on task 1: see `1.md` revision_3.
- Affected: maturity.extended.yaml, F2 rule (sale price sentence), factor sale_price_review.

**Observations (revision 3):**
- O3-1: F1 compute_basis `deadline_now` still quotes "the extension runs from the current resolution deadline to 60 calendar days after the commitment date". That string is no longer verbatim in the F1 rule, which now reads "…sets how far the extension runs from the current resolution deadline: where that document is a financing commitment, to 60 calendar days after the commitment date". It is stale basis text with no value consequence, and check_extended does not catch it. R's `deadline_now` also has no basis, as in every revision.
- O3-2: F1's general-first replaced_by places "apart from a further extension on a Summit loan's case" after the grant conditions. Read alone it can exempt Summit further extensions from those conditions; F2's replaced_by restores "on the same grant conditions".
- O3-3: within F2, balance_to_value_days and sale_price_review both divide by the case's appraised value. That shared case field is not a declared binding, but neither factor reads the other's binding.
- The revision-2 observations O2-1 (counting convention basis) and O2-3 stand. O2-2 (payoff double-count) is closed by removing payoff_readiness.

### closing_checklist (revision 3)
Written after the round-3 reveal.
- GT reproduced exactly: task 0 33/29/14/40; task 1 81/76. All factor_sensitivity, baseline and closure figures match.
- Scope remains disjoint and complete. Both trees hold (task 0: 3 prerequisites, 3 value_input edges, user write; task 1: 1 prerequisite, 1 value_input edge, user write). The graph is a DAG.
- Round-2 REDs: R2-N1 closed, R2-N2 closed. O2-2 closed.
- Open: **R3-N1** (SOURCE-FACTOR), the F2 sale_price_review tiers apply an appraisal-price review to sales that repay the loan in full.
- Observations (no rework required): O3-1 (stale F1 `deadline_now` basis quote), O3-2, O3-3, O2-1, O2-3.
- Gates on this form: all green except the allowed traceability unlock misses and the pre-render validate errors (`snapshot_r3.txt`).
- Not closed while R3-N1 is open.

VERDICT revision_3: task0=PASS task1=SOURCE-FACTOR RED charter=R3-N1

## revision_4

### charter_global_frozen (revision 4)
- Frozen 2026-10-15, before the round-4 reveal.
- Gate: worklog tail is `REWORK round 4: gates 7/7 green`. `snapshot.sh … 4` was executed and wrote `snapshot_r4.txt`.
- snapshot_r4 against snapshot_r3:
  - Same greens. COMPUTE branches are 66.00, against 65.00.
  - Traceability: unlock tool-name misses only.
  - validate_scenario: INVALID with tasks_ok 10/10. The read-only validator call shows all 20 errors are "required document … not found", i.e. before render.
- Hashes:
  - charter 755bfc2d36d035ca (changed from e50ab8651a75c75c).
  - task_tools 5fd6ea8653de2143 (unchanged).
  - masked 0.json 7f525bb60e89d379 and 1.json 5a15699daa40adbe, both unchanged from revision 3.
  - The base section is still byte-identical to blueprint.

### re-derived checks (revision 4)
- **Changes:**
  - R, W, E, F1 and A: params, factor sets and result expressions are identical to revision 3. Only compute_basis text moved:
    - F1 `deadline_now` now quotes "sets how far the extension runs from the current resolution deadline", which is verbatim in the rule. **O3-1 closed.**
    - R `deadline_now` now has a basis.
  - F2:
    - sale_price_review is removed and replaced by **closing_charge_days**: "Where the loan's Summit Tax and Insurance Reserve is active but holds less than one year's property tax and hazard premium on file, 7 calendar days are added for clearing the coming charges at closing; where that reserve is depleted, 14 calendar days are added; otherwise nothing is added."
    - A new rule sentence, "The case's as-is appraised value is the appraised value recorded on the case", backs a separate unbound `case_appraised_value` binding. It is now read only by equity_share. **O3-3 closed.**
- **R3-N1 closed.** No factor of F2 tests a sale price against the appraisal any more.
- closing_charge_days:
  - Its tiers (active and short / depleted / otherwise, i.e. active and funded or no reserve) are pairwise distinct and all reachable for a further extension.
  - The outcome, time to clear coming tax and insurance charges at closing when the reserve cannot cover them, is a plausible proprietary schedule. It mirrors A's reserve_charge_allowance and does not conflict with it: A sizes the request, F2 sizes the grant.
  - Its label (parameter) is honest.
- rule_compute_equivalence: PASS. Every binding has a basis whose sentences are verbatim in its own rule (script check). Baselines are in the rules. Bindings are disjoint, and no factor reads another factor's binding.
- Counts: F2 now has 6 factors, 5 parameter and 1 method. Multi-source factors: current_document_measure (request plus payoff case) and prior_grant_cut (grant event plus accepted request). Cross-difficulty factors: closing_charge_days (setaside) and household_occupant_days (residency). The other policies are as in revision 3.
- prerequisite_graph and sentences: unchanged and PASS. F2's effect text is as in revision 3, correct. The authoring-phrase sweep finds nothing.
- override_declarations: unchanged from revision 3 (O3-2 stands as an observation).

### findings (revision 4)
- No new charter RED.
- Observations still standing (none requires rework): O2-1 (counting-convention basis), O2-3 (E tier-1 floor), O3-2 (F1's general-first replaced_by read alone).

### closing_checklist (revision 4)
Written after the round-4 reveal.
- Per-task files 0.md and 1.md correspond one-to-one with the tasks, with revisions 1–4 appended and never rewritten. Every task carries a revision-4 comparison: PASS.
- Coverage and scope: the six extended policies are covered by two disjoint scopes ({R, W, E, F1} | {A, F2}). Task tools are closed, and the uuid8s are independent and unchanged.
- Trees:
  - Task 0: 3 prerequisites, 3 value_input edges, user write E.
  - Task 1: 1 prerequisite, 1 value_input edge, user write A.
  - The whole graph is a DAG. Every edge is false at opening and bears weight, and no tool judges a prerequisite.
- Factors:
  - Every computation has a self-sufficient baseline and 4–6 factors, with at least 2 parameter and 1 method. Each task has multi-source factors (task 0: charge/underway/carried; task 1: prior_grant_cut, current_document_measure, payoff_funds) and cross-difficulty factors (residency, setaside, payoff).
  - Every tier is reachable and distinct, every factor bears weight on its world, and each baseline alone gives a definite number different from gold: task 0 19/30/59/34; task 1 90/90.
- Gates on the final form (`snapshot_r4.txt`): all green except traceability (unlock tool-name only) and validate (pre-render "required document not found" only).
- All REDs from revisions 1–3 are closed. Remaining observations (O2-1, O2-3, O3-2) require no rework.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (revision 5)
- Frozen 2026-10-15, before the round-5 reveal.
- Gate: worklog tail is `REWORK round 5: gates 7/7 green`. `snapshot.sh … 5` was executed and wrote `snapshot_r5.txt`.
- snapshot_r5 against snapshot_r4:
  - Same greens. COMPUTE branches 69.00, branches_max 79.
  - Traceability: unlock tool-name misses only.
  - validate_scenario: INVALID with tasks_ok 10/10. The read-only validator call shows all 20 errors are "required document … not found", i.e. before render.
- Hashes:
  - charter 5d8669752c60d2be (changed from 755bfc2d36d035ca).
  - task_tools 5fd6ea8653de2143 (unchanged, so docstrings still match bodies; XF point 9 holds).
  - masked 0.json 7f525bb60e89d379 and 1.json 5a15699daa40adbe, unchanged.
  - The base section is still byte-identical to blueprint.
- Additional inputs read: `audits/render_source/XF_recipe.md` and `audits/render_source/maturity_due_and_payable_cases/render_r1.md`. No other render_source subdirectory was read.

### render_r1 items (revision 5), each re-checked on the new charter
- **A. Assembly class, all closed.** Each policy now defines in its rule, and in its baseline, the quantity its factors act on, with a default. Each factor's text names that target, and the combination is stated once with its order fixed:
  - A1 / F1: "The measured extension is the calendar days from the current resolution deadline to the end the request's supporting document sets, counted below zero…; the extension length is the measured extension with every addition made and every deduction taken; … raised to 30 … then limited to the plan's extension days …, every addition and deduction being made before the extension length is raised or limited". The baseline includes the floor and cap. Each factor says "added to / taken off the extension length".
  - A2 / F2: same construction. The baseline now carries the 30-day floor and the plan cap.
  - A3 / A: "The requested length is the span with every addition made …, every addition being made before that limit is applied"; the standard span is the plan's extension days.
  - A4 / W: the baseline defines the window count, base count and counting convention, and "all of them made before the count is turned into calendar days".
  - A5 / E: "the evidence window is the base evidence window with every addition made and every deduction taken …, a lower count being raised to 1 after every addition and deduction is made".
  - A6 / R: "the runway length is the base runway length with every addition made and every deduction taken; the additions and deductions change only the runway length". household_runway now decides `base_runway_length`.
- **B. Overwrite hygiene, closed.** A script check confirms every superseded clause is verbatim in its base rule and every replaced_by is verbatim in its own rule.
  - B7 / R: the replaced_by restates the general reclassification (higher rank, new type and event date, keeping status and deadlines, the new type's parameters govern, a death or sale removing any cure option) before its Summit-death scope.
  - B8 / W: "When the loan is called due, the case's response deadline is the plan's successor response days calendar days after that day, because the due-and-payable notice is sent the same day; …" is restated.
  - B9 / W: "and the options letter lists the plan's intent options and the response window" is restated for all cases.
  - B10 / E: "for a deceased borrower's loan" and "as the plan's successor confirmation requirement provides" are restored.
  - F1/F2 reappraisal overwrite: no longer defers to the base rule. It now reads "wherever the plan's reappraisal-for-extension setting calls for one" and "replaced by a new one when a payoff or sale is next evaluated".
  - A sweep for "as the base rule provides", "its own … rule", "set out below", "fixed below", "take the place", "as … figures it" finds none (XF point 5).
- **C. Undefined branches, closed as listed.**
  - C11 / E clock: the rule now states no response deadline → declaration date; extension period without a grant record → response deadline; resolution deadline before the response deadline → declaration date; no resolution deadline → response deadline. Compute matches each.
  - C12 / F1: no accepted declaration → nothing added (the sentinel 999 is gone and None is handled); a document of another kind or undated → "evidence insufficient, no extension …, zero"; no date of death → nothing.
  - C13 / F2: the unused `document_current` is removed. The prerequisite sentence carries the currency test as a state gate (tools still judge nothing). No grant on record → nothing taken off.
  - C14 / A: a span ending before the deadline is zero (MX(0, …) on the span); a missing commission or other cost counts as zero.
  - Negative appraisal age ("dated after … counting as less than 4 months old") is stated in W, E, A and F2.

### XF_recipe points (revision 5)
- Points 1, 2 and 4–7 and 9 hold. A script check over all six policies found:
  - no compute binding without a compute_basis;
  - every basis sentence verbatim in its rule;
  - every baseline sentence in its rule;
  - no computed-but-unused binding;
  - disjoint factor bindings, and no factor's bound expression reading another factor's binding;
  - no authoring phrasing and no 999 sentinel.
- Each factor names its own target quantity and none names another factor's. The only factor-id phrase in a rule is W's "counting convention", which is the baseline-defined quantity itself, not a factor reference.
- Rounding: RND(…, 2) on the equity share and on unrepaid advances matches "rounded half up to two decimal places" and the dollar amounts. Day counts are integers.
- Point 3 (solo and removal tests): the removal test is shown per task below. Solo: with the other factors at their defaults, each factor's tiers move the result in a reachable world. In F1 and F2 the floor of 30 and cap of 90 bind only at the extremes.
- **Point 8 (ties): fails. New R5-N1.**

### findings (revision 5)
**R5-N1 — SOURCE-POLICY RED (the "most recent" record selection leaves same-day ties undefined, and the compute resolves them against the rule's wording).**
- The rules choose records by "the most recently received extension request on the case that is still awaiting a decision" (F1, F2; A refers to it as the request any grant rests on), "the most recently accepted extension request" (F2), and "the most recent accepted intent declaration on the case" (R, W, E). Compute takes them with LATEST(…, date_field='request_date'), which compares dates only.
- The engine's LATEST keeps the first row met on equal dates (`check_compute.py` LATEST: `if best is None or key > best[0]`). So on a same-day tie the earlier-filed row wins. The rule never states a tie rule.
- Demonstrated consequence (F2, charter level):
  - Take a borrower whose pending request, resting on a stale listing, is received on day D, and who re-files in person on the same day D with a current financing commitment. A's rule expressly allows this, and A's tool writes a new received row dated "today".
  - Reading 1 ("most recently received" = the later filing, which A's rule names as the one "any grant rests on"): the measured extension uses the commitment, and the grant proceeds.
  - Reading 2 (the compute's tie-break, i.e. the first row): the measured extension rests on the stale listing, which gives the plan's days, and the prerequisite sentence ("dated no more than 30 days before the day that request was received") is unmet, so there is no grant.
  - Two outcomes for one situation.
- Members of the class:
  - F1: request_document, request_document_date, request_filer, request_received, listing_request_received.
  - F2: request_document, request_document_date, granted_document.
  - R, W, E: recorded_intent (two accepted declarations on one date with different intents).
  - F1: declared_date is date-only, so it is unaffected.
  - XLATEST picks of "the most recent occupancy inspection finding" and of the accepted death notice: two same-day rows are possible but unlikely; listed for completeness.
- Neither task's world contains a tie: task 0's declarations are 05-11 and 10-21; task 1's requests are 10-07 and 10-09. **Neither scored value is affected.**
- Affected: maturity.extended.yaml (F1, F2, A, R, W, E rule sentences and their LATEST bindings).

**Observations (revision 5):**
- O3-2 stands: F1's first replaced_by states nothing for a Summit further extension ("apart from a further extension on a Summit loan's case"). F2's replaced_by of the same base clause supplies "on the same grant conditions". The merged reading is unique.
- The E branches "the case shows no response deadline" cannot be reached by a declaration E takes, because the prerequisite requires a response deadline on or after the declaration day. They are defined anyway, which is harmless.
- O2-1 and O2-3 stand.

### closing_checklist (revision 5)
Written after the round-5 reveal.
- GT reproduced exactly: task 0 33/29/14/40; task 1 81/76. All sensitivity, baseline and closure figures match.
- render_r1 A1–A6, B7–B10 and C11–C14 are all closed. XF points 1–7 and 9 hold.
- Open: **R5-N1** (XF point 8, ties). The "most recent" record selections (F1, F2 request; F2 accepted request; R, W, E declaration) have no stated tie rule, and LATEST keeps the first-inserted row on equal dates. A same-day re-filing, which A's rule allows, gives two outcomes in F2.
- Trees, scope, factor counts and weight: unchanged from revision 4 and PASS.
- Gates: allowed form only (`snapshot_r5.txt`).
- Not closed while R5-N1 is open.

VERDICT revision_5: task0=SOURCE-POLICY RED task1=SOURCE-POLICY RED charter=R5-N1

## revision_6

### charter_global_frozen (revision 6)
- Frozen 2026-10-15, before the round-6 reveal.
- Gate: worklog tail is `REWORK round 6: gates 7/7 green`. `snapshot.sh … 6` was executed and wrote `snapshot_r6.txt`.
- snapshot_r6 against snapshot_r5:
  - Same greens. COMPUTE branches 82.50, branches_max 95.
  - Traceability: unlock tool-name misses only.
  - validate_scenario: INVALID with tasks_ok 10/10. The read-only validator call shows all 20 errors are "required document … not found".
- Hashes:
  - charter 9ab4e3d511f2794f (changed).
  - **task_tools 34edec9170b45641 (changed** from 5fd6ea8653de2143).
  - masked 0.json 7f525bb60e89d379 and 1.json 5a15699daa40adbe, unchanged.
  - The base section is still byte-identical to blueprint.

### task_tools re-check (revision 6)
- The only body change: the two request-writing user tools (declare_successor_intent, supplement_extension_request) now stamp `created_at=_CalendarDays.record_time(ctx.now())`. That is a `YYYY-MM-DDTHH:MM:SS` record time, the same format as every seeded created_at (for example "2026-10-07T16:22:00"), so string order equals time order.
- No new import. Owners are unchanged (declare and supplement user; the rest agent). uuid8s are unchanged.
- No docstring changed or states anything the body lacks (XF point 9).
- No tool judges a prerequisite (bodies only look up the case).

### R5-N1 closure: every member checked for rule tie sentence, compute and probe
Rule tie sentences added, each verbatim in its rule and quoted as the compute_basis of its day binding:
- **Extension requests (F1, F2, A)**: "Among extension requests received on the same day, the more recently received is the one recorded later by its recorded date and time, so that a request re-filed on the day of the request it replaces is the one a grant rests on."
  - F1: listing_request_received / request_received (day) → request_document, request_document_date, request_filer use LATEST(…, date_field='created_at', request_date=day).
  - F2: pending_request_day → request_document, request_document_date.
  - A's replaced_request_received is date-only, so it is tie-insensitive.
- **Accepted request behind the last grant (F2)**: "…the request behind it is the accepted extension request received most recently, and among accepted requests received on the same day the one recorded later by its recorded date and time". Compute: accepted_request_day → granted_document by created_at. last_grant_date is date-only.
- **Intent declarations (R, W, E)**: "Among accepted intent declarations made on the same day, the most recent is the one recorded later by its recorded date and time." Compute: declaration_day → recorded_intent by created_at. F1's declared_date is date-only, so it is tie-insensitive.
- **Inspection findings (R, W, F1, A, F2)**: "Where two occupancy inspection findings carry the same most recent date, a finding that the home is occupied by someone other than a borrower prevails over a finding that it is vacant, and a vacant finding prevails over any other finding." Compute: inspection_day, then XCOUNT for occupied_by_others, then vacant, then any. Two "other" findings fall on the same tier, so their order does not matter.
- **Accepted death notices (R, F1)**: "…among accepted notices received on the same day the one recorded later by its recorded date and time". Compute: date_of_death / death_date read by created_at within the latest received day.
- **Accepted purchase contracts (A)**: "…among accepted contracts received on the same day the one recorded later by its recorded date and time". Compute: contract_day → price, commission and other costs by created_at.

Mechanical probes (scratch script, evaluating the charter's own compute with `check_compute.py`'s `build_env`/`eval_compute` on the masked views):
- **Same-day re-filing (F2)**: task-1 world at 2026-10-07 18:00; pending request 506b8a84 received 10-07 16:22; re-filing received 10-07 18:00 with commitment 10-05. The result picks the re-filing (financing_commitment, measured 48, F2 = 76) whether the new row is inserted after or before the old one. This shows the tie rule, not insertion order, decides. **The two-outcome case of R5-N1 is gone.**
- **Same-day declarations (R)**: two accepted declarations on 2026-10-20 (deed_in_lieu recorded 15:00, sell_property recorded 09:00, inserted sell-first). recorded_intent is deed_in_lieu, the one recorded later, as the rule says.
- **Same-day inspection findings (R)**: a vacant finding added on 2026-08-21 and inserted first. The finding read is occupied_by_others, as the rule's precedence says.
- **Regression**: the gold chains on the masked views give R 33, W 29, E 14, F1 40 (task 0) and A 81, F2 76 (task 1), all unchanged.

### XF re-sweep (revision 6)
A script check over all six policies:
- no compute binding without a basis;
- every basis sentence verbatim in its rule;
- every baseline sentence in its rule;
- no computed-but-unused binding;
- disjoint factor bindings, with the new day bindings bound into their factors;
- no factor's bound expression reading another factor's binding;
- every superseded clause verbatim in its base rule and every replaced_by verbatim in its rule;
- no "as the base rule provides", "its own", "set out below", 999 or authoring phrasing.

Factor counts are unchanged (R 5, W 4, E 4, F1 6, A 6, F2 6, each with 1 method). Prerequisite edges are unchanged and PASS.

### findings (revision 6)
- **R5-N1 closed.** No new RED. The observations from revision 5 stand (O3-2, O2-1, O2-3).

### closing_checklist (revision 6)
Written after the round-6 reveal.
- Per-task files 0.md and 1.md correspond one-to-one with the tasks, with revisions 1–6 appended and never rewritten. Both tasks carry a revision-6 PASS.
- Scope: the six extended policies are covered by two disjoint scopes. Task tools are closed, and the uuid8s are independent and unchanged.
- Trees:
  - Task 0: 3 prerequisites, 3 value_input edges, user write.
  - Task 1: 1 prerequisite, 1 value_input edge, user write.
  - The whole graph is a DAG. Every edge is false at opening and bears weight, and no tool judges a prerequisite.
- Factors:
  - Every computation has a self-sufficient baseline and 4–6 factors (at least 2 parameter and 1 method), all reachable, distinct and bearing weight.
  - Task 0 baseline fall-backs: 19 / 30 / 59 / 34. Task 1: 90 / 90. Each differs from gold.
  - Multi-source and cross-difficulty factors are present in both tasks.
- render_r1 A1–A6, B7–B10 and C11–C14 are closed. XF points 1–9 hold, including ties (R5-N1 closed, with probes).
- Gates on the final form (`snapshot_r6.txt`): allowed form only (traceability unlock tool-name; validate pre-render documents).
- All REDs from revisions 1–5 are closed. Observations O2-1, O2-3 and O3-2 require no rework.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
