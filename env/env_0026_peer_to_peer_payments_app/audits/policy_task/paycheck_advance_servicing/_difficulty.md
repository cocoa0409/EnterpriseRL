# Policy-task audit — paycheck_advance_servicing / charter-global

## charter_global_frozen

- Scenario: `env/env_0026_peer_to_peer_payments_app`, difficulty `paycheck_advance_servicing`, category `advance`, M=2 (tasks 0, 1). Round r1 (first audit round).
- Frozen inputs (sha256):
  - `tasks/paycheck_advance_servicing/advance.extended.yaml` = `a170e21b43e3cdfe817ee7702cf0831e24fd031b0b60ae0b3035fde44af4e15b`
  - `tasks/paycheck_advance_servicing/task_tools.py` = `d4d526e4825ff3420ead2027a390dbe69a394d5c92591b0586eb27043b16ce30`
  - masked view 0 = `80f29a7b8f870eb4a7df087a30e568562a43372e665c8ffd4e967b602389287a`, masked view 1 = `1d2186b73ce2452128fe5b747db7ab15af5e025b929c654a5b277c83f8dce166` (hashes re-computed by the auditor, equal to the brief)
- Freeze time: 2026-09-25T00:18Z (UTC). Auditor: independent policy-task auditor (not the authoring agent).
- Read: `blueprint/blueprint.yaml`, `blueprint/products/advance.yaml` (only to confirm the base copy; `diff` of extended lines 1–911 against it differs only by a trailing newline — base copy verbatim), `blueprint/products/wallet.yaml` and `card.yaml` (variant names and the `wallet_direct_deposit` event only), `blueprint/share_tools.py` (advance finders), the extended charter, `task_tools.py`, the two masked views, the coordinator gate snapshot `coord/snap/d5_r1.txt`.
- Masked and not read while this section was written: `tasks/paycheck_advance_servicing/tasks/*.json`, `tasks/paycheck_advance_servicing/worklog.md`, the authoring scratchpad, other difficulties' tasks and audits, any other scenario. No recursive search was run over `tasks/` or the scenario root. Nothing in this section is derived from a revealed GT.
- Entry conditions: all instantiation-stage gates green per the snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; `check_traceability.py` deferred by the coordinator to the KB step). Masked views and hashes supplied. Input complete.

### policy_conflict_scan

Complete structured policy = 12 base policies (`advance_agg_multi_holding` … `advance_closure`) + 4 extended policies:

| ext policy | trigger | subject | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| `advance_ext_payroll_delay_relief` | state_due | advance_fee_waiver | `grant_payroll_delay_relief_50112cf3` (agent) | [] |
| `advance_ext_largest_advance` | on_request | advance_disbursement | `request_advance_00c9f515` (user) | ← payroll_delay_relief (value_input, state) |
| `advance_ext_late_fee_assessment` | state_due | advance_fee | `assess_late_fee_a649c20a` (agent) | [] |
| `advance_ext_card_repayment_share` | on_request | advance_repayment | `repay_advance_by_card_db2e846d` (user) | ← late_fee_assessment (value_input, state) |

Overlapping subjects:
- `advance_fee_waiver`: base `advance_waivers` (cancellation window, courtesy) vs relief. Declared by two overwrite entries (see override_declarations). The relief is booked with `waiver_reason courtesy`, the same reason the superseded customer-requested courtesy waiver used; after the merge no customer-requested courtesy waiver survives (finding F-OBS-2).
- `advance_disbursement`: base `advance_agg_outstanding` + `advance_disbursement_rules` + `advance_fees` vs largest advance. The effective-limit sentence is declared; the base cap sentence that uses it is not (finding F-POL-1).
- `advance_fee` (late fee): base `advance_late_fees` S2 vs late-fee assessment — declared.
- `advance_repayment` (manual card repayment): base `advance_repayment_rules` S2 vs card share — declared.
- Cross-ext overlaps: the relief reads the most recent late fee, which the late-fee assessment writes; the largest advance's holdback reads late fees and courtesy waivers written by those two; the card share's amount owed reads fees written by the late-fee assessment and waivers written by the relief. Each such coupling that is exercised by a task is carried by a declared prerequisite edge (relief → largest advance; late fee → card share). The couplings late fee → relief and late fee → largest advance are not declared edges; they bind only in a world where a late-fee period is due at the opening on the same line as a relief/largest-advance request (see F-OBS-3 for the task-0 world).
- Eligibility / time anchors: late fees anchor on the advance's due date + grace (ext) and past_due_since (base S1); card share anchors days past due on `past_due_since`; relief anchors the payroll delay on due date → autopay DD collection date. No conflicting anchors for the same quantity.
- Terminal states: relief lowers `outstanding_balance` (possibly below 0, per tool docstring); advance raises it by principal + flat fee; late fee raises it; card repayment lowers it. No two policies claim the same terminal field with different values.
- Cross-category read boundaries: relief reads wallet (history, opened_date, plan) and card (tier, status, form, purchases); largest advance reads wallet (1-month deposits, plan) and card; late fee reads wallet (3-month deposits, plan); card share reads wallet (1-month deposits, plan). Each is declared in `cross_category` and matched by `inputs.cross_category`.

Claimed scope vs blueprint claim: the blueprint claim of this difficulty lists event types `advance_open, advance_repayment, advance_fee_waiver, advance_extension, advance_fee, advance_cure, advance_suspend, advance_reinstate, advance_close`; it does **not** list `advance_disbursement`, which is the subject of `advance_ext_largest_advance` and the event `request_advance_00c9f515` books (plus its `advance_fee`). No other difficulty of the blueprint claims `advance_disbursement` (the four other claims are wallet/card/business/rewards), so there is no cross-fire; the blueprint summary of this difficulty names "requesting a new advance" as a customer decision in scope. Recorded as observation F-OBS-1.

Task-scope exclusivity and completeness: the prerequisite graph has exactly two components, {relief → largest advance} and {late fee → card share}; with M=2 the only partition in which every task's scope spans a whole tree is one component per task, which is exclusive and covers all four extended policies. Which component each task claims is established from its own world in the task files.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and every rule sentence back against compute.

