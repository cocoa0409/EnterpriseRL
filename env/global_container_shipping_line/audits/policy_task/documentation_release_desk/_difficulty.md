# Policy-task audit — documentation_release_desk / charter-global

## charter_global_frozen

- Scenario: `env/global_container_shipping_line`; difficulty `documentation_release_desk`; category `bol`; M = 2 (tasks 0 and 1).
- Freeze time: 2026-09-13T05:08:21Z (revision_1), taken from the file mtime of the completed charter-global section. The first GT reveal command ran at 05:11:59Z. Auditor: independent erl-task-policy-audit agent. I did not write any of the audited artifacts.
- Freeze hashes, recomputed by me with sha256sum. They match the coordinator's `HASHES.txt`:
  - `tasks/documentation_release_desk/bol.extended.yaml` = `a5aafd947662f8f3ea4afb7fc69db08e8e87e0788e9d5b79d667a15cd8fbd1b7`
  - `tasks/documentation_release_desk/task_tools.py` = `743f7e9ee3f90a5e5b30ecce0e71458731ece1e65c4915d2a4f1fc5ab1229689`
- Entry conditions (Step 0) were supplied with the brief. The gates were re-run by the coordinator on the current files and all were green: `check_extended` EXTENDED OK, `check_task_tools` TASK TOOL CONTRACT OK, `replay_tasks` REPLAY OK, `check_solvability` SOLVABILITY OK, `check_compute` COMPUTE OK, `check_grounding` GROUNDING OK and `check_cross_fire` SCOPE OK. `check_traceability` is deferred until the KB is published. Masked views came with their sha256 values: 0.masked = `e429d5ea…87fa`, 1.masked = `d978c1ac…f2ef`. My recomputed hashes match. A green gate only qualifies the difficulty for this manual audit. It does not prove correctness.
- Fields I was permitted to read while building this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/bol.yaml`, the rank lines of `blueprint/products/contract.yaml`, the whole `bol.extended.yaml`, the whole `task_tools.py`, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `eval_compute`).
- Fields explicitly masked while writing this section: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, and any existing audit. No task JSON under `tasks/documentation_release_desk/tasks/` was opened. No search was run over `tasks/`.
- This section contains nothing derived from a revealed GT. It was written before either task's GT was revealed.

### base copy check

`head -n 1010 bol.extended.yaml` diffed against `blueprint/products/bol.yaml` gives only one extra trailing blank line (`1009a1010 > `). The base section is a verbatim copy.

### policy_conflict_scan

The structured policy contains 6 extended policies and 1 workflow:

| id | subject | computes | target_tool (owner) | prerequisite |
| --- | --- | --- | --- | --- |
| bol_ext_correction_originals_return | bol_originals_surrendered | originals_count | return_originals_for_correction_b9bd03b3 (user) | [] |
| bol_ext_post_departure_correction_fee | bol_correction_fee_charged | amount_usd | charge_correction_fee_18211c73 (agent) | state_gate -> correction_originals_return |
| bol_ext_corrected_set_issue | bol_set_replaced | originals_count | issue_corrected_set_a7062696 (agent) | value_input -> correction_originals_return; state_gate -> post_departure_correction_fee |
| bol_ext_lost_original_void_count | bol_originals_voided, bol_set_replaced, bol_reissue_fee_charged | voided_originals_count | reissue_lost_originals_set_197b224c (agent) | [] |
| bol_ext_telex_full_set_surrender | bol_originals_surrender_completed | originals_count | surrender_full_set_at_origin_68a55055 (user) | value_input -> lost_original_void_count |
| bol_ext_telex_release_fee | bol_release_fee_charged | amount_usd | charge_telex_release_fee_be5da3ed (agent) | value_input -> telex_full_set_surrender |
| bol_wf_post_issuance_correction_with_originals_back (workflow) | 4 steps: return_originals (user) -> apply_particular_correction_a24e9121 (agent) -> charge_correction_fee (agent) -> issue_corrected_set (agent) | — | — | [] |

Overlapping subjects and triggers:
- `bol_originals_surrendered`: this subject is written by ext `correction_originals_return` (a lodgement for a correction, with no status change) and by base `bol_telex_release` / `bol_cargo_release` (origin and destination surrender). Ext `telex_full_set_surrender` writes the holding event `bol_originals_surrender_completed`, and that event triggers a `bol_originals_surrendered` row. The two surrender paths are separated by the reason of the request (correction vs telex) and by the tool. Only the telex path changes the status to `surrendered`. This matches base (`bol_correction` "The returned originals are recorded as surrendered at the origin office"; `bol_telex_release` "the document moves to surrendered"). No conflict.
- `bol_set_replaced`: ext `corrected_set_issue` covers the correction path and ext `lost_original_void_count` covers the loss path. Each has its own trigger (correction applied vs lost-original request) and its own tool, and each computes a different argument. No conflict.
- `bol_release_fee_charged`: ext `telex_release_fee` books charge_code `telex_release_fee` only. Base `bol_cargo_release` books `loi_release_fee`. These are different charge codes and different requests. No conflict.
- `bol_correction_fee_charged`: only ext `post_departure_correction_fee` books it. Its tier guard is `originals_return_required_for_correction`. The complementary tiers stay under base `bol_correction`, as the ext policy says: "the fee of bol_correction applies unchanged".

Eligibility and time anchors: none of the extended policies re-states a base time window with a different anchor, with one exception in ext `lost_original_void_count` (anchor "latest" request, see O4). Every base `eligibility` item (window, originals_back_first, fee_on_issued, charge_request_once, waiting_period, reissue_while_issued, documentation_party_only, full_set_surrendered, telex_fee_on_surrendered, release_request_charged_once) is left in force. Two extended policies restate it consistently (`effected`, `all_back`).

Terminal states: correction path — the document stays `issued`, `bl_set_sequence` goes up by 1 and the originals are back in circulation. Telex path — the document is `surrendered` with `originals_outstanding` 0. Both match base `lifecycle`.

Cross-category reads: every extended policy declares `cross_category` booking. `telex_release_fee` also declares contract. The declared reads (`status`, `departed_date`, `contract_id`, contract `variant_name`/`status`) are the only cross reads in the computes. See O1 for the implicit customer scoping that the DSL adds.

Scope exclusivity and completeness across M = 2: the two masked worlds support the partition {correction_originals_return, post_departure_correction_fee, corrected_set_issue, the workflow and its step apply_particular_correction} and {lost_original_void_count, telex_full_set_surrender, telex_release_fee}. In the first world there is a correction request on a straight bill with outstanding originals. In the second there is a telex request plus a lost-original request on a negotiable bill. The two tool sets are disjoint and together cover all 7 task tools. Pre-reveal this is an expectation drawn from the worlds only. The declared `charter_scope` is checked in `closing_checklist`.

Conflicts found by this scan are listed under `findings` (G1, G2).

### rule_compute_equivalence

Semantics used for the DSL come from `check_compute.build_env`:
- `SUM/COUNT/MAX/LATEST` are auto-scoped to the holding (`bl_id = HID`).
- `CFIELD(cat, field, **eq)` adds `customer_id = CUST`, where CUST is the documentation party of the document.
- `RND` is Python `round(float(x), n)`.
- `NOW` is the date part of `frozen_time`.

**bol_ext_correction_originals_return** (forward rule -> basis -> compute):
- set_in_force = `F('bl_set_sequence')`, basis "the set whose number is the document's bl_set_sequence" ✓.
- issued/surrendered/voided_in_set = three `SUM` over `bol_ledger.originals_count`, filtered by event_type and `bl_set_sequence=set_in_force`, basis quoted ✓. The rule's "never less than zero" is `MX(...,0)` ✓. "whole number" is `int(...)` ✓.
- shipped (loaded / departed / closed, or gated_in only when `received_for_shipment_allowed`) ✓. return_required is the tier flag ✓. The zero branch is quoted ✓.
- Reverse sweep: every binding has a verbatim quotation. "never taken from the caller's own count" is a negative instruction with no binding, and it does not change the value. "recorded as one entry for that set" is carried by the tool, which writes one row. No invented basis and no empty promise.

**bol_ext_post_departure_correction_fee**:
- departed_date is read from the booking via `CFIELD`, basis "read from the booking record" ✓. vessel_departed / chosen_fee ✓. return_tier zero branch ✓. `RND(...,2)` ✓.
- The rule claims "On these tiers no correction after issuance falls inside a free allowance and the named consignee is never changed". I verified this against base `variants`. The four tiers with `originals_return_required_for_correction: true` are Straight, Negotiable, Combined Transport and Switch. All four have `free_corrections_after_issuance: 0` and `max_consignee_changes_after_issuance: 0`. The claim is true, so base's `pre/post_departure_amount` collapses exactly to ext's `chosen_fee`.
- Reverse sweep: the keying-error exclusion ("stays uncharged under bol_correction and is not booked under this policy") has no compute branch, whereas the tier exclusion is encoded as 0 (O6). "exactly one correction fee row, tied to the correction request" is carried by the tool arguments.

**bol_ext_corrected_set_issue**:
- outstanding = `F('originals_outstanding')`, per_set = `P('originals_issued_count')`, shipped, all_back = `outstanding == 0`, result = `per_set if (all_back and shipped) else 0`. Every binding has a verbatim quotation ✓. "read ... as they stand at the moment the corrected set is issued" matches the handling time ✓.
- The rule's "Second, the correction fee ... has already been booked" is an ordering gate, not a value. It is declared as a state_gate edge and is correctly absent from compute.

**bol_ext_lost_original_void_count**:
- issued/surrendered/voided_total are whole-history `SUM`s ✓. in_circulation = `MX(...,0)` ✓.
- loss_reported = `LATEST(bol_service_requests, created_at, request_type=lost_original_reissue)`, basis "the date part of the latest lost-original reissue request's created_at" ✓. waited = `DAYS(loss_reported, NOW) >= P(...)`. DAYS takes the date part on both sides and uses `>=`, which matches "on or after ... calendar days" ✓.
- shipped ✓, `lost_original_reissue_available` ✓, result ✓.
- The rule asserts that the whole-history balance equals the set-in-force balance "because a set is always fully surrendered or voided before the next set is issued". That is a claim about the world, and it is verified per task.

**bol_ext_telex_full_set_surrender**:
- The whole-history balance, shipped and `telex_release_available` are all quoted ✓.
- The lost-original sentence is an ordering gate, declared as the value_input edge. Before the reissue, compute returns the balance 1, which is physically unsurrenderable, and the rule prose forbids surrendering before the reissue. See `prerequisite_graph`.

**bol_ext_telex_release_fee**:
- doc_status, outstanding, shipped and effected ✓.
- contract_tier = `CFIELD('contract','variant_name', contract_id=<booking.contract_id>, status='active')` ✓, "not the booking's own, or is not active, never exempts" ✓.
- contract_rank uses `params` rank_starter..rank_strategic_partner = 1..6. I checked this against `blueprint/products/contract.yaml` `variants[].rank`: Starter 1, Standard 2, Regional 3, Key 4, Global 5, Strategic 6 ✓.
- exempt = `min_rank > 0 and rank >= min_rank` ✓. result = `RND(fee if effected and not exempt else 0, 2)` ✓.

Engine-level conventions that the rule text does not state (O1, O2) are recorded as observations. Neither has a consequence in either masked world: in both worlds `bookings.customer_id == bills_of_lading.customer_id == service_contracts.customer_id`, and every fee is an exact 2-decimal tier value.

Result: check 2 PASSES, with observations O1, O2 and O6.

### action_binding_and_uuids

- `(target_tool, computes)`: the six pairs are pairwise distinct. Each task tool is targeted by at most one extended policy. `apply_particular_correction_a24e9121` is bound only as workflow step 1 (`computed_by: []`), and its arguments are verbatim copies of `bol_service_requests` fields.
- Only one business reading per binding. The subject, base refs, docstring and terminal state agree for every tool:
  - `return_originals_for_correction` writes one `bol_originals_surrendered` row at `origin_office` and lowers `originals_outstanding`. It does not change the status and charges nothing.
  - `apply_particular_correction` rewrites one particular and completes the request. It books no fee and issues no set.
  - `charge_correction_fee` writes one `bol_correction_fee_charged` row carrying the request_id and raises `charges_due_usd`.
  - `issue_corrected_set` writes one `bol_originals_issued` row, sets `bl_set_sequence` and `issued_date`, raises `originals_outstanding` and books no issuance fee.
  - `reissue_lost_originals_set` writes a void row (on set = new − 1), an issued row and a `bol_reissue_fee_charged` row, then completes the request.
  - `surrender_full_set_at_origin` writes one surrender row, lowers `originals_outstanding` and sets status `surrendered`.
  - `charge_telex_release_fee` writes one `bol_release_fee_charged` row with `telex_release_fee` and completes the telex request.
  No tool adds a confirmation, review or wait.
- Tool bodies judge no prerequisite. I read every one of the 7 function bodies (task_tools.py lines 30–270). None contains a conditional refusal, an error return or a precondition check. Each unconditionally calls `ctx.create`/`ctx.update` and returns a confirmation. The module docstring says the same: "No tool checks a business precondition, computes a fee or reconciles a ledger".
- uuid8 tails: `b9bd03b3`, `a24e9121`, `18211c73`, `a7062696`, `197b224c`, `68a55055`, `be5da3ed`. All seven are distinct. No two share a prefix of more than one hex digit (`18…`/`19…` differ at digit 2, and `a7…`/`a2…` differ at digit 2). None is a sequence, a shared stem with a changed tail, or an adjacent value. None is reused by a share tool. They look independently generated. PASS.

### prerequisite_graph

Nodes are the 6 policies and the workflow. Every one has a `prerequisite` field: [] for `correction_originals_return`, `lost_original_void_count` and the workflow.

| # | dependent -> problem | kind | gate | policy_source verbatim in dependent's rule? | resolved_by makes effect hold? | kind/gate match |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | post_departure_correction_fee -> correction_originals_return | state_gate | `bol_correction.originals_back_first` | yes: "Before the fee is booked, the correction it charges must already stand on the document, which on such a tier is possible only once every outstanding original has been lodged back with the line under bol_correction." | yes: the lodgement lowers `originals_outstanding` to 0, so originals_back_first holds, the correction can stand and the fee becomes bookable | a real eligibility id in base `bol_correction` ✓. It applies_to `bol_particulars_corrected`, `bol_set_replaced`; the edge reaches the fee through "the correction it charges must already stand" |
| E2 | corrected_set_issue -> correction_originals_return | value_input | `all_back` | yes: "First, the originals still in circulation on the document have come down to zero because every original of the previous set has been lodged back with the line." | yes: `outstanding` becomes 0, so `all_back` becomes true and the result changes from 0 to `originals_issued_count` | `all_back` is a compute binding of the dependent ✓ |
| E3 | corrected_set_issue -> post_departure_correction_fee | state_gate | `bol_ledger.request_id` | yes: "Second, the correction fee due on the correction request the set carries has already been booked, so that the corrected set leaves the desk with its documentation account complete." | yes: a fee row with that request_id exists | `bol_ledger.request_id` is a field path, not an eligibility id. The dependent policy has no `eligibility` block and the gate lives in rule prose only (O3) |
| E4 | telex_full_set_surrender -> lost_original_void_count | value_input | `in_circulation` | yes: "Where an original of the set in force has been reported lost, the full set cannot be surrendered until the replacement set has been issued under bol_lost_original_reissue, because the lost original counts as in circulation until it is declared void and a surrender without it leaves originals outstanding." | yes: void −k, issue +n, so in_circulation changes from k (the lost ones) to n | `in_circulation` is a compute binding ✓ |
| E5 | telex_release_fee -> telex_full_set_surrender | value_input | `effected` | yes: "A telex release fee is booked only once the release is effected, which requires that the full set of originals in circulation has been surrendered at the origin office so that the document is surrendered and originals_outstanding is 0" | yes: status becomes `surrendered` and outstanding 0, so `effected` becomes true | `effected` is a compute binding ✓ |

- Every `problem` points at an extended-policy id in this file. None points at a base policy or at itself.
- Acyclicity: {E1, E2, E3} form a DAG over {correction_originals_return < post_departure_correction_fee < corrected_set_issue}. {E4, E5} form a chain {lost_original_void_count < telex_full_set_surrender < telex_release_fee}. The two components share no node. There is no cycle.
- `condition` vs cited sentence: E1, E2 and E3 are copied verbatim or near-verbatim. E4's condition ("the replacement set has been issued ... before the full set is surrendered") restates the cited sentence without strengthening or weakening it. E5's condition matches the cited sentence. ✓
- No authoring-viewpoint wording ("in this task", "at the opening", "the current world") appears in any `prerequisite` block. ✓
- Result: check 7 PASSES, with one observation (O3).

### override_declarations

Each extended policy is checked sentence by sentence against its `base_policy_refs`. Only sentences that govern the quantity the policy scores, or the action it binds, are listed. Sentences on other subjects are marked N/A in bulk.

**bol_ext_correction_originals_return** (refs bol_correction, bol_telex_release, bol_cargo_release, bol_issuance; `overwrite: []`)
- bol_correction "the correction is applied only after every outstanding original has been returned to the line, so that originals_outstanding is 0": ext's count equals the originals outstanding of the set in force. Base's quantity is `originals_outstanding`, which is identically the whole-history delta sum. The two agree whenever earlier sets are closed, and earlier sets are always closed by base (corrected set only after outstanding reaches 0; reissue voids what is outstanding). **Follows.**
- bol_correction "The returned originals are recorded as surrendered at the origin office": ext writes one surrender row at `origin_office`. **Follows.**
- bol_correction "a request whose originals are not returned within originals_return_deadline_days of the request lapses and is withdrawn": ext does not address this. **Inherited, not weakened.**
- bol_issuance "puts originals_issued_count originals of the set into circulation" and the shipped_on_board gate: ext's zero branch for a booking that has not shipped cannot be reached on an issued document. **Follows.**
- bol_telex_release / bol_cargo_release: surrender-row shape only. The sentences on who may request (documentation party) are consistent with ext's "the documentation party lodges". Base bol_correction does not name who returns originals. **No conflict.**

**bol_ext_post_departure_correction_fee** (ref bol_correction; `overwrite: []`)
- "a consignee change is charged consignee_change_fee_usd": ext says "the named consignee is never changed" on return tiers. That is true, since `max_consignee_changes_after_issuance` is 0 on all four. **Follows.**
- "free while bol_msr_corrections_after_issuance is below free_corrections_after_issuance and otherwise costs correction_fee_after_issuance_usd before departure or correction_fee_after_departure_usd after departure": `free_corrections_after_issuance` is 0 on all four return tiers, so the free branch cannot fire. The departure split is identical. **Follows.**
- "A correction caused by the line's own keying error ... is never charged": ext defers this explicitly. **Follows.**
- "A correction fee is booked only on a document whose status is issued" and "Each correction request is charged at most once": ext says "exactly one correction fee row, tied to the correction request". **Follows / inherited.**
- `max_corrections_after_issuance`, the window, correctable fields and weight tolerance: not restated. **Inherited.**

**bol_ext_corrected_set_issue** (refs bol_correction, bol_lost_original_reissue, bol_issuance; `overwrite: []`)
- bol_correction "the corrected document is issued as the next set, bl_set_sequence plus 1, carrying no issuance fee": **Follows.**
- The number of originals in the corrected set is not stated by bol_correction. ext takes `originals_issued_count`, which is consistent with bol_issuance and with bol_lost_original_reissue "with originals_issued_count originals". **Follows.**
- The "fee first" gate is an addition. Base says nothing about the order of the correction fee and the corrected set. Status stays `issued` either way, so base allowed both orders. ext narrows this and does not contradict any base sentence. **Addition, not an override.**
- ext's zero branch "When originals are still outstanding ... the number is zero" sits against base "applied only after every outstanding original has been returned". The branch describes a set that base forbids issuing. It is counterfactual only (O5).

**bol_ext_lost_original_void_count** (refs bol_lost_original_reissue, bol_cargo_release, bol_correction; `overwrite: []`)
- "On reissue, the originals still outstanding of the set in force are declared void": ext uses the whole-history balance, which equals the set in force under the invariant that closed sets stay closed. **Follows.**
- "The earliest reissue date is the date part of the loss request's created_at plus the tier's waiting days": ext anchors to the *latest* lost-original request on the document. The two differ only when a document has several such requests (O4). **Follows in the one-request case.**
- "The request is registered and waits for the documentation party, who alone can sign the letter of indemnity and deliver a bank guarantee ...": ext is silent on this. Its three conditions (available, waited, shipped) define only when the count is taken. The base condition is **inherited**, but it has no structured eligibility and no recorded state (G2).
- "A replacement set is issued only while the document is still issued": **Inherited.**
- bol_cargo_release "the other originals of the set still outstanding are recorded as void": those rows fall inside ext's `voided_total`. **Consistent.**

**bol_ext_telex_full_set_surrender** (ref bol_telex_release; `overwrite: []`)
- "It is offered only on tiers whose telex_release_available is true": **Follows**, encoded.
- "Only the documentation party holding the record may request a telex release": **Follows.**
- "**The request is registered first and waits for the shipper, who alone can hand in the originals.**" against ext "For a telex release **the documentation party** surrenders at the origin office the full set of originals still in circulation". The two sentences govern who performs the action this policy binds, which is the `owner=user` surrender whose count it scores. They name different parties whenever the documentation party is not the shipper. The schema allows exactly that case: `bills_of_lading.customer_id` is the "documentation party that holds the record, normally the shipper or its forwarder". Base itself keeps the two roles apart (bol_draft_and_approval: "A draft is approved by the shipper, which only the shipper can do ... the documentation party may have the draft corrected"). The base `lifecycle` transition says "issued -> surrendered by user: The shipper surrenders the full set", and so does event `bol_originals_surrender_completed`. **Handled differently, and not named in `overwrite` (`overwrite: []`) — an undeclared override (G1).**
- "A telex release is effected only after the full set of originals has been surrendered at the origin office, so that originals_outstanding is 0": ext's count is exactly the in-circulation balance. **Follows.**
- "The surrender is recorded as originals surrendered at origin_office for the set in force, and the document moves to surrendered": **Follows** (tool).

**bol_ext_telex_release_fee** (refs bol_telex_release, bol_cargo_release; `overwrite` declared)
- "except when the documentation party holds an active service contract whose tier rank is at least ..." is superseded by "the service contract under which the booking is rated, named by the booking's contract_id". **Declared**, and the replaced clause is quoted verbatim from base. The merged semantics is unique: a single contract row is selected by `booking.contract_id` plus `status = active`.
- "A telex release fee of telex_release_fee_usd is charged to the documentation party": **Follows.**
- "booked only on a document whose status is surrendered": **Follows**, encoded as `effected`.
- "A release request is charged at most once": **Inherited.**
- bol_cargo_release: nothing in it governs the telex fee. **N/A.**

No author note calls a base output a "wrong value" or "the algorithm to avoid". I found no anonymous intermediate factor, no 0/1 multiplier and no dropped branch. The two readings of the zero branches are counterfactual and are listed as O5.

### findings

**G1 — undeclared override of who surrenders the originals for a telex release (check 1; SOURCE-POLICY where a task demonstrates it).**
- Symptom: the extended text and the base text name different parties for the same act.
- Root cause: `bol_ext_telex_full_set_surrender.rule` reassigns the surrender to the documentation party with `overwrite: []`.
- Evidence:
  - base `bol_telex_release.rule`: "The request is registered first and waits for the shipper, who alone can hand in the originals."
  - base `lifecycle.transitions` issued->surrendered: "The shipper surrenders the full set of originals at the origin office."
  - base `events[bol_originals_surrender_completed].meaning`: the same sentence.
  - ext `bol_ext_telex_full_set_surrender.rule`: "For a telex release the documentation party surrenders at the origin office the full set of originals still in circulation".
  - `task_tools.surrender_full_set_at_origin_68a55055` docstring: "The documentation party surrenders the full set".
  - Base keeps the roles apart elsewhere (`bol_draft_and_approval`).
- Affected artifact and location: `bol.extended.yaml` extended_policies[bol_ext_telex_full_set_surrender].rule / overwrite; the tool docstring.
- Bears on: every task whose documentation party differs from the printed shipper and whose GT includes the owner=user full-set surrender. The demonstration against a world belongs in that task's file (task 1).

**G2 — the letter-of-indemnity / bank-guarantee act that gates a lost-original reissue has no record state and no customer tool (check 1 / check 5 material).**
- Symptom: whether that act has been done cannot be read from any record.
- Root cause: the gate exists only in rule prose. `bol_service_requests.outcome` has no value for "customer act done, line not yet executed", and `bol_ext_lost_original_void_count` says nothing about the gate.
- Evidence:
  - base `bol_lost_original_reissue.rule`: "The request is registered and waits for the documentation party, who alone can sign the letter of indemnity and deliver a bank guarantee of reissue_bank_guarantee_pct_of_cargo_value percent of the declared_cargo_value_usd". Its `eligibility` lists only `waiting_period` and `reissue_while_issued`.
  - `db_schema.bol_service_requests.outcome`: values `awaiting_customer_action | completed | withdrawn | declined`, meaning "awaiting_customer_action until the customer signs, surrenders or approves as the request requires".
  - `task_tools.py` has no owner=user tool for signing the LOI or delivering the bank guarantee.
  - The blueprint summary for this difficulty says "signing a letter of indemnity or bank guarantee belong to the customer and are handed over as the customer's own actions".
- Consequence: before the reissue tool completes the request, the only record state available is `awaiting_customer_action`, which by its own schema meaning says that the signing has not happened. So the fact "LOI signed and BG delivered" can come only from a persona line.
- Affected artifact and location: base `bol_lost_original_reissue` (eligibility), `db_schema.bol_service_requests.outcome`, `task_tools.py` (no tool), extended_policies[bol_ext_lost_original_void_count].rule.
- Bears on: every task whose GT executes `reissue_lost_originals_set_197b224c` on a request whose outcome is `awaiting_customer_action` (task 1). The demonstration is in that task's file.

**Observations (no consequence demonstrated at charter level; tasks re-examine them against their worlds):**
- O1: the DSL's `CFIELD` silently adds `customer_id = <documentation party>`. So "the booking the document covers" (ext 1, 3, 4, 5, 6), "the booking record" (ext 2) and "named by the booking's contract_id" (ext 6) are read only when that booking or contract is held by the documentation party. The rule text does not carry this restriction. If a forwarder documents a cargo owner's booking, compute gives `booking_status='none'` and returns 0 (or not exempt), while the rule gives the count (or the exemption).
- O2: `RND` is Python banker's rounding on floats. The rules say "rounded half up". With tier fees that are exact to 2 decimals there is no difference.
- O3: E3's `gate: bol_ledger.request_id` is not an eligibility id. The gate is carried only by the quotable rule sentence.
- O4: `bol_ext_lost_original_void_count` anchors the waiting period to the *latest* lost-original request. Base anchors it to "the loss request" being executed.
- O5: `bol_ext_corrected_set_issue` and `bol_ext_lost_original_void_count` define a zero-count branch for states in which base forbids the action at all ("issued only when" / "issued only from"). A literal reader could take the branch as permission to issue a set with 0 originals, or to void nothing. The branch cannot be reached under the inherited base gates.
- O6: `bol_ext_post_departure_correction_fee` encodes the non-return-tier exclusion as a 0 result but has no branch for the keying-error exclusion. Relatedly, `bol_ext_corrected_set_issue`'s "fee already booked" gate is undefined when no fee is due (a keying-error correction).
- O7: workflow step `base_policy_refs` are subsets of the computing policy's refs. Step 0 omits bol_issuance, and step 3 omits bol_issuance.
- O8: `order_rationale` of the workflow asserts "the lodgement is the party's own act at the desk". That is a claim about the world. It holds only where the documentation party and the originals are physically at the origin office in the same contact. It is re-verified in the file of the task that claims the workflow.
- O9: the blueprint claim lists event types that no extended policy or task tool touches: bol_draft_created, bol_draft_reopened, bol_issued, bol_issuance_fee_charged, bol_switch_fee_charged, bol_voided, bol_fee_waived, bol_payment_received, bol_cargo_released and bol_delivery_release_recorded. Base still governs them. No relationship of this audit requires them to be instantiated.

## closing_checklist

Written after both reveals, at 2026-09-13T05:16Z. Everything above this heading is the pre-reveal charter-global section and was not changed after the reveal, except the freeze-time stamp, which is annotated where it appears.

**Status: the difficulty does NOT pass the source-layer audit.** Step 4 closes a difficulty only when every task passes all three relationships. Neither task does.

| task | policy self-consistency | problem tree holds | unique solution | file |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (check 5/6 zero-wait, F0-1) | SOURCE-CHAIN RED (F0-1) | SOURCE-TASK RED (F0-1) | `0.md` |
| 1 | SOURCE-POLICY RED (G1 → F1-1) | PASS under the persona reading; conditional on F1-2 | SOURCE-TASK RED (G2 → F1-2) | `1.md` |

In both tasks my independent derivation matched GT on every scored argument, owner and order under the reading GT adopts. Task 0: lodge 3 → apply → fee 150.00 → set 2 with 3 originals. Task 1: void 1 / set 3 / 3 originals / reissue fee 350.00 → surrender 3 of set 3 → telex fee 55.00. None of the REDs is an arithmetic or formula disagreement. Each one is a second defensible reading, or a real-world wait, that the artifacts leave open.

Items of the Step 4 checklist that can be verified regardless of the verdict:
- Audit files correspond one to one with the tasks (`0.md`, `1.md`), with `_difficulty.md` beside them. This is revision_1; no earlier revision exists. Each comparison section carries its verdicts, and the verdicts are not PASS.
- Coverage of extended policies:
  - Task 0 `charter_scope` = {correction_originals_return, post_departure_correction_fee, corrected_set_issue} + the workflow + 4 tools.
  - Task 1 `charter_scope` = {lost_original_void_count, telex_full_set_surrender, telex_release_fee} + 3 tools.
  - All 6 extended policies, the single workflow and all 7 task tools are covered.
  - The two scopes are pairwise disjoint, and each spans its whole problem tree (root and prerequisites).
  - Exactly one workflow exists, and exactly one task (task 0) claims it. This matches the pre-reveal expectation in § policy_conflict_scan.
- Each task tool has an independently generated, frozen uuid8 (§ action_binding_and_uuids).
- Each task's problem tree has 2 prerequisites, at least 1 value_input edge (task 0: 1; task 1: 2) and no cycle. The union of both tasks' `prerequisite` edges (E1–E5) is still a DAG. The two components share no node, so no cycle arises from cross-task references.
- Instantiation gates on the final form: I did not re-run them, per Step 0. The artifacts are byte-identical to the coordinator's gated form: at close, `bol.extended.yaml` = `a5aafd94…d1b7` and `task_tools.py` = `743f7e9e…9689`, unchanged. `tasks/0.json` = `f2a138bb…e59a` and `tasks/1.json` = `95a0f7d6…c190` were recorded at close. The coordinator's all-green snapshot therefore applies to the final form. A green gate does not change any verdict above.

Post-reveal charter-level observations. These are derived from the charter alone, but I noticed them only because GT text invoked them, so I disclose that here and keep them out of the pre-reveal section:
- **O10.** Base `bol_lost_original_reissue.eligibility.waiting_period` lists `bol_set_replaced` in `applies_to`. `bol_set_replaced` is also the subject of the correction path (`bol_correction` / ext `corrected_set_issue`). The structured scope therefore extends a loss-report waiting period to corrected sets, where the anchor event ("the loss of the originals was reported") does not exist. Task 0's GT applies it, anchored on the correction request's created_at. In task 0 it passes under both readings (2026-09-03 + 7 = 2026-09-10 ≤ 2026-09-11), so no consequence is demonstrated.
- **O11.** Base `bol_cargo_release.eligibility.loi_after_discharge` lists `bol_release_fee_charged` in `applies_to`. That subject is shared by the telex fee (`bol_telex_release` / ext `telex_release_fee`), while the condition is about release against a letter of indemnity. Task 1's GT applies it to the telex fee and adds an unscored `find_dnd_free_time` read. In task 1 it passes under both readings (2026-09-09 + 3 = 2026-09-12 ≤ 2026-09-14), so no consequence is demonstrated.

Not in scope here, and not run: the cross-difficulty merge surface and the scenario-level checks.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Auditor: the same independent auditor. The revision_1 text above is left untouched.
- Both shared inputs changed, so every charter-global section is re-derived in full:
  - `bol.extended.yaml`: `a5aafd94…d1b7` → `74890b86e93e141dd756a9bdc7817eb87ba299dd18edcb8889419c1527b49d58`
  - `task_tools.py`: `743f7e9e…9689` → `aa95c24d192a5c90cbc11d216626e7e785eec2862a82f7490f2ca0ade070eb2b`
  - Both were recomputed by me and match the brief and `source_r2/HASHES.txt`.
- The blueprint is unchanged since round 1: every file under `blueprint/` has an mtime of 03:20Z or earlier, before round 1 began. The base section is still a verbatim copy: `head -n 1010` diffed against `products/bol.yaml` gives only the trailing blank line.
- Entry conditions: the coordinator's round-2 gate block ran on the reworked files and every gate exited 0. `check_traceability` is deferred.
- Reworker claims were received by item id only. I treated them as unverified.
- Permitted reads were the same as in round 1, now on the new files. I did not open `tasks/*.json` before this section was frozen, and nothing below is derived from a round-2 GT. The masked views `source_r2/0.masked.json` (`7dd6e57b…d49c`) and `source_r2/1.masked.json` (`fadde55d…ee7a`) were read. They matter here only where a world is cited to show that an observation has no consequence.

### policy_conflict_scan (revision_2)

| id | subject | computes | target_tool (owner) | prerequisite | change vs r1 |
| --- | --- | --- | --- | --- | --- |
| bol_ext_correction_originals_return | bol_originals_surrendered | originals_count | return_originals_for_correction_b9bd03b3 (user) | [] | now a whole-history balance; new "latest correction request awaits" gate; presence at origin office written into the rule; explicit booking scoping; refs drop bol_issuance |
| bol_ext_post_departure_correction_fee | bol_correction_fee_charged | amount_usd | charge_correction_fee_18211c73 (agent) | state_gate → correction_originals_return | explicit scoping; keying error now out of scope; rounding sentence changed |
| bol_ext_corrected_set_issue | bol_set_replaced | originals_count | issue_corrected_set_a7062696 (agent) | value_input → correction_originals_return; state_gate → post_departure_correction_fee | keying-error case for the fee gate; zero-branch disclaimer; scoping; refs drop bol_issuance |
| **bol_ext_issuance_originals_count** (new; replaces bol_ext_lost_original_void_count) | bol_issued | originals_count | **issue_document_with_originals_c9d717be** (agent, new) | [] | new surface |
| bol_ext_telex_full_set_surrender | bol_originals_surrender_completed | originals_count | surrender_full_set_at_origin_68a55055 (user) | value_input → **issuance_originals_count** (was lost_original_void_count) | the surrendering party is now the printed shipper; tool gains `request_id` |
| bol_ext_telex_release_fee | bol_release_fee_charged | amount_usd | charge_telex_release_fee_be5da3ed (agent) | value_input → telex_full_set_surrender | scoping and rounding text only |
| workflow bol_wf_post_issuance_correction_with_originals_back | 4 steps (unchanged tools) | — | — | [] | scenario and order_rationale now require the party to have the originals at the origin office |

Overlapping subjects:
- `bol_set_replaced` is now written only by ext `corrected_set_issue`. The lost-original path has no extended policy any more; base `bol_lost_original_reissue` still governs it.
- `bol_issued` is written only by the new ext `issuance_originals_count`.
- `bol_originals_surrendered` is written by the correction lodgement (ext 1) and, through its trigger, by the telex surrender (ext 5). The two are still told apart by the request and the tool.
- No new conflict among triggers, eligibility, time anchors, terminal states or cross reads. The new booking scoping is declared in rule text.

Expected scope partition, from the worlds only: {ext 1, 2, 3 + workflow + 4 tools} and {ext issuance, 5, 6 + 3 tools}. The scopes are disjoint and together cover all 6 extended policies and all 7 tools. They are verified post-reveal.

### rule_compute_equivalence (revision_2)

- **ext 1 (`correction_originals_return`)**:
  - The whole-history `SUM`s are quoted, and so is `MX(…,0)` ✓.
  - `latest_request_outcome = LATEST(bol_service_requests, outcome, date_field=created_at, request_type=correction)` is quoted ("the correction request most recently registered") ✓. `request_awaiting` is quoted ✓.
  - Booking scoping is now in the rule ("a booking held by another customer is not read and counts as not shipped") ✓, which closes O1 for this policy.
  - The claim "an earlier set is always fully returned or voided before the next set is issued" is a world assertion and is checked per task.
  - The presence condition ("during a contact in which that party has them at the origin office") is a permission condition with no compute binding. That is correct: it is not a value.
- **ext 2**:
  - Unchanged compute. The rule now states scoping, so O1 is closed here.
  - Keying-error corrections are declared outside the policy ("books no row here"), so O6's first half is closed.
  - The rounding sentence is now "every tier amount is already a whole number of cents, so no rounding arises". I verified this against `variants`: every `correction_fee_*` value ends in `.00`. So `RND` is exact and O2 is closed for this policy.
- **ext 3**:
  - Unchanged compute.
  - The keying-error case of the fee gate is now defined ("the second fact is met without a fee row"), which closes O6's second half.
  - A zero-branch disclaimer is added ("A zero never permits a corrected set to be issued while originals are outstanding"), which closes O5 for this policy.
  - Scoping is stated, which closes O1.
- **ext `issuance_originals_count` (new)**:
  - doc_status, approved, per_set, booking_status, shipped and result are each quoted ✓.
  - "on a tier whose originals_issued_count is zero no originals exist" is carried by `per_set` = 0 ✓.
  - "The prepaid-freight hold of bol_issuance decides whether the document may be issued at all and does not change the number" has no binding. That is correct: the hold is inherited as base eligibility `prepaid_settled`.
  - The zero-branch disclaimer is present.
  - Reverse sweep: no invented basis and no empty promise.
- **ext 5**:
  - Compute unchanged. It is a whole-history balance with a telex tier and shipped gate.
  - The new party rule ("surrendered ... by the shipper printed on the document ... otherwise the request waits for the shipper") is a permission condition with no binding. The sentence "A document that has not yet been issued has no originals in circulation" is carried by `in_circulation` = 0 before issuance ✓.
- **ext 6**: compute unchanged. Scoping of the booking and contract reads is now in the rule, which closes O1. The rounding sentence closes O2 (`telex_release_fee_usd` values all end in `.00`). The rank table still matches `contract.yaml` ranks 1–6 ✓.

Result: **PASS**. Observation O13 is new; see findings.

### action_binding_and_uuids (revision_2)

- The six `(target_tool, computes)` pairs are distinct. `apply_particular_correction_a24e9121` is still workflow-only.
- New tool `issue_document_with_originals_c9d717be` (task_tools.py:158–199):
  - It moves the document to `issued`, dates it today, books one `bol_issuance_fee_charged` row for the set in force (fee as given) and one `bol_originals_issued` row, and raises `originals_outstanding` and `charges_due_usd`.
  - It checks nothing. It matches base `bol_issued` and its two triggers.
  - Docstring vs body: the docstring says originals are recorded "when the given number of originals is above zero", but the body creates the `bol_originals_issued` row unconditionally, including with count 0. That also departs from base's trigger `when: {variant_name: {not: AHL Sea Waybill}}`, since a waybill issued through this tool with 0 would still get a 0-count row. This is O14, with no consequence where the tier has originals.
- `surrender_full_set_at_origin_68a55055` now takes `request_id` and records it on the surrender row. Its docstring now reads "The shipper printed on a transport document surrenders" and matches ext 5.
- `charge_correction_fee_18211c73`'s docstring no longer says "rounded half up".
- No tool body contains a refusal, an error return or a precondition. I read all seven.
- uuid8 tails: b9bd03b3, a24e9121, 18211c73, a7062696, **c9d717be**, 68a55055, be5da3ed. All distinct. The new one shares no stem with the others and is not a sequence or adjacent value. The removed `197b224c` is not reused. **PASS.**

### prerequisite_graph (revision_2)

- E1, E2, E3 and E5 are unchanged (see revision_1 table): policy_source is verbatim, resolved_by holds, kind matches, and E3's gate label is still `bol_ledger.request_id` (O3 persists).
- **E4′** telex_full_set_surrender → issuance_originals_count:
  - kind value_input, gate `in_circulation`, which is a binding of the dependent ✓.
  - policy_source is verbatim in the dependent's rule: "A document that has not yet been issued has no originals in circulation, so the full set can be surrendered only after the document has been issued under bol_issuance and its originals put into circulation." ✓
  - The condition restates it ✓.
  - resolved_by `issue_document_with_originals_c9d717be` writes the originals-issued row, so in_circulation goes from 0 to `originals_issued_count` ✓.
- Every node's `prerequisite` field is filled in, with [] for ext 1, ext issuance and the workflow. No edge points at a base policy or at itself. There is no authoring-viewpoint wording.
- Components: {ext 1 < ext 2 < ext 3} and {issuance < ext 5 < ext 6}. They are disjoint, and the graph is a DAG.
- **PASS.** O3 persists.

### override_declarations (revision_2)

Sentence-by-sentence, per extended policy against its refs. Only the sentences that changed or are new are listed; every other sentence is as concluded in revision_1.

- **ext 1** (refs bol_correction, bol_telex_release, bol_cargo_release):
  - Whole-history balance vs base "every outstanding original": they agree under the closed-set invariant. **Follows.**
  - "Originals are lodged for the correction request most recently registered on the document, and only while that latest correction request still awaits the customer". Base `bol_correction` ties the return to *a* correction request on file and has no "latest" notion. The two differ only when an older correction request awaits while a newer one is completed, withdrawn or declined: ext lodges 0, and its own zero disclaimer then blocks the older request, whereas base would take the originals back for it. This is a **narrowing that base does not state**. Its consequence needs such a world (O13).
  - "lodged back ... by the documentation party holding the record": base `bol_telex_release`'s "the shipper, who alone can hand in the originals" sits in the telex request's sentence, and base `bol_correction` names no returning party. The two readings differ only if a forwarder documentation party returns originals for a correction. This is the same latent shape as G1, now on the correction path. **It was not raised in revision_1**; I record it now as O12 and disclose the omission.
- **ext 2 / ext 3**: the keying-error sentences now defer to base "never charged" consistently. **Follows.** No other change.
- **ext `issuance_originals_count`** (ref bol_issuance):
  - "An approved document is issued once the cargo has been shipped on board": **follows**.
  - The shipped_on_board gate: **follows** (the same status set).
  - "puts originals_issued_count originals of the set into circulation" on every tier except the Sea Waybill: ext's tier value, with 0 for the waybill. **Follows.**
  - "Issuance charges issuance_fee_usd once for the set": the tool books it, and ext does not restate it. **Inherited.**
  - The prepaid hold: explicitly **inherited**.
  - Service standard, fee-on-issued and set-charged-once: **inherited.**
  - No conflict.
- **ext 5** (ref bol_telex_release):
  - "The request is registered first and waits for the shipper, who alone can hand in the originals" against ext "surrendered at the origin office by the shipper printed on the document, who alone can hand in the originals; ... otherwise the request waits for the shipper". **Now follows base.**
  - The added identification rule (the documentation party counts only "when that party is the shipper printed on the document") does not say how the match is made: exact `company_name` = `shipper_name`, or otherwise. This is O15. There is no consequence where the strings are identical.
- **ext 6**: the declared override is unchanged and correctly quoted.

### findings (revision_2)

Status of the revision_1 charter-global items, each verified on the new files:

| item | r1 status | r2 verdict | evidence |
| --- | --- | --- | --- |
| G1 | undeclared override (who surrenders) | **CLOSED** | ext 5 now matches base: "by the shipper printed on the document, who alone can hand in the originals". The tool docstring agrees. The per-task demonstration is re-run in 1.md revision_2. |
| G2 | LOI/BG gate has no record state or tool | **Latent, no extended path** → observation | `bol_ext_lost_original_void_count` and `reissue_lost_originals_set_197b224c` are removed. No extended policy, workflow step or task tool reaches `bol_lost_original_reissue` any more. Base and schema are unchanged, so the gap persists in the blueprint but no task can demonstrate it. |
| O1 | CFIELD scoping unstated | **CLOSED** | every extended rule now states "the booking record held by the documentation party of the document; a booking held by another customer is not read". Ext 6 says the same for the contract. |
| O2 | RND vs half-up | **CLOSED** | rule text now says no rounding arises. All relevant tier amounts end in `.00`. |
| O3 | E3 gate label is not an eligibility id | **persists** (explanation only) | the label is unchanged. The edge is still quotable and bears weight through permission. Observation. |
| O4 | "latest" anchor on reissue waiting | **MOOT** | the policy was removed. |
| O5 | zero branch read as permission | **CLOSED** | ext 3 and the new ext issuance carry explicit "a zero never permits …" disclaimers. Ext 1 does too. |
| O6 | keying-error handling | **CLOSED** | ext 2 declares it out of scope; ext 3 defines the fee gate for it. |
| O7 | workflow step refs vs policy refs | **CLOSED** | step 0 refs = ext 1 refs; step 3 refs = ext 3 refs. |
| O8 | "at the desk" world assertion | **CLOSED at charter level** | the workflow scenario and order_rationale now require the originals to be at the origin office during the contact, and otherwise the request waits. The per-task truth is checked in 0.md revision_2. |
| O9 | claim event types uncovered | **persists** (explanation only) | this is a coverage note, not a relationship defect. |
| O10 | base `waiting_period` applies_to `bol_set_replaced` | **persists** (base frozen) | re-checked against task 0's world in 0.md revision_2. |
| O11 | base `loi_after_discharge` applies_to `bol_release_fee_charged` | **persists** (base frozen) | re-checked against task 1's world in 1.md revision_2. |

New observations (revision_2):
- **O12** (latent G1 shape on the correction path). Ext 1 has the documentation party lodge the originals for a correction. Base `bol_telex_release` calls the shipper the one "who alone can hand in the originals". It could bear only where the documentation party is not the printed shipper. Round 1 missed this; the rule text is unchanged in that respect.
- **O13.** Ext 1's "latest correction request awaits" gate narrows base when an older request is open behind a newer closed one.
- **O14.** Docstring vs body of `issue_document_with_originals_c9d717be` on 0-original rows (see action_binding_and_uuids).
- **O15.** The shipper-identity match in ext 5 is not specified.

None of O12–O15 has a demonstrated consequence at charter level. Each task file re-examines the ones its world touches.

**No new charter-global SOURCE-POLICY finding.**

### closing_checklist (revision_2)

This checklist was written after both round-2 reveals, at 2026-09-13T05:41Z. Everything in `revision_2` above this heading was written before those reveals.

**Status: the difficulty does NOT yet pass the source-layer audit.** Task 1 passes all three relationships. Task 0 fails the problem-tree relationship on one proof-level defect, F0-2. That defect is two stale `skipped_effect` sentences in `prerequisite_closure`. It changes no scored value.

| task | policy self-consistency | problem tree holds | unique solution | r1 REDs closed? | file |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | **SOURCE-CHAIN RED** (F0-2, new: false skipped-step figures in `prerequisite_closure.edge_load_bearing`) | PASS | F0-1 CLOSED | `0.md` § revision_2 |
| 1 | PASS | PASS | PASS | F1-1 CLOSED; F1-2 CLOSED (routed around) | `1.md` § revision_2 |

- **Round-1 REDs.** G1, F0-1, F1-1 and F1-2 are all genuinely closed, each verified on the new artifacts rather than on the reworker's claims. G2 is downgraded to a latent observation: the base clause and schema are unchanged, but no extended path passes through them.
- **Round-1 observations.**
  - Closed by edits: O1, O2, O5, O6, O7, O8.
  - Moot: O4.
  - Explanation only, and they persist as observations with no consequence: O3, O9, O10, O11.
- **Regressions.** None in the charter or the tools. The one regression is in task 0's proof text (F0-2), where round-1 figures were left in place after the world was extended.
- **New observations** (none with a demonstrated consequence): O12 through O15 at charter level, O16 in task 0, O17 in task 1. O12 is the correction-path twin of G1. It was present but unraised in round 1, which I disclose.
- **Step 4 items that can be verified now:**
  - One audit file per task, plus `_difficulty.md`. Revision_1 text is preserved, and revision_2 is appended in all three files.
  - Scopes: task 0 has {ext 1, 2, 3} plus the workflow and 4 tools; task 1 has {ext issuance, 5, 6} plus 3 tools. They are pairwise disjoint and together complete (6 policies, 1 workflow, 7 tools). Exactly one task claims the workflow.
  - uuid8s are independent and frozen; the new one is `c9d717be`.
  - Each tree has 2 prerequisites and at least one value_input edge (task 0: 1; task 1: 2), with no cycle. The union E1, E2, E3, E4′, E5 is a DAG with no shared nodes across tasks.
- **Gates.** I did not re-run them (Step 0). At close, the artifacts are byte-identical to the coordinator's round-2 gated form:
  - `bol.extended.yaml`: `74890b86…9d58`
  - `task_tools.py`: `aa95c24d…eb2b`
  - `tasks/0.json`: `d3a879a3…08f1`
  - `tasks/1.json`: `2da532bc…2a59`
  
  The all-green snapshot therefore applies to the final form.

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3, by the same independent auditor. Earlier revisions are left untouched.
- Both shared inputs changed again, so every charter-global section is re-derived in full:
  - `bol.extended.yaml`: `74890b86…9d58` → `46f75d0115b95d47391623257440307bef3e0e77575571445a0466b6b01f63e6`
  - `task_tools.py`: `aa95c24d…eb2b` → `fd6d809d73f7312a03907cfe5aa55fec0b375d7ea9c3dca36e77c0be3edb03a6`
  - Both were recomputed by me and match the brief and `source_r3/HASHES.txt`. For later rounds I kept private copies of both in my own scratchpad subfolder.
- The blueprint is unchanged: every mtime is at or before 03:20Z. The base section is still verbatim; `head -n 1010` against `products/bol.yaml` differs only by the trailing blank line.
- Gate block: the coordinator re-ran it on the reworked files, and every gate exited 0.
- Masking: this section was written before any round-3 GT was opened. Nothing below derives from round-3 GT.

### policy_conflict_scan (revision_3)

The node set is the same as in revision_2: 6 extended policies (`correction_originals_return`, `post_departure_correction_fee`, `corrected_set_issue`, `issuance_originals_count`, `telex_full_set_surrender`, `telex_release_fee`), 1 workflow and 7 tools, with the same `(target_tool, computes)` pairs. What changed in round 3:

- **ext 1 `correction_originals_return`:**
  - The lodging party is now "the shipper printed on the document, who alone can hand in the originals".
  - The documentation party is accepted "only when that party is the printed shipper, meaning that its registered company_name matches the document's shipper_name exactly, character for character, and otherwise the correction request waits for the shipper".
  - The "latest correction request awaits" gate is replaced by "only while at least one correction request on the document still awaits the customer, counted as the correction requests on file less those completed, withdrawn or declined".
  - Compute now uses three `COUNT` bindings in place of `LATEST`.
- **ext 5 `telex_full_set_surrender`:** adds the same exact-match definition of "the shipper printed on the document".
- **Workflow:**
  - `scenario` now requires "the shipper printed on the document, being the documentation party holding the record".
  - `order_rationale` now reads "The lodgement is the printed shipper's own act, taken from the documentation party only when it is that shipper".
  - Step 0's `role` text still reads "the documentation party lodges …" (O18).
- **ext 2, 3, issuance and 6:** unchanged from revision_2.
- **Tools:**
  - `return_originals_for_correction_b9bd03b3` docstring now says "The shipper printed on a transport document lodges its original bills of lading".
  - `issue_document_with_originals_c9d717be` now creates the `bol_originals_issued` row only `if int(originals_count) > 0`, and its Returns text mentions "none".
  - The other bodies are unchanged.

Overlaps: the subjects, triggers, time anchors, terminal states and cross reads are the same as in revision_2. The correction path and the telex path now name the same party in the same way (the printed shipper, identified by exact match), and that agrees with base `bol_telex_release` "the shipper, who alone can hand in the originals". I found no new conflict. The expected scope partition is unchanged and is confirmed post-reveal.

### rule_compute_equivalence (revision_3)

- **ext 1:**
  - `requests_on_file = COUNT(correction)`, and `requests_closed` sums the three `COUNT`s by outcome (completed, withdrawn, declined).
  - `request_awaiting = on_file − closed > 0`. Its basis is quoted verbatim ("counted as the correction requests on file less those completed, withdrawn or declined") ✓.
  - `db_schema.bol_service_requests.outcome` has exactly four values (awaiting_customer_action, completed, withdrawn, declined). So on_file − closed is exactly the number of awaiting requests. The subtraction reading and the "still awaits the customer" reading cannot diverge ✓.
  - The whole-history balance, the shipped test, the tier and the int conversion are unchanged ✓.
  - The shipper-identity and presence conditions are permission conditions and carry no binding. That is correct.
  - The reverse sweep finds no invented basis.
- **ext 5:** the exact-match sentence is a permission condition. The compute is unchanged ✓.
- **ext 2, 3, issuance, 6:** unchanged from revision_2 and PASS.

**Result: PASS.**

### action_binding_and_uuids (revision_3)

- The six `(target_tool, computes)` pairs are still distinct.
- `issue_document_with_originals_c9d717be`: the docstring ("when the given number of originals is above zero, records those originals") now matches the body (`if int(originals_count) > 0:`). This also matches base's trigger `when: {variant_name: {not: AHL Sea Waybill}}` for the 0-original tier. The `if` checks the shape of the argument; it is not a business precondition, and the tool still writes whatever it is given.
- None of the seven bodies contains a refusal, an error return or a precondition check.
- The uuid8s are unchanged (b9bd03b3, a24e9121, 18211c73, a7062696, c9d717be, 68a55055, be5da3ed): distinct and independent.

**Result: PASS.**

### prerequisite_graph (revision_3)

- E1, E2, E3, E4′ and E5 are unchanged in kind, gate, condition, policy_source, resolved_by and effect.
- Every policy_source is still verbatim in its dependent's rule. I re-checked each after the rule edits.
- It is a DAG of two disjoint components.
- O3 (E3's gate label) persists.

**Result: PASS.**

### override_declarations (revision_3)

- **ext 1**, against `bol_telex_release` "The request is registered first and waits for the shipper, who alone can hand in the originals": ext now has the printed shipper hand in the originals for a correction, otherwise waiting for the shipper. **Follows.** Base `bol_correction` names no returning party, so there is nothing to conflict with. Base `bol_telex_release` "Only the documentation party holding the record may request ... a correction" governs who requests. ext 1 governs who lodges, and it leaves requesting untouched. **Consistent.**
- **ext 1**, against `bol_correction` "the correction is applied only after every outstanding original has been returned": ext now lodges whenever any correction request awaits, instead of only for the latest. This no longer narrows base in the older-open-behind-newer-closed case. **Follows.**
- **ext 5**, exact match: base does not say how "the shipper" is identified. Ext's rule (registered `company_name` equals `shipper_name` exactly) is a definition that adds precision, and it is consistent with the base's own exact-match convention for the consignee in `bol_cargo_release`. **Addition; no conflict.**
- **Other policies:** as concluded in revision_2. ext 6 still declares its override correctly.

### findings (revision_3)

Charter-level status of the items open after revision_2, each verified on the new files:

| item | r2 status | r3 verdict | evidence |
| --- | --- | --- | --- |
| O12 (latent G1 shape on the correction path) | observation | **CLOSED** | ext 1 now names the printed shipper as the lodging party, accepts the documentation party only by exact match, and otherwise waits. The tool docstring and the workflow scenario and order_rationale agree. |
| O13 (latest-request narrowing) | observation | **CLOSED** | the gate is now "at least one correction request ... still awaits the customer". |
| O14 (docstring vs body on 0-original rows) | observation | **CLOSED** | the body now matches the docstring. |
| O15 (shipper match unspecified) | observation | **CLOSED** | "registered company_name matches the document's shipper_name exactly, character for character" now appears in ext 1 and ext 5. |
| O3, O9, O10, O11 | observations | persist, unchanged | no consequence in either world (re-checked per task) |
| G2 | latent | latent, unchanged | there is still no extended path through `bol_lost_original_reissue`. |
| G1, O1, O2, O4–O8 | closed/moot in r2 | **still closed** (no regression) | the relevant text is unchanged or strengthened |

- New in revision_3, **O18**: workflow step 0's `role` still says "the documentation party lodges the outstanding originals of the set in force at the origin office". ext 1, the tool docstring and the workflow `scenario` now say "the shipper printed on the document", with the scenario adding "being the documentation party holding the record". Within the workflow's own scenario the two parties are the same company, so the step text reaches the same result there. I found no demonstrable consequence, so this is an observation only.
- **No charter-global SOURCE-POLICY finding.**

### closing_checklist (revision_3)

Written after both round-3 reveals, at 2026-09-13T05:51Z.

**Status: the difficulty PASSES the source-layer audit.** Both tasks pass all three relationships.

| task | policy self-consistency | problem tree holds | unique solution | open RED | file |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | none (F0-2 closed) | `0.md` § revision_3 |
| 1 | PASS | PASS | PASS | none | `1.md` § revision_3 |

**Round-2 RED and observations:**
- F0-2 is closed. I verified its figures by replay on the unchanged world rather than taking the reworker's claim.
- O12, O13, O14, O15 and O17 are closed by edits.
- O16 has no edit. Its two readings reach the same outcome, so it has no consequence.

**No regression.** Every item closed in revision_1 and revision_2 is still closed, and the relevant text is unchanged or strengthened: G1, F0-1, F1-1, F1-2, O1, O2, O4–O8.

**Observations that remain, none with a consequence:**
- O3: E3's gate label is not an eligibility id.
- O9: event types claimed but not instantiated.
- O10 and O11: base structural `applies_to` reach. The base is frozen, and both pass under either reading in their worlds.
- G2: latent, with no extended path.
- O16: the base measure anchor.
- O18: workflow step 0 role text still says "documentation party". It is equivalent under the workflow's own scenario.
- O19: an unverifiable history-consistency sentence in task 0's rationale.

**Step 4 checklist:**
- Audit files correspond one to one with the tasks, with `_difficulty.md` beside them. revision_1 through revision_3 are preserved in order. Each round-3 comparison carries a PASS.
- Extended-policy coverage is complete: 6 policies, 1 workflow, 7 tools. Task 0 = {ext 1, 2, 3} + the workflow + 4 tools. Task 1 = {issuance, ext 5, ext 6} + 3 tools. The two sets are pairwise disjoint, and each scope spans its whole tree. Exactly one workflow exists, and only task 0 claims it.
- The tool uuid8s are independent and frozen.
- Each tree has 2 prerequisites and at least 1 value_input edge (task 0: 1, task 1: 2), with no cycle. The union E1, E2, E3, E4′, E5 is a DAG.
- Instantiation gates: the coordinator's round-3 block was all green, and I did not re-run it. At close the artifacts are byte-identical to that gated form: `bol.extended.yaml` `46f75d01…63e6`, `task_tools.py` `fd6d809d…03a6`, `tasks/0.json` `57214ea4…da21`, `tasks/1.json` `b0117d9f…eb8b`. `check_traceability` stays deferred until the KB is published.
