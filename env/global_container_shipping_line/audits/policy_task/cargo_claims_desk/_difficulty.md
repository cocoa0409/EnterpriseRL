# Policy-task audit — cargo_claims_desk / charter-global

## charter_global_frozen

- Auditor: Claude (Opus 5) policy-task audit subagent, independent of the agent that authored the charter, tools and tasks; no answer supplied on its behalf.
- Freeze time of this section: 2026-09-13T05:58Z (wall clock), written before any task's GT was revealed. Nothing in this section is derived from a revealed GT.
- Frozen inputs:
  - `env/global_container_shipping_line/tasks/cargo_claims_desk/claims.extended.yaml` sha256 `b5de5e88020d0db955c22f0e1f90d75ca9116c9ea82796300fcd11051ed3874a` (matches the coordinator's HASHES.txt)
  - `env/global_container_shipping_line/tasks/cargo_claims_desk/task_tools.py` sha256 `bec33e0697793ae91818ceb04047d3d8dfad5f17655978bf5e081f5162e3734f` (matches)
  - blueprint: `blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/claims.yaml`; `products/reefer.yaml` and `products/contract.yaml` read only for their variant ranks (reefer: Standard 1, Monitored 2, Cold Treatment 3, Controlled Atmosphere 4, Pharma GDP 5, Superfreezer 6; contract: Starter 1, Standard 2, Regional Account 3, Key Account 4, Global Account 5, Strategic Partner 6).
  - erlbench-side DSL semantics taken from `skills/erl-task-instantiate/scripts/check_compute.py` `build_env` (SUM/COUNT/LATEST auto-scoped to the holding's primary key; `within_months` = `0 <= MONTHS(event_date, NOW) < n`; `CFIELD/CPARAM` read cross-category holdings filtered by `customer_id = holding.customer_id` plus the given equalities; `LATEST` = max by string date, first row wins on ties).
- Fields permitted: the whole charter, tool module, schema, share tools. Fields masked for this section: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, db-closure fields. None were read.
- Contamination disclosure: none. The only listing that touched a sibling area was `ls env/global_container_shipping_line/audits/policy_task`, which printed sibling difficulty directory names only; no sibling file was opened.

### entry_conditions (Step 0)

- Gate snapshot supplied by the coordinator, all exit 0: `check_extended` EXTENDED OK; `check_task_tools` TASK TOOL CONTRACT OK; `replay_tasks` REPLAY OK; `check_solvability` SOLVABILITY OK; `check_compute` COMPUTE OK; `check_grounding` GROUNDING OK; `check_cross_fire` SCOPE OK. `check_traceability` deferred until the KB is published (recorded, not re-run here).
- Masked views supplied with hashes, re-verified by sha256sum: `0.masked.json` `c1f815b0…2144`, `1.masked.json` `d35b658c…77b8`; each keeps only `task_index, frozen_time, user_scenario, initial_state`.
- Base-copy check: `head -n 852 claims.extended.yaml | diff - blueprint/products/claims.yaml` differs only by the one blank separator line before `extended_policies:`; the base section is verbatim identical to the constitution.

### policy_conflict_scan

Overlapping subjects (extended id short names used below: E1 `claims_ext_settlement_invoice_share`, E2 `claims_ext_notice_container_value`, E3 `claims_ext_lodging_rejection_grounds`, E4 `claims_ext_bind_invoice_value`, E5 `claims_ext_premium_contract_rank`, E6 `claims_ext_premium_balance_remittance`, W `claims_wf_further_notice_on_open_cover`):

| Write subject | Base policies in force | Extended | Trigger | Conflicts found |
| --- | --- | --- | --- | --- |
| claims_settlement_approved | claims_coverage_and_exclusions, claims_settlement_calculation, claims_agg_annual_aggregate | E1 (amount_usd) | state_due | F-3 (aggregate per holder vs per cover, headline sentence undeclared); O-2, O-3, O-11 |
| claims_claim_lodged | claims_notice_and_time_bar | E2 (claimed_amount_usd) | on_request | F-2 ("never declines to register" vs claim cap / claimant entitlement / one-open-claim) |
| claims_claim_rejected | claims_notice_and_time_bar, claims_coverage_and_exclusions | E3 (rejection_reason) | state_due | F-6 (0-day apparent-damage branch) |
| claims_cover_bound | claims_cover_eligibility | E4 (insured_value_usd) | on_request | F-1 (prepayment order), F-4 (max_cover_value gate vs cap) |
| claims_premium_charged | claims_premium | E5 (amount_usd) | state_due | none of its own; party to F-1 through the bind-before-charge sentence |
| claims_premium_paid | claims_premium | E6 (amount_usd) | on_request | F-1 (bind-before-settle order), F-5 (recomputed balance vs premium_due_usd cap) |
| claims_claim_closed | claims_settlement_payment | none (W steps 1 and 4, computed_by []) | — | none |

- Time anchors: E3 counts from `cargo_covers.delivery_date` exactly as base `notice_window`/`time_bar`; E4 re-affirms base `bind_before_departure` (etd_date minus tier days, inclusive); E1 replaces base's "trailing 365 calendar days ending on the approval date" with "fewer than 12 whole calendar months before the approval date" (declared, overwrite #2).
- Terminal states: E1/E3 leave cover status unchanged (tool contracts), closure is W's `close_cargo_claim_a3572c28` per base claims_settlement_payment "A decided claim closes the open claim on the cover, whether it was settled or rejected." E4 moves quoted→active; E5/E6 move `premium_due_usd` up/down. No terminal-state conflict between policies.
- Cross-category read boundaries: E1 bol{declared_cargo_value_usd, package_count}; E2 bol{declared_cargo_value_usd}, booking{container_count}; E3 reefer{variant_name}; E4 bol{declared_cargo_value_usd}, booking{container_count}; E5/E6 contract{variant_name, status}. All reads are declared in `cross_category`; the compute scopes them to the cover holder's customer_id (O-1).
- Scope partition derivable from the charter alone (to be confirmed against `charter_scope` at closing): the `prerequisite` graph has two connected components, {E1, E2, E3, W} (tools approve/close/lodge/reject) and {E4, E5, E6} (tools bind/charge/pay). With M = 2 these are the only disjoint, jointly complete partition in which each task's tree is whole; exactly one component carries W.

### rule_compute_equivalence

Mechanical check (private script, not left in the write domain): every `compute_basis` quotation (split on ` ... `) is a verbatim substring of its policy's `rule`; every `prerequisite.policy_source` is verbatim in the dependent policy's rule; every overwrite `superseded_clause` is verbatim in the named base rule and every `replaced_by` verbatim in the extended rule. Result: all pass. Binding without its own `compute_basis` entry: `cargo` in E5 and E6 (a bare `F('cargo_type')` read; covered by the `uplift_pct` quotation) — O-6.

Forward (rule → compute) and reverse (compute → rule) sweep, per policy:

- **E1** — proven loss = `MN(claimed, invoice_share)` ("never more than the commercial invoice value of the affected packages"); invoice share rounded to the cent, fallback to claimed when the BL has no declared value (verbatim); Hague-Visby limit `RND(MX(pkg*affected, kg*affected_weight)*rate, 2)` (verbatim, "that higher figure converted ... rounded to the cent"); declared-value share rounded (verbatim); cargocare: uplift unrounded, single deductible `MX(general, kind)` with kind = wet/temperature/none (verbatim), `MN(cap, MX(0, …))` ("the remainder, never below 0.00, is then capped"); aggregate `MX(0, limit − approved_12m)` on the cover within 12 whole months (verbatim; `within_months=12` implements "fewer than 12 whole calendar months before the approval date" since NOW is the approval date); only the final figure rounded (verbatim). Reverse sweep: no binding invents a basis. Gaps: the rule's `liability_basis` recording clause has no compute (it is not in `computes`; O-7); the rule excludes delay loss but compute has no delay branch (O-3); `claimed`/`affected_*` are SUMs over documents_complete files where the rule speaks of one file (O-4).
- **E2** — container value `RND(doc_value / booking_containers, 2)`, fallback `RND(insured / cover containers, 2)`, cap at `cover_cap_per_container_usd` when above 0.00 and exceeded — all verbatim. Compute also falls back when the booking container count is unreadable, which the rule does not name (O-14). Rule's "entered exactly as the claimant states them" (container, kind, apparent, packages, weight) is persona input, not compute.
- **E3** — ordered grounds below_minimum → not_covered_by_tier → claim_time_barred → notice_out_of_time → `'not_applicable'` (= not rejected under this policy), all verbatim; reefer rank map equals the reefer charter ranks; "no reefer service counts as tier rank 0" implemented by the final `else 0`; time bar via `MONTHS` with the end-of-month rule: verified by hand on 2025-01-15/2026-01-20 (barred), 2024-01-31→2024-02-29 (in time), 2024-03-01 (barred); window `DAYS(delivery, notice) <= window_days` inclusive (verbatim).
- **E4** — `RND(doc_value * cover_containers / booking_containers, 2)`, fallback to quote value, cap at `max_cover_value_usd` — verbatim.
- **E5** — base premium, then uplift, then discount, each on the prior result, "never combined into one rate"; discount only when `premium_discount_min_contract_rank > 0` and contract rank ≥ it; contract = holder's active contract on any lane; minimum `MX(min_per_container × cover containers, min_per_cover)`; only the final figure rounded — verbatim. `CFIELD('contract', …, status='active')` takes the first active contract; the rule is silent when a holder has several active contracts of different tiers (O-5).
- **E6** — `product_premium` restates E5 in one expression (verbatim "built up exactly as the premium charge is built up"), less remittances and refunds on the cover, `MX(0, …)` rounded — verbatim.

### action_binding_and_uuids

| Policy | target_tool | computes | Tool owner | Claimed by another policy? |
| --- | --- | --- | --- | --- |
| E1 | approve_claim_settlement_060ed8c3 | amount_usd | agent | no |
| E2 | lodge_cargo_claim_268664bf | claimed_amount_usd | user | no |
| E3 | reject_cargo_claim_5f9631bd | rejection_reason | agent | no |
| E4 | bind_cargo_cover_f980fecc | insured_value_usd | agent | no |
| E5 | charge_cover_premium_8ce00127 | amount_usd | agent | no |
| E6 | pay_cover_premium_9f1f968f | amount_usd | user | no |
| (W only) | close_cargo_claim_a3572c28 | — | agent | — |

- Each `(target_tool, computes)` is claimed once. uuid8s `060ed8c3, a3572c28, 268664bf, 5f9631bd, f980fecc, 8ce00127, 9f1f968f`: seven distinct first characters, no shared prefix of length ≥ 2, no sequence or adjacent-value pattern, none reused across tools; consistent with independent generation.
- Docstrings vs policies: bind "records the insured value the cover is bound for, replacing the value carried on the quote" = E4; approve "marks the claim file as approved … the cover's status is left unchanged" and reject "The cover's status is left unchanged" = W's need for explicit closes; lodge "the notice is dated today … The cover's status becomes claim_open" = base lifecycle. No tool adds a confirmation, review or wait. The approve enum gloss "proven_loss (no cap bound and the approved amount is the loss measure itself)" is looser than E1's "proven_loss otherwise, including when the invoice value of the affected packages limited the proven loss" under an uplift (O-7).
- Function bodies: none of the seven tools reads a status, window, cap, gate or prior row to refuse or warn; approve/charge/pay read only the prior balance to add/subtract; lodge/reject/bind/close write unconditionally. The tool layer judges no prerequisite.

### prerequisite_graph

| Dependent | problem | kind | gate | policy_source verbatim in dependent rule | condition vs sentence | resolved_by makes effect hold |
| --- | --- | --- | --- | --- | --- | --- |
| E2 | E1 | state_gate | claims_notice_and_time_bar.claim_cap (real gate) | yes | faithful | partly: approve decides the file but leaves cover status claim_open; the lodging transition needs claim_closed, supplied by the W close (O-9) |
| E3 | E2 | value_input | notice_amount (binding exists) | yes | faithful | yes (lodge creates the notice_registered file) |
| E5 | E4 | value_input | insured (binding exists) | yes | slightly narrowed: "fixed at binding from the transport document" (E4 keeps the quote value when the BL carries none) (O-10) | yes |
| E6 | E5 | state_gate | `cargo_covers.premium_due_usd` — a field, not an eligibility-gate id; the operative gate is `claims_premium.remittance_once` "may not exceed premium_due_usd" (O-8) | yes | faithful | yes |
| E6 | E4 | value_input | bound_insured (binding exists) | yes | faithful | yes |

- `prerequisite` filled on all six policies and W (`[]` on E1, E4, W). Every `problem` is an extended id in this file, none a base id, none self. The graph is acyclic (E1→∅, E2→E1, E3→E2, E4→∅, E5→E4, E6→{E5,E4}). No authoring-viewpoint phrasing ("opening", "this task", "current world", "in this world", "at the start": zero hits in the extended section).

### override_declarations

Sentence-by-sentence conclusion against each `base_policy_refs` entry (F = conflict finding, followed = extended follows or merely makes precise, inherited = not restated and stays in force).

**E1 vs claims_settlement_calculation** — C1 "follows the product's liability_basis": followed. C2 "Under hague_visby_limitation the line pays the proven loss, the claimed_amount_usd once documents are complete": **declared** (overwrite #1); rest of C2 (limit, conversion, rounding, package/weight/proven_loss recording): followed. C3 declared_value share: followed (E1 adds rounding to the cent; the term "proven loss" now carries overwrite #1). C4 cargocare uplift / one deductible / per-container cap / cover_limit: followed per the rule text; base's own `formula.cargocare_settlement` deducts `max(deductible_per_claim_usd, wet_damage_deductible_usd, temperature_damage_deductible_usd)` regardless of the kind of loss — a base-internal rule/formula split (O-2). C5 delay loss: outside E1, inherited. C6 "The annual aggregate then applies under claims_agg_annual_aggregate": followed (points at the overwritten aggregate). C7 never negative: followed. C8 desk authority: inherited gate (per-task check). C9 premium_paid_before_settlement: inherited (affects payment only).

**E1 vs claims_agg_annual_aggregate** — A1 "CargoCare products carry an annual aggregate per cover holder.": handled differently (E1: "the aggregate still available on the cover") and **not named** in `overwrite` → F-3. A2 per-holder 365-day sum: **declared** (overwrite #2, names `claims_msr_settled_365d`). A3 reduce to remaining / approve at 0.00 with aggregate_limit: followed. A4 no aggregate for Standard/Declared: followed (limit 0.00 → "not reduced"). The base `formula.remaining_aggregate` and the measure `claims_msr_settled_365d` (per holder, 365 days) remain in the charter unchanged.

**E1 vs claims_coverage_and_exclusions** — covered types, reefer rank, logged excursion, delay rolls, misdeclaration, excluded peril, "Settlement may be approved only while the claim's cover is claim_open and the claim's documents are complete", "Each claim is decided once": all inherited as gates; E1's "the cover's claim file in the documents_complete state" follows the last-but-one.

**E2 vs claims_notice_and_time_bar** (`overwrite: []`) — N1 lodged by the claimant by written notice naming container and loss: followed ("lodged by the claimant in person"). N2 claimants_allowed / exact consignee match: conflicts with "the desk never declines to register a notice" → F-2. N3 "A cover takes at most max_claims_per_cover claims … and only one claim is open at a time": cap part conflicts with "never declines" → F-2; one-open part followed and sequenced ("a claim still open on the cover whose documents are complete is decided by the desk before the further notice is lodged"). N8 below-minimum: followed, but the amount tested is now E2's container value, not the claimant's loss figure (O-11). All window, time-bar, documents and withdrawal sentences: untouched by E2.

**E3 vs claims_notice_and_time_bar** (`overwrite: []`) — N4/N5 non-apparent window, inclusive last day: followed. N6 "Loss apparent at delivery must be noted on the delivery receipt when apparent_damage_notice_days is 0, and otherwise notified within that many calendar days of delivery; notice of delay loss …": the delay and non-zero apparent branches followed; the 0-day branch turned into a dated window whose last day is delivery_date → F-6. N7 time bar: followed. N8 below minimum: followed. N12 out-of-time reasons: followed. N14 "A rejection may be booked only while the claim's cover is claim_open": followed. Documents-deadline, withdrawal, decided-once: inherited. Ordering of grounds: added by E3; base states no order, so no conflict.

**E3 vs claims_coverage_and_exclusions** — covered types → not_covered_by_tier and reefer-rank sentence: followed; "a container with no reefer service counts as tier rank 0": added precision, no base sentence contradicted. Logged excursion, misdeclared, excluded peril: inherited and examined after E3's grounds.

**E4 vs claims_cover_eligibility** (`overwrite: []`) — statutory attach, cargo owner's option, eligible cargo types, min insured value, container_count/partial, forwarder, drafted transport document, binding deadline, credit_hold: inherited (E4: "Every binding gate of claims_cover_eligibility still applies"). "the insured value must be … at most max_cover_value_usd": handled differently ("A value above the product's max_cover_value_usd is bound at max_cover_value_usd") → F-4. Prepayment sentence: re-affirmed by E4 but contradicted by E6's order → F-1.

**E5 vs claims_premium** (`overwrite: []`) — rate, uplift, discount ("that rank is not 0" read as the minimum rank; equivalent in every variant because every contract rank is ≥ 1 and every variant with minimum rank 0 has discount 0), minimum and rounding: followed. "charged once at binding": followed as a separate charge step immediately after binding (base event `claims_cover_bound` triggers `claims_premium_charged`; the tool split keeps the charge a distinct agent write — O-13). "A premium may be booked only on a cover whose status is active", "charged premium once", due days: inherited.

**E6 vs claims_premium** (`overwrite: []`) — "A premium remittance is written with the reference exactly as quoted … and a reference is recorded once per cover": followed. "may not exceed premium_due_usd": E6 fixes the amount by recomputing the product premium, not from `premium_due_usd` → F-5. E6's "a quoted cover is bound before its premium is settled" vs claims_cover_eligibility's prepayment sentence → F-1.

### findings

**F-1 — SOURCE-POLICY RED (charter-global; bears on task 1, which claims E4/E5/E6).** Symptom: two passages fix opposite orders of binding and premium payment for the same cover. Evidence: base claims_cover_eligibility "When the cover holder's credit_status is cash_in_advance and the product's premium_prepayment_required is true, the premium must be received before binding.", re-affirmed by E4 "Every binding gate of claims_cover_eligibility still applies, including … the premium prepayment of a cash_in_advance holder."; versus E6 "A remittance is taken only against premium already charged to the cover, so a bound cover whose premium has not yet been charged has it charged before the holder pays. The balance is worked out on the insured value fixed at binding, so a quoted cover is bound before its premium is settled." together with base claims_premium "A premium may be booked only on a cover whose status is active." Demonstrated conflict: a cash_in_advance holder of a quoted AHL CargoCare Plus cover (premium_prepayment_required true) asks to put it in force and pay — base/E4: pay, then bind; E6/E5/base premium_on_active: bind, then charge, then pay. No order satisfies both, so the charter has no solution in that situation (base alone already implies the loop, since a remittance "may not exceed premium_due_usd", which is 0.00 until an active cover is charged). Root cause: E6 orders bind-before-settle without naming the base prepayment sentence in `overwrite`, while E4 re-affirms it. Affected: `claims.extended.yaml` E4 rule, E6 rule, base claims_cover_eligibility.prepaid_premium. Consequence per task: see task 1 file.

**F-2 — SOURCE-POLICY RED (charter-global; bears on task 0, which claims E2).** Symptom: E2 says every notice is registered; base says some notices cannot be lodged. Evidence: E2 "the desk registers every notice the claimant wishes to lodge, including one that will be rejected as soon as it is registered; the desk never declines to register a notice." versus base claims_notice_and_time_bar "A cover takes at most max_claims_per_cover claims, counted by claims_msr_claims_on_cover, and only one claim is open at a time." and "The claimant must be one the product's claimants_allowed admits …" (both eligibility items apply_to claims_claim_lodged). Demonstrated conflict: an AHL CargoCare Essential cover (max_claims_per_cover 2) with two non-withdrawn decided claims, holder asks to lodge a third — base: the cover takes no further claim; E2: register it, and E3 has no ground to reject it, so it stays open as a third claim. Same for a printed consignee under Essential (claimants_allowed [cover_holder]). Inside E2 itself, "never declines to register" also collides with "A further notice can be lodged on a cover only when no claim is open on it" when the open claim is still notice_registered (E1 decides only documents_complete files, so nothing at the desk removes it). Root cause: absolute registration sentence with `overwrite: []`. Affected: E2 rule. Consequence per task: see task 0 file.

**F-3 — SOURCE-POLICY RED (charter-global; bears on task 0, which claims E1).** Symptom: aggregate scope per cover holder (base) vs per cover (E1). Evidence: base A1 "CargoCare products carry an annual aggregate per cover holder." (not named in E1 `overwrite`), base measure `claims_msr_settled_365d` "across every cover of the same product held by the cover holder", base `formula.remaining_aggregate`; versus E1 "the settlement is then reduced to the aggregate still available on the cover, which is annual_aggregate_limit_usd less the amounts of the settlement approvals already booked on the same cover". Demonstrated conflict: holder with two AHL CargoCare Plus covers (limit 300,000.00), 295,000.00 approved on cover A in the last 12 months, new claim on cover B computing 20,000.00 — A1 + measure: remaining 5,000.00 → approve 5,000.00 aggregate_limit; E1: nothing approved on B → approve 20,000.00 proven_loss. Root cause: overwrite #2 names the operative sentence A2 but not the headline A1. Affected: E1 `overwrite`. Consequence per task: see task 0 file.

**F-4 — SOURCE-POLICY RED (charter-global; bears on task 1, which claims E4).** Symptom: a value above max_cover_value_usd is refused by base and capped by E4. Evidence: base claims_cover_eligibility "the insured value must be at least min_insured_value_usd and at most max_cover_value_usd"; E4 "the insured value it is bound for is the commercial invoice value of the goods the cover takes … A value above the product's max_cover_value_usd is bound at max_cover_value_usd … Every binding gate of claims_cover_eligibility still applies". Demonstrated conflict: AHL CargoCare Premium quote (max 2,500,000.00) for all containers of a booking whose BL declares 3,000,000.00 — base gate on the invoice value: the cover cannot be bound; E4: bind at 2,500,000.00. Root cause: cap replaces a refusal gate with `overwrite: []`, and E4's own gate re-affirmation keeps the refusal reading alive. Affected: E4 rule. Consequence per task: see task 1 file.

**F-5 — SOURCE-POLICY RED (charter-global; bears on task 1, which claims E6).** Symptom: the payment amount can exceed what base allows. Evidence: base claims_premium "A premium remittance … may not exceed premium_due_usd"; E6 "the amount paid is the premium balance owed on the cover. That balance is the premium the cover's product yields on the insured value the cover was bound for, built up exactly as the premium charge is built up … less the amounts of every premium remittance already applied … and of every premium refund already booked". Demonstrated conflict: AHL CargoCare Premium, OOG, 4 containers, bound at 857,600.00 while the holder's Key Account contract is active → charged 2,004.64 (premium_due_usd 2,004.64); the contract expires before the holder pays within the 30 premium_due_days — E6 recomputes without the discount: 857,600 × 0.25 % × 1.10 = 2,358.40; base caps the remittance at 2,004.64. Root cause: E6 derives the balance from a fresh recomputation rather than from the charge on the ledger, with `overwrite: []`. Affected: E6 rule/compute `product_premium`. Consequence per task: see task 1 file.

**F-6 — SOURCE-POLICY RED (charter-global; bears on task 0, which claims E3).** Symptom: base's 0-day apparent-damage requirement is a delivery-receipt notation; E3 makes it a dated window. Evidence: base "Loss apparent at delivery must be noted on the delivery receipt when apparent_damage_notice_days is 0"; db_schema `damage_apparent_at_delivery` "whether the loss was apparent at delivery (noted on the delivery receipt)"; E3 "the window is … apparent_damage_notice_days calendar days for any other loss apparent at delivery …, its last day being the cover's delivery_date plus those days". Demonstrated conflict: AHL CargoCare Essential cover, delivery 2026-05-01, physical damage noted on the delivery receipt (flag true), written notice dated 2026-05-03 — base: the notation requirement is met, no notice_out_of_time; E3: last day 2026-05-01, notice later → notice_out_of_time. Root cause: undeclared reinterpretation of N6's 0-day branch (`overwrite: []`). Affected: E3 rule/compute `window_days`, `within_window`. Consequence per task: see task 0 file.

Observations (no consequence demonstrable in this difficulty's worlds; not grounds for rework on their own):

- O-1 Cross-category reads are scoped to the cover holder's `customer_id` by `CFIELD`; the rules say "the transport document of the cover's booking", "the booking's container_count", "the reefer service … on the cover's booking" with no party restriction. A world where the BL documentation party, booking party or reefer orderer differs from the cover holder would make compute fall back while the rule reads the row. Both task worlds seed these rows under the cover holder.
- O-2 Base-internal rule/formula splits in products/claims.yaml: `cargocare_settlement` takes the max of all three deductibles; `hague_visby_limit_usd` names `package_count`/`gross_weight_kg` where the rule says affected packages/weight; `claims_premium.formula` omits the discount step the rule states. E1/E5 follow the rule texts.
- O-3 E1's rule excludes delay loss; its compute has no delay branch.
- O-4 E1 `claimed`/`affected_*` are SUMs over documents_complete files; lifecycle keeps that to one file.
- O-5 E5/E6 read the first active contract; the rule is silent when several active contracts carry different tiers.
- O-6 `cargo` binding in E5/E6 has no own compute_basis entry.
- O-7 `liability_basis` on approval is fixed by E1's rule text only; the approve tool's enum gloss for proven_loss is looser than E1's.
- O-8 E6 → E5 edge: `kind: state_gate` with `gate: cargo_covers.premium_due_usd` (a field) instead of an eligibility id (`claims_premium.remittance_once`).
- O-9 E2 → E1 edge: `resolved_by: approve_claim_settlement_060ed8c3` alone leaves the cover claim_open; the effect relies on the W close step (no policy owns `close_cargo_claim_a3572c28`; base claims_settlement_payment "A decided claim closes the open claim on the cover" supports it).
- O-10 E5 → E4 edge condition "fixed at binding from the transport document" narrows E4 (which keeps the quote value when the BL has no declared value).
- O-11 db_schema `cargo_claims.claimed_amount_usd` "loss claimed and supported by the commercial invoice and survey; treated as the proven loss once documents are complete" is a schema gloss contradicted by E2 (notice amount = container value at risk) and E1 (proven loss capped by invoice share). Not a policy sentence, so `overwrite` cannot name it; the numbers it would produce are shown in task 0's file.
- O-12 W carries no `requires_external_wait` / `zero_wait_proof` in the charter; per `skills/erl-task-instantiate/references/task.json` these live in the workflow task's `solvability_contract.gold_actions[]` (masked) and are checked at task 0's reveal. W's `dataflow` omits the lodge → reject `claim_id` binding and the close → lodge status effect (per-task check in task 0).
- O-13 Base event `claims_cover_bound` triggers `claims_premium_charged`; the tool module splits them (bind "No premium is charged"), consistent with E5's order.
- O-14 E2 compute also falls back when the booking container count is unreadable; the rule names only the missing declared value.

## closing_checklist

Written after both reveals (2026-09-13T06:07Z). Everything above this heading was frozen before any reveal and is unchanged.

**The difficulty is not closed out.** Step 4 closes a difficulty only when every task PASSes all three relationships; here task 0 is SOURCE-CHAIN RED (F-T0-1 in `0.md`) and the charter carries six charter-global SOURCE-POLICY REDs (F-1 to F-6 above), none of which is engaged by either task's world. Checklist status as it stands:

- Audit files: `_difficulty.md`, `0.md`, `1.md` — one per task, first revision, each with `source_derivation_frozen` (hashed pre-reveal) and `source_gt_comparison`. Comparison verdicts: task 0 unique solution PASS / problem tree RED; task 1 unique solution PASS / problem tree PASS.
- Coverage and scope: `charter_scope` of task 0 = {E1, E2, E3} + W + approve/close/lodge/reject; of task 1 = {E4, E5, E6} + bind/charge/pay. All six extended policies covered, pairwise disjoint across the whole trees; exactly one workflow, claimed by task 0 only; each of the seven task tools used by exactly one task; uuid8s independent (see `### action_binding_and_uuids`). Matches the partition derived pre-reveal.
- Problem trees: task 0 declares 2 prerequisites with 1 value_input edge, but the value_input prerequisite is named by the customer (F-T0-1) — fails; task 1 has 2 prerequisites, 2 value_input edges, no cycle — holds. The difficulty-wide `prerequisite` graph is acyclic (two disconnected components, no cross-task edge).
- Workflow zero-wait: task 0's gold actions carry `requires_external_wait: false` and per-step `zero_wait_proof` — holds.
- Artifact stability during the audit: `claims.extended.yaml` `b5de5e88…3874a` and `task_tools.py` `bec33e06…3e734f` unchanged from masking time; task files at reveal `tasks/0.json` `cccb5695…cb9b`, `tasks/1.json` `0f59ca7d…637a`.
- Gate re-run on the final form: not performed — closing conditions are not met, and the brief's gate snapshot (all seven instantiation gates green, traceability deferred) is the recorded state. The gates are green while F-1…F-6 and F-T0-1 stand, which is expected: none of these defects is a structural or reference fault the scripts check.
- Provenance of the frozen charter-global section: written in three appends between 2026-09-13T05:58Z and 06:01Z (file mtime 06:01Z; sha256 `b7fd4e82…0757` recorded at 06:04:27Z), all before the first reveal at 06:04:36Z; the "Freeze time" stamp in its header marks the first append.

## revision_2

### charter_global_frozen (r2)

- Auditor: same subagent as round 1. Written 2026-09-13T06:2xZ, before either round-2 task reveal; nothing here is derived from a round-2 GT. Round-1 text above is untouched.
- Shared inputs changed, so every charter-global section is re-derived in full (not carried forward): `claims.extended.yaml` round 1 `b5de5e88…3874a` → round 2 `7e7453d43c92ae4bd9be43d0833fbe4afa0869a81acb4289c86a514bd08a9d7f`; `task_tools.py` round 1 `bec33e06…3e734f` → round 2 `31441b0ceeadeab481698f77d5bd89c43d59691ef011153ea1274437953b7d02` (both match the coordinator's `source_r2/HASHES.txt`). Blueprint files unchanged (mtimes 02:21–03:19 predate round 1); `head -n 852 claims.extended.yaml | diff - blueprint/products/claims.yaml` still differs only by the separator blank line — base copy verbatim.
- Entry conditions: coordinator's round-2 gate block all exit 0 (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE OK; traceability deferred). Masked views `source_r2/0.masked.json` `ff211d35…675d`, `source_r2/1.masked.json` `0ddad7a4…23f3` re-verified. Diff against round-1 masks: `frozen_time` and every `initial_state` row identical in both tasks; only `user_scenario` changed.
- Reworker's claims were not taken as evidence; each item below is re-checked on the files.
- Contamination disclosure: none.

### policy_conflict_scan (r2)

Subjects, triggers, targets and `(target_tool, computes)` pairs are unchanged from round 1. What moved:

- E1 adds overwrite #3 on claims_agg_annual_aggregate ("CargoCare products carry an annual aggregate per cover holder." → "The annual aggregate is kept per cover, not per cover holder, and settlements approved on the holder's other covers of the product do not reduce it."); adds "of which a cover carries at most one"; BL read now "recorded for the cover holder".
- E2 replaces "the desk never declines to register a notice" with "The desk registers a notice whenever the lodging conditions of claims_notice_and_time_bar are met … and a notice that fails one of those lodging conditions is not registered at all"; adds "Each notice names one container and one loss; a loss found in another container of the same shipment is never added to a claim file already on the cover and needs a notice of its own." and "a claim still awaiting its documents keeps the cover closed to further notices until it is decided or withdrawn"; notice amount "is not the proven loss".
- E3 adds the 0-day apparent branch: "has no dated window … so such a notice is never rejected with notice_out_of_time"; compute `within_window` short-circuits that case.
- E4 drops the cap: "a cover whose value so fixed is below the minimum or above the maximum is not bound at all, and no other value is substituted for it"; compute loses `max_value`/`bound_value`.
- E5 unchanged except the E5 → E4 condition wording.
- E6 rewritten: "it never exceeds the premium_due_usd the cover's account shows"; prepaid case carved out ("a premium that claims_cover_eligibility requires to be received before binding … is outside this policy"); premium owed = product premium on the bound date, "on any later date … the sum of the premium charges booked on the cover" (compute `on_bound_date`, `premium_owed`); E6 → E4 edge now `state_gate`, gate `cargo_covers.bound_date`.
- Tools: bodies unchanged (still no status/gate/balance check); only the approve `liability_basis` enum gloss changed.
- Scope partition derivable from the graph is unchanged: {E1, E2, E3, W} / {E4, E5, E6}.

### rule_compute_equivalence (r2)

Mechanical re-check (private script, removed): all `compute_basis` fragments verbatim in their rules; all `policy_source` and overwrite `superseded_clause`/`replaced_by` verbatim; no binding lacks a basis (the round-1 `cargo` gap is closed). Forward/reverse sweep of the changed bindings: E3 `within_window` = rule's 0-day sentence; E4 `invoice_value` fallback "When either of those records is missing or carries no value" = compute's `(doc_value and booking_containers)` guard (O-14 closed for E2 and E4); E6 `on_bound_date` / `premium_owed` = "On the cover's bound_date … ; on any later date the premium owed is the sum of the premium charges booked on the cover". One promise without an implementing binding: E6 "it never exceeds the premium_due_usd the cover's account shows" is quoted in `result`'s basis but no binding caps against `premium_due_usd` (R2-O3). E1's rule still excludes delay loss with no delay branch in compute (O-3, kept).

### action_binding_and_uuids (r2)

Unchanged: six `(target_tool, computes)` pairs, each claimed once; seven uuid8s unchanged and independent. Function bodies re-read: none refuses, warns or reads a gate. Docstring change: approve's `proven_loss` gloss now reads "no limit, share, cap or aggregate bound, so the approved amount is the proven loss after any uplift and deductible, including when the invoice value of the affected packages limited the proven loss" (O-7 closed); the `aggregate_limit` gloss still reads "the cover holder's annual aggregate reduced the amount" (R2-O1).

### prerequisite_graph (r2)

| Dependent → problem | kind | gate | policy_source verbatim | Notes |
| --- | --- | --- | --- | --- |
| E2 → E1 | state_gate | claims_notice_and_time_bar.claim_cap | yes | resolved_by approve still needs the W close to make the lodging transition available (O-9, kept) |
| E3 → E2 | value_input | notice_amount | yes | unchanged |
| E5 → E4 | value_input | insured | yes | condition now "fixed at binding under the insured-value rule for binding" (O-10 closed) |
| E6 → E5 | state_gate | claims_premium.remittance_once | yes | real eligibility id (O-8 closed on this edge) |
| E6 → E4 | **state_gate** (was value_input) | `cargo_covers.bound_date` | yes ("The balance is worked out on a bound cover, so, outside the prepaid case, a quoted cover is bound before its premium is settled.") | gate is a field, not an eligibility id; E6's compute still reads the bound cover (`bound_insured`, `on_bound_date`) — R2-O2 |

All seven entries filled; every `problem` an extended id; acyclic; zero authoring-viewpoint hits.

### override_declarations (r2)

- **E1** — C1–C9 of claims_settlement_calculation: same conclusions as round 1 (C2 first clause declared; C4 per rule; C8 desk authority inherited). claims_agg_annual_aggregate: A1 now **declared** (overwrite #3); A2 declared; A3/A4 followed.
- **E2** — N1 followed (one container, one loss per notice matches "written notice naming the container and the loss"). N2 claimant entitlement and N3 cap / one-open-claim now **followed** ("registers a notice whenever the lodging conditions … are met … a notice that fails one of those lodging conditions is not registered at all"; the awaiting-documents case keeps the cover closed). N8 below-minimum: followed, amount = E2 container value.
- **E3** — N6 0-day apparent branch now **followed** (receipt notation, never notice_out_of_time); delay and non-zero branches followed; rest as round 1.
- **E4** — "at least min_insured_value_usd and at most max_cover_value_usd" now **followed** as a refusal gate; prepayment gate re-affirmed.
- **E5** — as round 1; its sentence "a quoted cover is bound before its premium is charged" carries no prepaid carve-out (F-1 residual below).
- **E6** — "may not exceed premium_due_usd" now **followed** (stated, and the later-date branch reads the charges on the ledger); the prepaid case is excluded from E6.

### findings (r2) — disposition of round-1 charter findings

- **F-1 — NOT CLOSED; SOURCE-POLICY RED remains (narrowed).** The E6 half is closed: E6 now says the prepaid premium "is outside this policy". The loop now runs through E4, E5 and base. Situation: cash_in_advance holder, quoted AHL CargoCare Plus cover (premium_prepayment_required true), asks to put it in force and pay. E4: "Every binding gate of claims_cover_eligibility still applies, including … the premium prepayment of a cash_in_advance holder", with base "the premium must be received before binding" → pay, then bind. E5: "a quoted cover is bound before its premium is charged", with base "A premium may be booked only on a cover whose status is active." and "A premium remittance … may not exceed premium_due_usd" (0.00 on a quoted cover) → no premium can be charged or received before binding. No order satisfies both, and after E6's carve-out no policy fixes how much a prepaid premium is. Consequence: no solution in that situation. Affected: E4 rule, E5 rule, base claims_cover_eligibility.prepaid_premium / claims_premium. Bears on task 1 (claims E4, E5).
- **F-2 — CLOSED.** E2 now registers only notices that meet the base lodging conditions, and it resolves the awaiting-documents case. Re-checked against N2/N3: no residual conflict.
- **F-3 — CLOSED** at policy level (overwrite #3 names A1). Residual observation R2-O1 on the tool gloss.
- **F-4 — CLOSED.** E4 refuses out-of-range values; the compute no longer caps.
- **F-5 — CLOSED.** Round-1 situation re-run: charge 2,004.64 on bound day D, contract expires, payment on a later date → E6 premium owed = sum of charges 2,004.64 = premium_due_usd; no excess. Residual R2-O3 (the "never exceeds" cap is stated, not computed).
- **F-6 — CLOSED.** Round-1 situation re-run: Essential, apparent damage flagged, notice two days after delivery → E3 `within_window` True, no notice_out_of_time; matches base N6.

Round-1 observations: closed by edits — O-1 (rules now read "recorded for the cover holder", matching the CFIELD scoping), O-4, O-6, O-7 (proven_loss gloss), O-8 (E6 → E5 edge), O-10, O-11 (E2 "it is not the proven loss"; the schema gloss itself is blueprint text and unchanged), O-14. Kept, unchanged and still observation-level: O-2, O-3, O-5, O-9, O-12, O-13.

New observations (no consequence demonstrable in either world):
- **R2-O1** approve `aggregate_limit` gloss "the cover holder's annual aggregate reduced the amount" vs E1 "kept per cover, not per cover holder". Task 0's holder holds one cover, so the two scopes coincide.
- **R2-O2** E6 → E4 declared `state_gate` with a field as gate, while the edge still carries value: skipping the bind moves E6 from 2,004.64 to 1,870.00 (charge on the quote's 800,000.00) or to 0.00 (no charge). The kind understates the edge; the tree keeps its value_input edge E5 → E4.
- **R2-O3** E6's "it never exceeds the premium_due_usd the cover's account shows" has no implementing binding. On the bound date it relies on "the premium charge booked that day applies the same build-up to the same records", which holds when E5 is applied that day. On later dates the sum of charges minus remittances and refunds equals premium_due_usd by the tool arithmetic.

### closing_checklist (r2)

Written after both round-2 reveals (2026-09-13T06:27Z). The r2 charter-global sections above were frozen before them (hash `17c73afa…e90f` at 06:25:38Z) and are unchanged. There is one post-reveal correction, recorded in `1.md` `### source_gt_comparison (r2)`: under the replay-unchanged test, R2-O2's value claim comes transitively through E5, and the direct E6 → E4 edge moves only the terminal state. The residual of R2-O2 is the field-as-gate label only.

**The difficulty is still not closed out: charter-global SOURCE-POLICY RED F-1 remains open** (E4 re-affirms the base prepayment gate while E5 orders bind-before-charge and base forbids any premium booking or remittance on a quoted cover; a cash_in_advance holder of a prepayment product has no feasible order). Neither task's world triggers it.

Round-1 → round-2 disposition: F-T0-1 closed; F-2, F-3, F-4, F-5, F-6 closed; F-1 narrowed but open. Observations O-1, O-4, O-6, O-7, O-8 (on E6 → E5), O-10, O-11, O-14, O-T0-2, O-T0-5, O-T1-1, O-T1-2 (on E6 → E5) closed by edits; O-2, O-3, O-5, O-9, O-12, O-13, O-T0-3, O-T0-4, O-T1-3 kept, still observation-level. New observations: R2-O1, R2-O2 (corrected), R2-O3, R2-O-T0-1. No new RED; no regression in any scored value, order or terminal state.

Checklist status:
- Audit files: `_difficulty.md`, `0.md`, `1.md`, each with `## revision_2` appended; round-1 text untouched.
- Coverage and scope: task 0 {E1, E2, E3} + W + approve/close/lodge/reject; task 1 {E4, E5, E6} + bind/charge/pay; pairwise disjoint over whole trees; all six extended policies covered; one workflow, claimed by task 0 only; each task tool used by one task; uuid8s unchanged and independent.
- Problem trees: task 0 — 2 policy-conveyed prerequisites, 1 value_input edge, acyclic (holds after the persona rework); task 1 — 2 prerequisites, 1 value_input edge (E5 → E4), acyclic. The difficulty-wide graph is acyclic.
- Workflow zero-wait: `requires_external_wait: false` + `zero_wait_proof` on all five task-0 gold actions.
- Artifact stability during r2: `claims.extended.yaml` `7e7453d4…9d7f`, `task_tools.py` `31441b0c…7b02` unchanged from the coordinator's r2 hashes; tasks at reveal `0.json` `bf9341bb…e85d`, `1.json` `0a3db2d0…6435`.
- Gate re-run on the final form: not performed (closing conditions unmet because of F-1). The coordinator's round-2 gate block is green, as expected for a defect that sits in policy semantics.

## revision_3

### charter_global_frozen (r3)

- Written 2026-09-13 at about 06:33Z, before either round-3 task reveal; nothing here derived from a round-3 GT. Earlier revisions untouched.
- Both shared inputs changed, so the charter-global sections are re-derived in full: `claims.extended.yaml` r2 `7e7453d4…9d7f` → r3 `d25d800f9362a63349a04511bae99515c6125a5df3026f4b0647d9f4b54469ec`; `task_tools.py` r2 `31441b0c…7b02` → r3 `8e608b1e977a1edfce6bc97b3596fcbeac38c265625272d3cf34c7a81ced63fc` (both match `source_r3/HASHES.txt`). Blueprint unchanged (claims.yaml `3fa292d8…3818`, mtime 03:06); base copy still verbatim (diff = separator line only).
- Entry conditions: coordinator's r3 gate block all exit 0 (traceability deferred). Masks `source_r3/0.masked.json` `8b338c14…fff7`, `source_r3/1.masked.json` `0ddad7a4…23f3` re-verified. Against r2: both worlds and frozen_times identical; task 0's user_scenario loses exactly one sentence ("You assume the shipment already has a claim running with the line's claims people and that this can simply go with it"); task 1's mask is byte-identical.
- Reworker's claims not taken as evidence. Contamination disclosure: none.

### policy_conflict_scan (r3)

What moved since r2 (everything else re-read and unchanged, including E1/E2/E3 rules, computes and edges, probed sentence by sentence against the r2 quotations, and the workflow W):
- **E4** — "including … the premium prepayment of a cash_in_advance holder" removed; added "This policy governs the binding of a cover whose premium is settled after binding; a cover whose holder's credit_status is cash_in_advance under a product whose premium_prepayment_required is true, whose premium claims_cover_eligibility requires to be received before binding, is outside this policy and outside the premium charge and premium settlement policies that follow binding. Within that scope every other binding gate of claims_cover_eligibility still applies, including the binding deadline … and the bar on binding a CargoCare product for a holder on credit_hold." Compute unchanged.
- **E5** — added "This policy governs the premium of a cover whose premium is settled after binding; a premium that claims_cover_eligibility requires to be received before binding, because the holder's credit_status is cash_in_advance and the product's premium_prepayment_required is true, is outside this policy." Compute unchanged.
- **E6** — sentence "and it never exceeds the premium_due_usd the cover's account shows" deleted; added "A cover that has never been bound, and so carries no bound_date, owes no premium under this policy, and its premium owed is 0.00."; compute `premium_owed` = `0 if not F('bound_date') else (product_premium if on_bound_date else SUM(charges))`; edge E6 → E4 now `value_input`, gate `premium_owed`.
- **Tools** — bodies unchanged (same 18 DB calls, no status/gate/balance check); approve gloss now "aggregate_limit (the annual aggregate still available on the cover reduced the amount)".
- The three carve-outs name the same scope in the same terms (credit_status cash_in_advance AND premium_prepayment_required true), so E4, E5 and E6 agree on which covers they do not govern.

### rule_compute_equivalence (r3)

Mechanical re-check (private script, removed afterwards): all compute_basis fragments, policy_sources and overwrite clauses verbatim; every binding has a basis; each `value_input` gate names a binding of its dependent's compute (notice_amount, insured, premium_owed). E6 sweep: `premium_owed` implements "On the cover's bound_date …; on any later date … the sum of the premium charges …. A cover that has never been bound … its premium owed is 0.00." with the three branches in that order; `result` = "less … remittance … and … refund …, never below 0.00". The r2 unimplemented promise is gone with the deleted sentence. The base cap "may not exceed premium_due_usd" is still inherited, and it holds in scope by construction: later-date branch = charges − remittances − refunds = premium_due_usd by the tool arithmetic; bound-date branch = the same-day E5 charge (R3-O1). O-3 (no delay branch in E1) kept.

### action_binding_and_uuids (r3)

Unchanged pairs and uuid8s; each claimed once; no tool judges a prerequisite. R2-O1 closed: approve's `aggregate_limit` gloss now speaks of the aggregate "still available on the cover", matching E1 overwrite #3.

### prerequisite_graph (r3)

| Edge | kind | gate | Real gate / binding? |
| --- | --- | --- | --- |
| E2 → E1 | state_gate | claims_notice_and_time_bar.claim_cap | eligibility id ✓ (O-9 kept) |
| E3 → E2 | value_input | notice_amount | binding ✓ |
| E5 → E4 | value_input | insured | binding ✓ |
| E6 → E5 | state_gate | claims_premium.remittance_once | eligibility id ✓ |
| E6 → E4 | value_input | premium_owed | binding ✓ — R2-O2 closed |

Acyclic, all filled, all `problem` ids extended, zero authoring-viewpoint hits. E6 → E4 under replay-unchanged (gold charge 2,004.64 still booked, bind skipped): E6 = 0.00 instead of 2,004.64 — the edge now carries value directly, consistent with its kind.

### override_declarations (r3)

E1, E2, E3: conclusions of r2 stand (text unchanged). E4: min/max gate followed; the prepayment sentence is now outside E4's scope instead of re-affirmed, and every other binding gate is inherited. E5: base build-up followed; its bind-before-charge sentence applies only in scope, where base's prepayment gate does not fire. E6: "may not exceed premium_due_usd" inherited and satisfied in scope; prepaid case outside scope. No undeclared override found.

### findings (r3) — disposition

- **F-1 extended side — CLOSED.** The r2 residual was E4 re-affirming "premium received before binding" while E5 ordered bind-before-charge. Now E4, E5 and E6 all exclude the same set of covers (cash_in_advance holder AND premium_prepayment_required true). Within that shared scope the base prepayment gate never fires, so base premium_on_active and the remittance cap are met by the single order bind → charge → pay. No in-scope situation is left with no valid order or with two answers. Out of scope the extended charter says nothing, and binding, charging and settling such a cover falls to base alone.
- **B-1 (carried, base-internal; logged by the coordinator as a known blueprint issue).** Base alone still has no feasible order for a cash_in_advance holder of a prepayment product: claims_cover_eligibility "the premium must be received before binding" vs claims_premium "A premium may be booked only on a cover whose status is active." / "may not exceed premium_due_usd". The text is identical in blueprint `products/claims.yaml` and in the base copy. Per the coordinator's note it moves no scored value in either world (task 0 has no binding; task 1's holder is credit_approved on a no-prepayment product). It is recorded here so the audit trail stays complete; the extended charter no longer adds to it.
- **R2-O1 closed** (tool gloss). **R2-O2 closed** (E6 → E4 value_input with a binding as gate). **R2-O3 closed** (unimplemented sentence deleted; base cap inherited and met in scope). R2-O-T0-1: see task 0 file.
- Kept, still observation-level: O-2, O-3, O-5, O-9, O-12, O-13 (charter); O-T0-3, O-T0-4, O-T1-3 (per task).
- **R3-O1 (observation, new surface).** E6's bound-date branch rests on the sentence "because the premium charge booked that day applies the same build-up to the same records". It is true whenever E5 is applied that day on unchanged records. If the holder's contract status changed between a same-day charge and payment, the recomputed product premium would differ from premium_due_usd, and the inherited base cap would then bound the payment. That needs an intra-day change of a cross-category record, and neither world has one.
- No new RED.

### closing_checklist (r3)

Written after both round-3 reveals. The r3 charter-global sections above were frozen before them (`_difficulty.md` sha256 `9cd631bb…f36a` at 06:34:58Z) and are unchanged. No post-reveal correction was needed this round.

**Round-2 disposition:** F-1 extended side closed; R2-O1, R2-O2, R2-O3 closed (charter/tools); R2-O-T0-1 closed (task 0 persona). Kept observations O-2, O-3, O-5, O-9, O-12, O-13, O-T0-3, O-T0-4, O-T1-3 are unchanged and still observation-level. New: R3-O1 (observation). No new RED; no regression in any scored value, order, owner or terminal state across r1 → r3.

**Per task (r3):** task 0 PASS / PASS / PASS; task 1 PASS / PASS / PASS (policy self-consistency / problem tree / unique solution).

Step-4 checklist:
- Audit files `_difficulty.md`, `0.md`, `1.md`, each with revisions 1–3 in order; earlier text untouched; every revision's per-task derivation frozen and hashed before its reveal.
- Extended policies fully covered; scopes pairwise disjoint over whole trees (task 0 {E1, E2, E3} + W; task 1 {E4, E5, E6}); exactly one workflow, claimed by task 0 only; task tools closed (each used by one task); uuid8s independent and unchanged since r1.
- Problem trees: task 0 — 2 policy-conveyed prerequisites, 1 value_input edge, acyclic; task 1 — 2 prerequisites, 2 value_input edges, acyclic; difficulty-wide graph acyclic, no cross-task edge.
- Gates on the final form: the coordinator's round-3 gate block (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE — all OK, exit 0; traceability deferred until KB publication) was run on the reworked files. Their hashes match those audited here (`claims.extended.yaml` `d25d800f…69ec`, `task_tools.py` `8e608b1e…63fc`), and both stayed unchanged through this re-audit. Task files at reveal: `0.json` `a494ba6e…a540`, `1.json` `2b051bda…789a`.

**Closing conclusion:** the difficulty's instantiation artifacts (extended charter, task tools, both tasks) pass the source-layer audit on all three relationships. One defect is carried outside them: **B-1**, the base-internal prepayment loop in blueprint `products/claims.yaml` (and its verbatim base copy). The coordinator has logged it as a known blueprint issue; no task world engages it, and no extended policy now adds to it.

## revision_4

### charter_global_frozen (r4)

- Written 2026-09-13 at about 07:35Z, before either round-4 task reveal; nothing here derived from a round-4 GT. Earlier revisions untouched.
- Inputs: `claims.extended.yaml` r3 `d25d800f…69ec` → r4 `7e4caefab618eb65010367bc94bdfb8f15c87b5634963ee69c088eb6b920df82` (changed → charter-global sections re-derived); `task_tools.py` `8e608b1e…63fc` (unchanged since r3 → the tool-side conclusions of `### action_binding_and_uuids (r3)` are carried forward on that hash). Blueprint unchanged (`claims.yaml` `3fa292d8…3818`); base copy still verbatim.
- Entry conditions: coordinator's r4 gate block, now including `check_traceability`, all OK / exit 0. Masks `source_r4/0.masked.json` `06445a00…6819` (task 0 user_scenario changed) and `source_r4/1.masked.json` `0ddad7a4…23f3` (identical to r2/r3) re-verified; both worlds and frozen_times identical to r3.
- Contamination disclosure: the literal `ccl_6c9158c0b2c9` now appears inside the task-0 mask itself (user_scenario). I already knew it from the round-1 reveal (it is the gold reject `claim_id`). It enters this round as audited input, not as leaked GT; I recomputed it independently (below) rather than taking it on trust.

### charter delta and re-derivation (r4)

- The only charter change: E6 → E4 prerequisite `condition` "The quoted cover has been bound, so it carries a bound_date and the insured value fixed at binding." → "… so it carries a binding date and the insured value fixed at binding." Kind (`value_input`), gate (`premium_owed`), policy_source, resolved_by and effect are unchanged. The new wording means the same thing (the cover's `bound_date` is its binding date), and it neither strengthens nor weakens the cited sentence "The balance is worked out on a bound cover, so, outside the prepaid case, a quoted cover is bound before its premium is settled." No snake_case field name remains in any of the five `condition` texts. (The `effect` texts still name fields such as `cargo_covers.premium_due_usd` and `bound_date`. That is internal-reference wording, not authoring-viewpoint phrasing, and the renderer's report concerned `condition` — observation only.)
- Everything else re-checked, not assumed: every rule, compute and compute_basis re-verified verbatim (mechanical, private script, removed afterwards). E1/E2/E3 rule lengths identical to r3 (3175 / 2075 / 2612). The r3 E4/E5/E6 scope sentences and the E6 never-bound sentence are present verbatim; the deleted "never exceeds" sentence is still absent. E6 `premium_owed` expression unchanged. W unchanged (5 steps, 4 dataflow entries, `prerequisite: []`). Zero authoring-viewpoint hits.
- Re-derived sections, conclusions: `policy_conflict_scan` — no conflict; `rule_compute_equivalence` — all bindings verbatim-backed, each value_input gate a real binding; `action_binding_and_uuids` — carried by hash (unchanged pairs, uuid8s, gloss); `prerequisite_graph` — same five edges, kinds and gates as r3, acyclic; `override_declarations` — r3 conclusions stand (no text they rest on moved).
- DSL recompute on the r4 charter and r4 masks: task 0 22,704.00 / 103,200.00 / notice_out_of_time (opening contrast below_minimum_claim); task 1 857,600.00 / 2,004.64 / 2,004.64.

### findings (r4)

- Round 3 had no RED. Carried: B-1 (base-internal, coordinator-logged). Carried observations: O-2, O-3, O-5, O-9, O-12, O-13, R3-O1.
- **Renderer report (internal field name in a prerequisite condition): closed** by the E6 → E4 reword, with no semantic change.
- No new charter-level defect.
- Correction on an erlbench fact my earlier revisions relied on implicitly. `erlbench/engine.py` `call_user_discoverable_tool` returns a user-owned tool's result to the simulator only; the agent sees it only if the simulator relays it. My r1–r3 task-0 derivations wrote the reject's `claim_id` as "the lodge receipt's claim_id", as if the agent saw the receipt. The agent-reachable source in those rounds was a runtime share query after the lodge (`find_cargo_claims(cover_id=…)` reads the live DB and returns the new file), which the skill counts as a reachable source. `check_traceability` models only prior agent gold actions plus the simulator brief, and the gold had no post-lodge query, which is why it went red. No r1–r3 verdict changes. The task-0 consequences are handled in `0.md` `## revision_4`.

### closing_checklist (r4)

Written after both round-4 reveals. The r4 charter-global sections above were frozen before them (`_difficulty.md` `38788cf0…38e0` at 07:35:40Z) and are unchanged.

- **Round-3 disposition:** no round-3 RED existed. Both round-4 source changes were verified.
  - (1) The task-0 persona now relays the claim reference. This is not a RED; it is observation R4-O-T0-1 (`0.md` `## revision_4`). The literal is accurate only for the gold lodge arguments, and the unique solution and reachability are unchanged.
  - (2) The E6 → E4 condition reword closes the renderer report with no semantic change.
  - No new RED; no regression in any scored value, owner, order or terminal state from r1 to r4.
- **Per task (r4):** task 0 PASS / PASS / PASS; task 1 PASS / PASS / PASS.
- **Step-4 checklist:**
  - Audit files carry revisions 1–4 in order, earlier text untouched, and every revision's derivation was frozen before its reveal.
  - Coverage and scope are unchanged: task 0 {E1, E2, E3} + W; task 1 {E4, E5, E6}; disjoint; one workflow, claimed by task 0; task tools closed; uuid8s unchanged.
  - Trees: task 0 has 2 prerequisites / 1 value_input; task 1 has 2 prerequisites / 2 value_input. Both acyclic, and the difficulty-wide graph is acyclic.
  - Gates on the final form: the coordinator's r4 block, now including `check_traceability` (TRACEABILITY OK), all exit 0. It was run on files whose hashes match those audited here (`claims.extended.yaml` `7e4caefa…df82`, `task_tools.py` `8e608b1e…63fc`), and both stayed unchanged through this re-audit. Task files at reveal: `0.json` `2c736763…211a`, `1.json` `db79a88d…727c`.
- **Closing conclusion:** unchanged from r3. The difficulty's instantiation artifacts pass the source-layer audit on all three relationships. B-1 is carried as the coordinator-logged blueprint issue, and no task world engages it.