`advance_ext_payroll_delay_relief`
- `late_fee_amount` LATEST late_fee by entry_date ↔ "The relief acts on the late fee most recently booked on the line." ✓
- `advance_due_date`/`collection_date`/`payroll_delay_days` ↔ "counted in calendar days from the due date of the line's most recent advance to the date of the line's most recent autopay collection from a direct deposit" ✓; `delay_share` ↔ the ≥long / ≥short / shorter ladder ✓.
- `dd_count_6m`/`dd_total_6m` with `within_months=6` ↔ the window sentence ("records dated after the same day of the month that many months before … up to and including the handling date") ✓; `regularity_share` both parts in each tier, "without meeting both parts of the higher test" realised by the else-branch ✓.
- `account_age_days` from wallet `opened_date` ↔ "linked personal account was opened" ✓; `account_share` ✓.
- `late_fees_12m <= 1` ↔ "no late fee in the twelve months … other than the one relieved": equivalent only while the relieved fee itself lies inside the 12-month window; if it lay outside, compute would still admit one other fee. Not exercised by task 0 (the relieved fee is in the window). Observation F-OBS-4.
- `plan_share`, `relief_share`, `unrounded_relief`, `card_tier` (active physical), `card_purchases_3m`, `rounded_relief` (multiplier before rounding), `result = MN(late_fee, rounded)` ↔ rule sentences 7–11 ✓. The rule's eligibility clauses (qualifying fee, advance repaid in full, no request needed) are gates, not compute; no compute binding lacks a rule sentence.

`advance_ext_largest_advance`
- `payroll_bonus` (≥2×dd_min and ≥2 deposits / ≥dd_min and ≥dd_min_deposits_count), `plan_bonus` (2×plan_limit_bonus / plan_limit_bonus / 0), `tenure_bonus` on the **line** `opened_date`, `track_bonus` on 12-month disbursement count, `kept_late_fees` = 12-month late fees − 12-month courtesy waivers, `holdback` ("reach" = ≥), `remaining_principal` = MX(0, disbursed − MX(0, repaid + waived − fees)), `room` order, `adjusted_room`, `result` = floor to advance_increment ↔ rule sentences 3–13 ✓. No invented basis.
- Rule S1 ("flat advance fee and due date … are those of the fee and disbursement rules") is realised by the base `advance_fees.formula` and `repayment_term_days`, not by this compute; the tool takes `due_date` and `flat_fee` as arguments. ✓ (no empty promise: the base formula exists.)

`advance_ext_late_fee_assessment`
- `unpaid_principal` line-wide ↔ S3 ✓; `advance_principal`/`advance_due_date` LATEST disbursement ↔ S1/S2 ✓; `period_number = int((DAYS(due,NOW) − grace)/interval)` ↔ "most recent block that has closed by the handling date" ✓.
- `weekly_rate` (3-month deposits ≥ 3×dd_min AND never a late fee → steady_rate_first; ≥ AND carried → steady_rate_repeat; else late_fee_pct_weekly) ✓; `repaid_share`, `collection_factor` ✓; `plan_factor` ✓; `rated_fee` product ✓; `treated_fee` floor (`int(RND(x*100,6))/100`) on period 1, half-up otherwise ✓; `cap_room` = cap% × advance principal − late fees booked on the line ✓; `result = MN(MX(treated, min), cap_room)` ↔ S10 order ✓.
- The rule states no condition that the advance is still unpaid when a period closes (S1 "When a full late-fee period has closed on the line's most recent advance after its grace period"); compute has none either — the two faces agree, but see F-OBS-3.

`advance_ext_card_repayment_share`
- `amount_owed` ↔ S3 ✓; `track_share` (line age AND all-time advances count) ✓; `payroll_share` (≥dd_min AND ≥2 / ≥dd_min/2) ✓; `card_history_share` (≥2 / ==1 / 0 over all-time `manual_debit_card` repayments) ✓; `plan_share` ✓; `share_points` ✓; `days_past_due` from `past_due_since` ✓; `timed_share` ✓; `result = MN(owed, MX(min_manual_repayment, RND(owed × share/100, 2)))` ↔ S5/S10 ✓.

Every declared factor's ladder tiers appear both as rule sentences and as branches of the `decides` binding, and no branch lacks a rule tier. Result: rule ↔ compute equivalence holds in both directions (one observation, F-OBS-4).

### action_binding_and_uuids

- `(target_tool, computes)`: `(grant_payroll_delay_relief_50112cf3, amount)`, `(request_advance_00c9f515, amount)`, `(assess_late_fee_a649c20a, amount)`, `(repay_advance_by_card_db2e846d, amount)` — each claimed by exactly one policy. ✓
- uuid8s `50112cf3`, `00c9f515`, `a649c20a`, `db2e846d`: no shared prefix, no shared tail, no sequence or adjacency; independently generated as far as can be judged. ✓
- Docstrings: none names another tool, none states a position in a sequence. The words "afterwards" (return value `outstanding_balance … afterwards` in request/assess/repay) and "first" (`fee_period` "1 for the first full late-fee period") describe the tool's own effect / an ordinal, not an order between actions. ✓
- Tool bodies (read in full): each does `ctx.find(...)[0]`, creates the ledger row(s) with the given values and updates `outstanding_balance`; none checks status, dates, prior waivers/fees, amounts or any prerequisite; none computes an amount. ✓ The tool layer judges no prerequisite.
- Business-reading uniqueness: `request_advance` is fixed to standard delivery to the external debit card, matching ext rule S1; `grant_payroll_delay_relief` fixes `waiver_reason courtesy`; `assess_late_fee` fixes `fee_type late_fee`; `repay_advance_by_card` fixes `manual_debit_card`. No confirmation, review or wait outside the policies is added.

### prerequisite_graph

- `prerequisite` filled in on all four ext policies (`[]` on relief and late fee). ✓
- Edges: largest_advance → `advance_ext_payroll_delay_relief`; card_repayment_share → `advance_ext_late_fee_assessment`. Both point at ext policy ids in this file, not at a base policy, not at self. Graph acyclic (two disjoint 2-node chains). ✓
- `policy_source` verbatim in the blocked policy's own rule: largest advance rule S2 = "The largest advance a line can take is worked out only after every late fee on the line that qualifies for payroll-delay relief carries its relief waiver entry." ✓; card share rule S2 = "The card repayment share is not applied until the line carries a late fee entry for every late-fee period that has closed on its past-due advance." ✓
- `form: state` on both, no `fallback_reason` on either. ✓
- `condition` vs sentence: edge 1 condition names the relief's qualifying conditions (autopay from a DD posted after the due date, advance repaid in full) and an `advance_fee_waiver` row with `waiver_reason courtesy` pointing at the fee — same strength and scope as "every late fee … that qualifies for payroll-delay relief carries its relief waiver entry". Edge 2 condition "for every full late-fee period that has closed after the grace period of the line's past-due advance, an advance_fee row with fee_type late_fee and that period's fee_period stands" — same as the sentence. Neither strengthened nor weakened. ✓
- `resolved_by` = the depended-on policy's `target_tool` on both; the write creates exactly the row the condition names. ✓
- `kind: value_input` with `gate` = `kept_late_fees` (exists in largest-advance compute) and `amount_owed` (exists in card-share compute). ✓ Effects stated ("kept_late_fees falls and the holdback tier can change"; "amount_owed … rise") are genuinely what those bindings do.
- No authoring-viewpoint wording ("in this task", "at the opening") in any `prerequisite` field. ✓

### prerequisite_sentences

Edge 1 (largest advance ⇐ relief):
- Four-point test: ordering connective "only after" ✓; waited-on thing is a state ("every late fee … carries its relief waiver entry"), with no action, performer or tool ✓; no tool name, no policy id, no snake_case, no row id ✓ ("payroll-delay relief" is the business name of the waiver kind, the same words the relief rule uses); strength = the condition ✓.
- Exactly one write of this difficulty brings "a late fee carries its relief waiver entry" about: `grant_payroll_delay_relief_50112cf3` is the only tool that books an `advance_fee_waiver`. ✓
- Derivation a reader performs: sentence → "which late fees qualify for payroll-delay relief?" → relief rule S1 ("A late fee booked on an advance whose autopay collection came from a direct deposit that posted after the advance's due date … booked once that advance is repaid in full as a waiver of that one late fee with waiver_reason courtesy") → records: late fee rows, the advance's due date, its `autopay_direct_deposit` repayment date, whether it is repaid in full → for each qualifying fee lacking a waiver, the relief rule is the write that brings the state about. Single reading. ✓
- The relief rule does not restate the sentence; the largest-advance rule carries no second wording, no tool name. ✓

Edge 2 (card share ⇐ late fee):
- "not … until" ✓; state "the line carries a late fee entry for every late-fee period that has closed on its past-due advance" ✓; no tool/id ✓; strength = condition ✓.
- Only `assess_late_fee_a649c20a` books an `advance_fee` with `fee_type late_fee` (`request_advance` books `fee_type advance_fee`). ✓
- Derivation: sentence → "which periods have closed?" → late-fee rule S2 (blocks of `late_fee_interval_days` from grace end; most recent closed block) → records: past-due advance's due date, grace_period_days, existing late-fee rows by `fee_period` → the late-fee rule is the write. Single reading. ✓ The late-fee rule does not restate it. ✓

Undeclared cross-problem orders in rules:
- Relief rule S1 "booked once that advance is repaid in full" states that the relief waits on a state (advance repaid in full) that a repayment write — including `repay_advance_by_card_db2e846d` — can bring about; no edge is declared for it. It is a copy of base `advance_waivers` S3's eligibility ("only once the advance it belongs to is repaid in full") and it binds in no task of this difficulty whose tree contains both policies (the relief and the card share lie in different components). Observation F-OBS-5.
- Base rules with cross-problem orders (`advance_closure` S3 "Closing the personal account requires the advance line to be closed first") ground no edge and no tree rests on them. ✓
- No `prerequisite` edge is declared anywhere without a rule sentence. ✓

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry.

`advance_ext_payroll_delay_relief` ← `advance_waivers`
- S1 (cancellation-window waiver of flat/express fee): superseded, declared; replaced_by "A payroll-delay relief is granted without regard to the cancellation window, which governs only the flat advance fee and the express fee." The replacement no longer states the waiver itself (flat/express fee waived when repaid within the window) — the base S2 counting sentence and the `cancellation_window` eligibility block still presuppose it. Declared, so legal; the dropped statement of the cancellation-window waiver bears on no task of this difficulty (no advance in either world is repaid within its window). Observation F-OBS-6.
- S2 (counting in full hours; express waived only to personal balance): followed / not touched.
- S3 (courtesy late-fee waiver at request, per-year cap, after full repayment): superseded, declared; replaced by the unrequested relief. After the merge the per-year courtesy waiver at the customer's request has no surviving sentence (F-OBS-2).
- S4 (each fee waived at most once): followed (relief once per fee; `waive_once` inherited).
- S5 (flat fees outside the window, extension fees, fees on a written-off advance never waived): followed.

`advance_ext_largest_advance` ← `advance_agg_outstanding`, `advance_disbursement_rules`, `advance_fees`
- `advance_agg_outstanding` S1 clause (a) "the count of advances not yet fully repaid plus the new one may not exceed max_outstanding_advances": followed (inherited gate).
- `advance_agg_outstanding` S1 clause (b) "**and their remaining principal plus the new advance may not exceed the effective limit**": **not named in `overwrite`**, and handled differently by the extension — the extension's room adds `payroll_high_bonus/low`, `tenure_*_bonus`, `track_*_bonus` and up to 2×`plan_limit_bonus`, and multiplies by `card_uplift_*`, so the new advance can exceed any reading of the effective limit. Its referent was superseded: S2 (the definition "The effective limit is advance_limit plus plan_limit_bonus … fees never count toward it") is declared and replaced by "The room for a new advance starts from the tier's advance_limit", which defines a different quantity ("room") and leaves "the effective limit" of S1 either undefined or equal to the tier's `advance_limit`. Finding **F-POL-1 (SOURCE-POLICY RED)**.
- `advance_agg_outstanding` S3 (monthly count): followed.
- `advance_disbursement_rules` S1 (line active), S2 (destinations), S4 (cooldown), S5 (due date, delivery fees), S6 (customer confirms): followed. S3 "The amount is at least min_advance_amount and a whole multiple of advance_increment, **within advance_agg_outstanding**": the first two parts are followed; "within advance_agg_outstanding" re-imports the cap of F-POL-1 and is likewise not named in `overwrite`.
- `advance_fees` S1–S4: followed (ext S1 says the flat fee is that of the fee rules).

`advance_ext_late_fee_assessment` ← `advance_fees`, `advance_late_fees`, `advance_extensions`
- `advance_late_fees` S1 (past_due status and `past_due_since`): followed. S2 (per-period late fee, per-advance cap): superseded, declared (per-period fee now line-wide unpaid principal, cap now "advance's principal less the late fees already booked on the line"). S3 (no late fee while an extension's new due date + grace has not passed): followed.
- The replaced_by sentence states the fee as "unpaid principal times late_fee_pct_weekly, rounded to the cent (half up)", while ext S6 substitutes the weekly rate ("in place of late_fee_pct_weekly") and S9 rounds the first period down; the ext rule itself fixes their relation ("the first-period treatment then rounds that product, and only then are the minimum and the cap applied"), so the merged semantics is unique (baseline sentence + declared factors).
- `advance_fees` S4 ("no fee other than those named in this charter"): followed. `advance_extensions`: no sentence touched.

`advance_ext_card_repayment_share` ← `advance_repayment_rules`
- S1 (autopay), S3 (fees then principal), S4 (on-time counting), S5 (autopay off refused): followed.
- S2 (manual repayment bounds): superseded, declared; replaced_by covers only the past-due card case, so manual repayments on a current line or from the personal balance lose their stated bounds after the merge. Bears on no task (task 1 is past-due by card). Observation F-OBS-7.

Undeclared overrides found: F-POL-1 only. Demonstration of its consequence belongs to the task whose world exercises `advance_ext_largest_advance`.

### factor_ladders

Per policy (label as declared → label as audited):

`advance_ext_payroll_delay_relief` — 6 factors; baseline "late fee × standard_share, rounded, ≤ late fee"
| factor | decides | declared | tiers | tiers distinct | multi-source | cross_difficulty | audited label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| payroll_delay | delay_share | parameter | 3 (≥14 d / 7–13 d / <7 d) | 0.20/0.10/0 ✓ | no (one aggregate: due date→collection date, both on the advance) | — | parameter ✓ |
| payroll_record | regularity_share | parameter | 3 | 0.10/0.05/0 ✓ | count AND total over the same wallet rows | wallet | parameter ✓ |
| account_age | account_share | parameter | 3 | 0.05/0.02/0 ✓ | no | wallet | parameter ✓ |
| lateness_record | clean_share | parameter | 3 | 0.05/0.02/0 ✓ | late-fee rows AND disbursement rows ✓ | — | parameter ✓ |
| plan_membership | plan_share | parameter | 3 | 0.10/0.05/0 ✓ | no | wallet | parameter ✓ |
| card_multiplier | rounded_relief | **method** | 3 | ×1.4/×1.2/×1 | card account AND card purchases ✓ | card | **parameter** (see F-FAC-1) |

`advance_ext_largest_advance` — 6 factors; baseline "advance_limit − remaining principal, floored to advance_increment"
| factor | decides | declared | tiers | tiers distinct | multi-source | cross | audited |
| --- | --- | --- | --- | --- | --- | --- | --- |
| payroll_bonus | payroll_bonus | parameter | 3 | 50/25/0 ✓ | total AND count over same wallet rows | wallet | parameter ✓ |
| plan_bonus | plan_bonus | parameter | 3 | 2×plan_limit_bonus / plan_limit_bonus / 0 — collapses to 0/0/0 on Starter (`plan_limit_bonus: 0.00`) | no | wallet | parameter ✓ (F-OBS-8) |
| line_tenure | tenure_bonus | parameter | 3 | 30/15/0 ✓ | no | — | parameter ✓ |
| borrowing_track | track_bonus | parameter | 3 | 20/10/0 ✓ | no | — | parameter ✓ |
| lateness_holdback | holdback | parameter | 3 | 40/20/0 ✓ | late-fee rows AND courtesy-waiver rows ✓ | — | parameter ✓ |
| card_uplift | adjusted_room | **method** | 3 | ×1.10/×1.05/×1 | card account AND purchases ✓ | card | **parameter** (F-FAC-1) |

`advance_ext_late_fee_assessment` — 4 factors; baseline "unpaid principal × late_fee_pct_weekly, half-up, ≥ min, ≤ cap room"
| factor | decides | declared | tiers | tiers distinct | multi-source | cross | audited |
| --- | --- | --- | --- | --- | --- | --- | --- |
| steady_payroll_rate | weekly_rate | parameter | 3 | 0.50/0.75/late_fee_pct_weekly — on Elite (`late_fee_pct_weekly 0.75`) tier 2 and fall-through coincide | wallet deposits AND advance late-fee rows ✓ | wallet | parameter ✓ (F-OBS-8) |
| collection_credit | collection_factor | parameter | 3 | 0.8/0.9/1 ✓ | no | — | parameter ✓ |
| plan_factor | plan_factor | parameter | 3 | 0.8/0.9/1 ✓ | no | wallet | parameter ✓ |
| first_period_treatment | treated_fee | method | 3 | ×0.75 & round **down** / ×0.9 & round **down** / round **half up** | period number AND line age ✓ | — | method ✓ (rounding mode changes between tiers) |

`advance_ext_card_repayment_share` — 5 factors; baseline "what the line owes × standard_share %, half-up, ≥ min_manual_repayment, ≤ owed"
| factor | decides | declared | tiers | tiers distinct | multi-source | cross | audited |
| --- | --- | --- | --- | --- | --- | --- | --- |
| track_record | track_share | parameter | 3 | 20/10/0 ✓ | line opened_date AND ledger disbursement count ✓ | — | parameter ✓ |
| payroll_points | payroll_share | parameter | 3 | 15/5/0 ✓ | high tier total AND count over same rows | wallet | parameter ✓ |
| card_history | card_history_share | parameter | 3 | 10/5/0 ✓ | no | — | parameter ✓ |
| plan_points | plan_share | parameter | 3 | 10/5/0 ✓ | no | wallet | parameter ✓ |
| arrears_timing | timed_share | **method** | 3 | ×1.2/×1.1/×1 | no | — | **parameter** (F-FAC-1) |

Structural checks common to all four:
- Every factor's `bindings` are disjoint from the other factors' bindings of the same policy; every `decides` is an input, never `result`. ✓
- Every ladder has 3 pairwise-disjoint tiers as stated, and every tier (condition and value/method) is a sentence of the policy's `rule` and a branch of the `decides` binding. ✓
- Every factor's fall-through tier equals its `baseline` binding, and every `baseline` equals what the policy's `baseline.rule` states for that input (0 added share / 0 bonus / 0 holdback / factor 1 / weekly rate late_fee_pct_weekly / half-up rounding as it stands / no multiplier). ✓ `baseline.rule` sentences are all rule sentences; `baseline.params` are the keys the baseline uses. ✓
- Business realism of conditions and outcomes: payroll delay, payroll regularity, account age, late-fee record, plan, card relationship for a late-fee relief; payroll, plan, tenure, track, kept late fees, card relationship for an advance amount; steady payroll, repayment progress, plan, first-period leniency for a late fee; track, payroll, prior card use, plan, age of the arrears for a daily card-repayment cap — each is a consideration earned-wage-access / small-dollar lenders publish in some form, and no condition holds of every customer who reaches the write. No tier value is a straw man (fall-throughs are the plain standard method). The card-share premise (a daily cap on how much of a past-due balance may be repaid by debit card) is unusual but coherent (daily card-funding limits). No unreal-ladder finding.
- Counts after F-FAC-1: relief 6 factors / 6 parameter / **0 method**; largest advance 6 / 6 / **0 method**; late fee 4 / 3 / 1 ✓; card share 5 / 5 / **0 method**. Multi-source and cross-difficulty per task: tree {relief, largest} has multi-source (lateness_record, lateness_holdback, card_multiplier, card_uplift) and cross-difficulty (wallet, card) ✓; tree {late fee, card share} has multi-source (steady_payroll_rate, first_period_treatment, track_record) and cross-difficulty (wallet) ✓.

Whether each factor bears weight is decided in the task files (`factor_weight`).

### findings

**F-POL-1 — SOURCE-POLICY RED (undeclared override of the advance limit cap).**
- Symptom: the extension computes a largest advance that exceeds the ceiling the inherited base sentence imposes on every new advance.
- Root cause: `advance_ext_largest_advance.overwrite` names only `advance_agg_outstanding` S2 (the definition of the effective limit). The base cap itself — `advance_agg_outstanding` S1 "…and their remaining principal plus the new advance may not exceed the effective limit" — and its echo in `advance_disbursement_rules` S3 "…a whole multiple of advance_increment, within advance_agg_outstanding" are not named, yet the extension handles that quantity differently (bonuses 25–100 per factor, card uplift ×1.05/×1.10 on top of `advance_limit`). The replaced_by "The room for a new advance starts from the tier's advance_limit" defines "room", not "effective limit", so after the merge the base cap either refers to an undefined term or reads as `advance_limit` (the replacement's only anchor); under the unreplaced base definition it reads as `advance_limit + plan_limit_bonus`.
- Evidence: `advance.extended.yaml` base `advance_agg_outstanding.rule` S1 (line 631); `advance_disbursement_rules.rule` S3 (line 670); `advance_ext_largest_advance.overwrite` (lines 1129–1134) naming only the S2 sentence; ext rule S7–S13 (lines 1164–1170).
- Demonstrated consequence: in any world where a bonus or uplift tier is taken, the room exceeds `advance_limit + plan_limit_bonus − remaining principal`, and the base cap gives a second defensible answer. Demonstrated against task 0's world in `0.md`.
- Affected: `advance_ext_largest_advance.overwrite`; base `advance_agg_outstanding` S1 and `advance_disbursement_rules` S3 as inherited; the scored `amount` of `request_advance_00c9f515`. Bears on: the task whose tree contains `advance_ext_largest_advance`.

**F-FAC-1 — SOURCE-FACTOR RED (mislabelled `method` factors; no honest method factor in three computations).**
- Symptom: `card_multiplier` (relief), `card_uplift` (largest advance) and `arrears_timing` (card share) are labelled `method`, but each tier only substitutes a different number into the same formula.
- Evidence (compute, verbatim structure):
  - relief `rounded_relief`: `RND(unrounded_relief * 1.4, 2)` / `RND(unrounded_relief * 1.2, 2)` / `RND(unrounded_relief, 2)` — one formula `RND(unrounded_relief × m, 2)`, m ∈ {1.4, 1.2, 1}; the rounding step, its mode and its position are identical in all tiers.
  - largest advance `adjusted_room`: `room * 1.10` / `room * 1.05` / `room`, then the same `int(·/increment)*increment` — one formula `room × m`, m ∈ {1.10, 1.05, 1}.
  - card share `timed_share`: `share_points * 1.2` / `share_points * 1.1` / `share_points` — one formula `share_points × m`, m ∈ {1.2, 1.1, 1}.
  By contrast `first_period_treatment` changes the rounding mode (floor vs half-up) and is an honest method.
- Demonstrated consequence: counting only honestly labelled factors, `advance_ext_payroll_delay_relief`, `advance_ext_largest_advance` and `advance_ext_card_repayment_share` each have 0 `method` factors against the bound of ≥1 per computation. Every task of this difficulty has at least one of these computations (see the task files for which).
- Affected: `factors[].effect` of the three factors named; the policies' `rule` sentences stating the tiers are unchanged in substance.

**Observations (no demonstrated consequence on a scored value; not grounds for rework on their own):**
- F-OBS-1: `advance_disbursement` (subject of `advance_ext_largest_advance`, booked by `request_advance_00c9f515`) is outside the blueprint claim's event-type list of this difficulty; no other difficulty claims it.
- F-OBS-2: after the relief overwrite, base `advance_waivers` S3 (courtesy late-fee waiver at the customer's request, `late_fee_courtesy_waivers_per_year`, `advance_msr_courtesy_waivers_year`) has no surviving sentence; the relief's "does not count toward late_fee_courtesy_waivers_per_year" refers to a count nothing else now increments.
- F-OBS-3: the late-fee rule states no condition that the advance is still not fully repaid when a late-fee period closes (ext S1/S2; the superseded base S2 had none either, only S1 of the base frames lateness as "still not fully repaid"). Read literally, periods keep "closing" on a most recent advance repaid long ago and `late_fee_min` lifts a zero-principal fee to the minimum. The task files note whether their worlds expose this.
- F-OBS-4: `clean_share` compute uses `late_fees_12m <= 1`, equivalent to the rule only while the relieved fee is inside the 12-month window.
- F-OBS-5: relief rule "booked once that advance is repaid in full" is a state wait that a repayment write can satisfy, with no declared edge; inherited from base eligibility and not exercised in any tree here.
- F-OBS-6: the replaced_by of the relief's second overwrite no longer states the cancellation-window waiver itself.
- F-OBS-7: the card-share replaced_by covers only past-due card repayments; other manual repayments lose their stated bounds after the merge.
- F-OBS-8: tier-coincident ladders on specific tiers: `plan_bonus` is 0/0/0 on Pocketwire Advance Starter (`plan_limit_bonus 0.00`); `steady_payroll_rate` tier 2 (0.75) equals its fall-through on Pocketwire Advance Elite (`late_fee_pct_weekly 0.75`). Neither task's line is on those tiers.
- F-OBS-9: the prerequisite sentence of edge 1 says "every late fee on the line that qualifies", while the relief rule "acts on the late fee most recently booked on the line"; with two qualifying fees the older one could not be relieved by the rule as written. Not exercised when a line carries a single qualifying fee.

## closing_checklist

Written after both reveals (2026-09-25T00:24Z). The difficulty is **not closable this round**: not every task passes all four relationships.

- Per-task files `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` sits alongside; first round, no older revision. Comparison sections: task 0 carries SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1 carries SOURCE-FACTOR RED. ✗
- Coverage and scopes: task 0 = {payroll_delay_relief, largest_advance}, task 1 = {late_fee_assessment, card_repayment_share}; disjoint and together cover all four extended policies; each tree's tools closed; uuid8s independent. ✓
- Trees: each has 1 prerequisite problem, 1 value_input edge, 1 `owner=user` write, no cycle; difficulty-wide graph acyclic. ✓
- Factors: baselines self-sufficient and honest; every factor bears weight on its task's world; baseline-alone numbers differ from gold (0.30/1.80, 200/305, 2.06/0.62, 61.99/148.77). But three of four computations have no honestly labelled `method` factor (F-FAC-1). ✗
- Policy self-consistency: undeclared override F-POL-1 gives task 0's scored amount a second defensible value. ✗
- Gate re-run on the final form: not performed by the auditor (gates were supplied by the coordinator per the entry conditions; the artifacts are unchanged since snapshot `d5_r1`).

## revision_2

### charter_global_frozen (r2)

- Inputs: `advance.extended.yaml` sha256 `7dfe1bf5bfcfc5be106f2b1e19723904c9292107bf760e8d7b89dad3c710dc49` (**changed** from r1 `a170e21b…`), `task_tools.py` sha256 `d4d526e4…ce30` (unchanged); masked views r2 `0.view.json` `80f29a7b…` and `1.view.json` `1d2186b7…` (identical to r1). Gate snapshot `coord/snap/d5_r2.txt`: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK (traceability deferred). Entry conditions met.
- Freeze time 2026-09-25T00:3xZ, before the r2 task JSONs were opened. Because the charter hash moved, every charter-global section is **re-derived in full** below; the tool module is unchanged, so §action_binding_and_uuids is carried forward by reference on the unchanged hash `d4d526e4…`.
- Base section: lines 1–911 still verbatim with `blueprint/products/advance.yaml` (diff = trailing newline only).
- contamination_disclosure: this auditor revealed the r1 GT of both tasks at the end of round 1 (recorded in the r1 comparison sections). Nothing in this r2 charter-global section depends on it; no r2 task JSON was read before this section and the per-task r2 derivations were frozen.

### changes found (r1 → r2 charter)

1. `advance_ext_payroll_delay_relief`: rule gains S3 ("The flat advance fee and any express fee … are still waived with waiver_reason cancellation_window when … repaid in full within the cancellation window") and S4 ("Apart from the payroll-delay relief, a late fee can still be waived with waiver_reason courtesy at the customer's request at most late_fee_courtesy_waivers_per_year times …"); lateness_record re-worded to "at most one late fee … / two or more late fees" (rule, compute_basis, ladder); `card_multiplier` tier 2 changed from ×`card_multiplier_mid` to "card_purchase_credit (0.02) is added … for each card purchase in that window" (rule, compute, ladder; param `card_multiplier_mid` removed, `card_purchase_credit` added).
2. `advance_ext_largest_advance`: two new `overwrite` entries — `advance_agg_outstanding` "and their remaining principal plus the new advance may not exceed the effective limit." → "The largest advance worked out here takes the place of the effective limit as the ceiling on a new advance: a new advance may not exceed it, and the remaining principal of the line's advances is already taken off in it."; `advance_disbursement_rules` "The amount is at least min_advance_amount and a whole multiple of advance_increment, within advance_agg_outstanding." → "The amount of a new advance is at least min_advance_amount, a whole multiple of advance_increment and within the largest advance worked out here, and the count of advances not yet fully repaid plus the new one still may not exceed max_outstanding_advances."; both replaced_by texts added to the rule (S6, S7). `card_uplift` tier 2 changed from ×`card_uplift_mid` to "card_purchase_room (1.00) is added to the room for each card purchase in that window"; S-order sentence now says "card treatment".
3. `advance_ext_late_fee_assessment`: S1 now "…after its grace period while that advance still has unpaid principal, …; once no unpaid principal remains, a closing period carries no late fee." (also in baseline.rule and compute_basis); compute `result` gains `if unpaid_principal > 0 else 0`.
4. `advance_ext_card_repayment_share`: rule gains S2 ("Any other manual repayment, from the personal balance or on a line that is not past due, is at least min_manual_repayment or the whole amount outstanding on that advance, and never more than that amount."); `arrears_timing` tier 1 changed from ×`early_multiplier` to "early_points_per_day (2) points are added to the share for each day by which they fall short of early_days" (rule, compute, ladder; param `early_multiplier` removed, `early_points_per_day` added).

### policy_conflict_scan (r2)

Re-run over the whole structured policy. Overlapping subjects as in r1; the disbursement cap is now declared (below). The relief and the customer-requested courtesy waiver both book `waiver_reason courtesy` and both are now stated; the relief says it "does not count toward late_fee_courtesy_waivers_per_year", and the largest advance's holdback nets all courtesy waivers — consistent. Card-share S2 now covers the non-past-due and personal-balance repayments that the superseded base S2 used to. Late fees now stop when the advance has no unpaid principal. Time anchors, terminal fields and cross-category reads unchanged and declared. Task-scope partition unchanged: two components {relief → largest advance}, {late fee → card share}. No new conflict.

### rule_compute_equivalence (r2)

- relief: `clean_share` compute `late_fees_12m <= 1` now equals the rule "at most one late fee in the twelve months" ✓ (F-OBS-4 closed). `rounded_relief` tier 2 `RND(unrounded_relief + card_purchases_3m * K('card_purchase_credit'), 2)` ↔ rule "card_purchase_credit is added to the late fee times the relief share for each card purchase in that window before the relief is rounded" ✓. New S3/S4 are waiver-eligibility statements with no compute (the relief compute is not theirs) — no empty promise for this policy's `amount`.
- largest advance: `adjusted_room` tier 2 `room + card_purchases_3m * K('card_purchase_room')` ↔ rule S13 ✓; order sentence "card treatment then acts on that room" ✓. S6/S7 are ceiling/eligibility statements realised by `result` being the ceiling ✓.
- late fee: `result … if unpaid_principal > 0 else 0` ↔ S1 "once no unpaid principal remains, a closing period carries no late fee" ✓.
- card share: `timed_share` tier 1 `share_points + (K('early_days') - days_past_due) * K('early_points_per_day')` ↔ S12 ✓. S2 (other manual repayments) is not this policy's computed amount and has no binding — it is a bound, stated in words equal to the superseded base sentence. ✓
- All other bindings unchanged from r1 and still equivalent. Result: holds.

### action_binding_and_uuids (r2)

Carried forward from r1 by reference: `task_tools.py` hash unchanged (`d4d526e4…ce30`), `(target_tool, computes)` pairs unchanged in the charter. ✓

### prerequisite_graph (r2)

Both `prerequisite` blocks are byte-identical to r1 (edge largest ← relief, edge card share ← late fee; state form; gates `kept_late_fees`, `amount_owed` still exist in compute; `policy_source` still verbatim in rule S2 / S3 of the blocked rule). Acyclic ✓. Holds.

### prerequisite_sentences (r2)

Four-point test and single-write derivation as in r1, re-checked against the new rules: the late-fee rule's added "while that advance still has unpaid principal" does not touch edge 2's sentence and does not restate it; the card-share rule's new S2 contains no ordering connective about another problem; the largest-advance rule's new S6/S7 state a ceiling, not an order. Still only one write books a courtesy waiver on a qualifying fee (`grant_payroll_delay_relief_50112cf3` — the customer-requested courtesy waiver of relief S4 has no tool in this difficulty and requires a customer request, so it is not a second write that brings edge 1's state about in any task where the customer asks for none). Holds. F-OBS-5 unchanged.

### override_declarations (r2)

- relief ← `advance_waivers`: S1 and S3 still superseded and declared; their substance is now re-stated in the rule (S3, S4), so no base provision is dropped (F-OBS-2, F-OBS-6 closed). S2, S4, S5 followed.
- largest advance ← `advance_agg_outstanding`: S2 declared (r1); S1 clause (b) now **declared** (superseded_clause is a verbatim substring of base S1); clause (a) re-stated in the disbursement replaced_by. `advance_disbursement_rules` S3 now **declared**. Merged reading: the largest advance worked out by the extension is the single ceiling; no inherited sentence caps a new advance lower. **F-POL-1 closed.** `advance_fees`: followed.
- late fee ← `advance_late_fees`: S2 declared; S1, S3 followed; the new unpaid-principal condition is inside the extension's own rule and does not contradict base S1 ("An advance still not fully repaid …") — it agrees with it (F-OBS-3 closed).
- card share ← `advance_repayment_rules`: S2 declared; its non-past-due / personal-balance bounds now re-stated in rule S2 (F-OBS-7 closed). Others followed.
- No undeclared override remains.

### factor_ladders (r2)

Unchanged factors as in r1. Changed factors:
| policy / factor | tiers (r2) | label | audited |
| --- | --- | --- | --- |
| relief / card_multiplier | premium: RND(x × 1.4) / Classic-Gold: RND(x + n × 0.02) (n = purchases in window) / otherwise RND(x) | method | **method ✓** — tier 2 is an additive per-purchase term, a different functional form from tier 1's multiplication and from tier 3 |
| largest / card_uplift | premium: room × 1.10 / Classic-Gold: room + n × 1.00 / otherwise room | method | **method ✓** — same reasoning |
| card share / arrears_timing | ≤14 d: share + (14 − d) × 2 / 15–30 d: share × 1.1 / >30 d: share | method | **method ✓** — tier 1 is a per-day additive schedule, tier 2 a multiplication |
| relief / lateness_record | ≤1 late fee AND ≥3 advances / ≤1 AND <3 / ≥2 late fees | parameter | parameter ✓ (0.05 / 0.02 / 0) |

- Each changed tier is a sentence of the rule and a branch of its `decides` binding ✓; fall-throughs = baselines ✓; tiers pairwise disjoint and distinct in method ✓.
- Counts: relief 6 (5 parameter, 1 method) ✓; largest advance 6 (5, 1) ✓; late fee 4 (3, 1) ✓; card share 5 (4, 1) ✓. Multi-source and cross-difficulty per tree unchanged ✓. **F-FAC-1 closed.**
- Realism of the new tiers: a per-card-purchase credit and a per-day schedule for fresh arrears are both treatments a payments app could publish. Two shape observations, neither a RED on its own:
  - F-OBS-10: `arrears_timing` is non-monotone at its boundary — at 14 days past due tier 1 adds 0 points (share as it stands, the fall-through's outcome), while at 15 days tier 2 multiplies by 1.1; a customer one day later in arrears may repay more by card. The value coincides with the fall-through only at d = 14, so the tiers remain distinct methods.
  - F-OBS-11: across card tiers of the relief, tier 2's additive credit (≥ 10 × 0.02 = 0.20) beats tier 1's ×1.4 whenever late fee × share < 0.50, so the Gold/Classic card can earn more relief than a premium card on small fees.

### findings (r2)

- F-POL-1: **closed** (declared overrides; merged ceiling unique).
- F-FAC-1: **closed** (all three factors now change the functional form).
- F-OBS-2, F-OBS-3, F-OBS-4, F-OBS-6, F-OBS-7: closed as described. F-OBS-1, F-OBS-5, F-OBS-8, F-OBS-9: unchanged (observations).
- New: F-OBS-10, F-OBS-11 (observations). No new RED at charter level.

### closing_checklist (r2)

Written after the r2 reveals (2026-09-25T00:34Z).
- `0.md`, `1.md` one-to-one with tasks 0, 1; `_difficulty.md` alongside; r1 text preserved, r2 appended under `## revision_2`; both r2 comparison sections carry PASS. ✓
- Extended policies fully covered; scopes {relief, largest advance} and {late fee, card share} pairwise disjoint; task tools and GT closed; uuid8s independent (tool module unchanged). ✓
- Each tree: 1 prerequisite problem, 1 value_input edge, 1 `owner=user` write, acyclic; difficulty graph acyclic. ✓
- Every computation: self-sufficient baseline; 4–6 factors with ≥2 `parameter` and 1 honest `method`; ≥1 multi-source and ≥1 cross-difficulty per task; ladders of 3 distinct tiers stated in the rule; every factor bears weight; baseline-alone ≠ gold (0.30/1.76, 200/305, 2.06/0.62, 61.99/144.63). ✓
- Instantiation gates on the final form: coordinator snapshot `coord/snap/d5_r2.txt` all OK on the r2 artifacts (traceability deferred to the KB step); not re-run by the auditor.
- Open observations (not blocking): F-OBS-1, F-OBS-5, F-OBS-8, F-OBS-9, F-OBS-10, F-OBS-11.

Difficulty `paycheck_advance_servicing` passes the source-layer audit in revision 2.

## revision_3

### charter_global_frozen (r3)

- Inputs: `advance.extended.yaml` sha256 `38459324dba90596b277112ed1c82c3ff06d11d227c9e92fae62ca145746ab69` (changed from r2 `7dfe1bf5…`); `task_tools.py` `d4d526e4…ce30` (unchanged); r3 views `80f29a7b…` / `1d2186b7…` (unchanged). Gate snapshot `coord/snap/d5_r3.txt`: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK (traceability pending KB publication). Trigger for the round: `coord/snap/advance_render_r1.txt` — `check_docs.py` FAIL "payroll_delay_relief_bd13e672.json: hub repeats hidden factor name 'payroll_delay'".
- Time 2026-09-25T01:1xZ (UTC).

### scope of the charter change (r3)

- `collection_lag` occurs exactly once in the charter (line 1023, `- id: collection_lag`, the first factor of `advance_ext_payroll_delay_relief`).
- Reverse-substitution proof: replacing that single line with `- id: payroll_delay` gives sha256 `7dfe1bf5bfcfc5be106f2b1e19723904c9292107bf760e8d7b89dad3c710dc49`, which is exactly the r2 charter hash. **The factor-id rename is the only change**; effect, decides (`delay_share`), bindings (`advance_due_date, collection_date, payroll_delay_days, delay_share`), ladder, baseline, rule, compute and params are byte-identical to r2.
- Consequence for the charter-global sections: every r2 conclusion (§policy_conflict_scan, §rule_compute_equivalence, §action_binding_and_uuids, §prerequisite_graph, §prerequisite_sentences, §override_declarations, §factor_ladders, §findings under `## revision_2`) rests on content that is byte-identical modulo that id, so each is re-confirmed unchanged; in §factor_ladders the relief's first row now reads `collection_lag` (parameter, 3 tiers 0.20/0.10/0, baseline 0). No r2 RED to close (r2 closed with none); nothing regressed.
- Id hygiene (the render-gate concern, checked here only as a charter fact): no factor id of the charter is now a substring of any `target_tool` name (`grant_payroll_delay_relief_50112cf3`, `request_advance_00c9f515`, `assess_late_fee_a649c20a`, `repay_advance_by_card_db2e846d`) or of any extended policy id. The compute binding `payroll_delay_days` still contains the string `payroll_delay`; it is a binding name, not a factor id — observation F-OBS-12, for the KB audit to weigh, no policy-task consequence.

### task-file changes (r3)

- `tasks/0.json` sha256 `661afba2…` (r2 `3ca12826…`): factor-id references updated — `collection_lag` in `computations[relief].factor_sensitivity[0].factor`, its `factor_trace` entry, the step-9 `argument_uniqueness_tracing.amount` text and the relief breakdown text, plus a "ROUND 3 REVISION (KB render gate)" note; no remaining factor-id use of `payroll_delay`. Scored values, sensitivities, baseline results, prerequisite_closure, charter_scope and required_documents equal the r2 values recorded in `0.md` §revision_2 (1.76; 305 / 2026-10-22 / 9.0; 0.3 / 1.16, 1.61×4, 1.5; 200 / 255, 280, 275, 295, 325, 295; skip 285).
- `tasks/1.json` sha256 `e8855344…` (r2 `76d761dc…`): **hash moved although the brief names no change to it.** Both files have the same mtime (01:06:17) and each is exactly `json.dumps(indent=4, ensure_ascii=False) + "\n"` of its content, i.e. both were re-serialised by one script. The auditor kept no r2 byte copy, so a byte diff is not possible; semantically, `frozen_time`/`user_scenario`/`initial_state` equal the r3 view, and evaluation_criteria writes (0.62 period 1; 144.63), computations (0.62 / 2.06 / 1.25, 0.69, 0.69, 0.83; 144.63 / 61.99 / 123.97, 134.30, 134.30, 123.97, 123.97), prerequisite_closure (order, edge, skip 144.20 / 61.80), charter_scope and required_documents equal the r2 values in `1.md` §revision_2; its dossier ends with the r2 note (no r3 note). Observation F-OBS-13 (re-serialisation, no semantic change found).

### closing_checklist (r3)

All r2 closing items stand (checked against the r3 artifacts as above); gates re-run by the coordinator on the final form (`d5_r3.txt`, all OK). Open observations: F-OBS-1, 5, 8, 9, 10, 11, 12, 13. Difficulty `paycheck_advance_servicing` passes the source-layer audit in revision 3.
