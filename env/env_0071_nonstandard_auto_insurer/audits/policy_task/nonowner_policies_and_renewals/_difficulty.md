# Policy-task audit — nonowner_policies_and_renewals / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-18T10:48Z (written before any task GT was revealed; nothing below is derived from a revealed GT field).
- Auditor: erl-task-policy-audit (independent of the instantiator; no answer supplied by the coordinator; the brief carries no scored value).
- Inputs and hashes (re-computed by the auditor, equal to the brief):
  - `tasks/nonowner_policies_and_renewals/nonowner.extended.yaml` sha256 67df3e94088355113ef3aee1b00771f127fa9c075ee2bf090e3870e99a0d719a
  - `tasks/nonowner_policies_and_renewals/task_tools.py` sha256 1fc353ab76b6c6e4414e00a04640be65ca109c7bfc19642dbe63dd91b484a9cc
  - masked views `.audit_views/policy/nonowner_policies_and_renewals/r1/0.masked.json` 484da923…3e67 and `1.masked.json` 5263df84…86c1 (keys kept: frozen_time, user_scenario, initial_state).
- Permitted: blueprint.yaml, db_schema.json, share_tools.py, products/{nonowner,fr,billing,auto}.yaml, the extended charter, task_tools.py, the two masked views, the instantiate-stage DSL helper `skills/erl-task-instantiate/scripts/check_compute.py` (functions only, run on the masked worlds), audits/render_source/XF_recipe.md.
- Masked / not read: tasks/*.json, plan.md, the difficulty worklog.md, the scenario worklog.md, any other audit, any sibling difficulty tasks/, any other env/ scenario.
- Entry conditions (Step 0): gate snapshot `/tmp/erl0071_coord/snap_nonowner_policies_and_renewals_r1.txt` carries rc=0 lines for check_extended, check_task_tools, replay_tasks --check, check_solvability, check_compute, check_grounding, check_cross_fire; masked views and hashes supplied. Entry conditions complete.
- Base copy: lines 1-1889 of the extended charter are byte-identical to `blueprint/products/nonowner.yaml` (`diff` empty).

Policy ids used below: P1 `nonowner_ext_late_renewal_written` (book_renewal_written_premium_ed68a083, agent), P2 `nonowner_ext_insured_cancel_return` (cancel_nonowner_term_6aabad38, user), P3 `nonowner_ext_package_rerate` (change_nonowner_package_67dc97ad, user), P4 `nonowner_ext_renewal_offer_premium` (issue_nonowner_renewal_offer_23563ff0, agent), P5 `nonowner_ext_reinstatement_rewritten` (book_reinstatement_rewritten_premium_bf43cbc7, agent), P6 `nonowner_ext_package_increase_premium` (book_package_increase_premium_8b98e0ec, agent).

### policy_conflict_scan
- Subjects / targets: P1 nonowner_premium_written (lapse renewals only), P2 nonowner_cancelled_insured_request + its return, P3 nonowner_limits_changed (limits-rejection case only), P4 nonowner_renewal_issued (package-kept case only), P5 nonowner_additional_premium reason reinstatement (with-lapse case), P6 nonowner_additional_premium reason limits_increase. No two extended policies claim the same (event, case); P5 and P6 share the event type but are separated by transaction_reason and by P6's replaced_by ("a reinstatement still re-writes premium under the reinstatement rule").
- Time anchors: P1 handling = processing date (window "fewer than twelve whole months before the processing date"); P2 cancellation date = max(requested, received) as base; P3 change "takes effect on the day it is made"; P6 increase days from NOW, consistent with P3; P4 rating date = renewal effective date = expiring expiration_date, offer day = base offer_days. Compatible.
- Cross-category read boundaries: billing (late fees, returned payments, latest payment channel, term plan variant) and fr (filing status/form/required-through/end date/rejection) — reads only, no cross-category writes (XF14: every tool event's base `triggers` stays in nonowner: nonowner_cancelled_insured_request -> nonowner_return_premium, written by the same tool; all other written events have `triggers: []`).
- Cross-charter conflict found: P3 vs the fr base cure for a limits rejection — finding CG-1.
- Scope partition (from the worlds, pre-reveal): task 0's world exercises exactly {P1, P2}; task 1's world exercises exactly {P3, P4, P5, P6}. The two sets are disjoint and cover all six extended policies (to be compared with charter_scope after reveal).

### rule_compute_equivalence
- Scratch sweep (`/tmp/audit_…/s/sweep.py`, whitespace-normalised substring test): every `compute_basis` quote of all six policies is verbatim in its own rule (XF4 clean); every sentence of every `baseline.rule` is verbatim in its rule; every `prerequisite.policy_source` is verbatim in its own rule; every value_input `gate` names an existing compute binding (written_premium_on_term, expiring_package, rerated_premium_now, rewritten_on_term).
- Windows: "fewer than twelve whole months before the processing date, a month being complete on the same day of the following month" == DSL `_within` (0 <= MONTHS(posted, NOW) < 12, MONTHS decrements when day2 < day1). Ties: "on a tie the one recorded first" / "the one recorded first gives the days" == strict `>` in LATEST/XLATEST (first iterated row kept). Rounding: every rule's "rounded half up to the cent on the final figure only" == single RND at `result` (XF6 clean).
- Every ladder tier of every factor is a rule sentence and a branch of its `decides` binding, and vice versa (checked factor by factor). Rate-table date tests: "before 2026-06-01" == DAYS(date,'2026-06-01') > 0; "on or after 2026-11-01" == DAYS('2026-11-01', date) >= 0.
- Divergences (rule word != compute in some producible case): CG-8 (certificate selection unfiltered by form / first match) and CG-9 (P6 tier-2 zero-day record).

### action_binding_and_uuids
- Six policies, six target tools, six distinct `computes` (written_amount, return_amount, rerated_full_term_premium, renewal_full_term_premium, rewritten_amount, additional_amount): each (target_tool, computes) claimed once.
- uuid8s ed68a083, 6aabad38, 23563ff0, 67dc97ad, 8b98e0ec, bf43cbc7: pairwise distinct, no shared prefix/suffix, no sequence pattern.
- Docstrings: no ordering word positioning the action in a sequence (only "once the entry/return is counted", describing the returned balance), no other tool named, no concrete example value (formats/enums only); every effect claimed is in the body (XF7 clean). No body refuses, errors or hints on an unresolved prerequisite (no branch on state at all).
- Owners: cancel_nonowner_term and change_nonowner_package are owner=user ("Put into effect the named insured's own …"); the other four are agent.

### prerequisite_graph
| policy | edge | kind | form | resolved_by | gate exists |
|---|---|---|---|---|---|
| P1 | [] | | | | |
| P2 | <- P1 | value_input | state | book_renewal_written_premium_ed68a083 | written_premium_on_term |
| P3 | [] | | | | |
| P4 | <- P3 | value_input | state | change_nonowner_package_67dc97ad | expiring_package |
| P4 | <- P6 | state_gate | action (fallback_reason present) | book_package_increase_premium_8b98e0ec | — |
| P5 | [] | | | | |
| P6 | <- P3 | value_input | state | change_nonowner_package_67dc97ad | rerated_premium_now |
| P6 | <- P5 | value_input | state | book_reinstatement_rewritten_premium_bf43cbc7 | rewritten_on_term |

`prerequisite` filled on all six; every `problem` is an extended id of this file, none self, none base; graph acyclic (P1->P2; P5->P6; P3->P6->P4; P3->P4). `condition`s match the sentences' strength; each `resolved_by` is the depended-on target_tool and its body writes exactly the state named (premium-written row; variant_name + full_term_premium; additional_premium reason reinstatement; additional_premium reason limits_increase). No authoring-viewpoint phrasing (grep for "this task / at the opening / current world" empty).

### prerequisite_sentences
- P2: "The requested-cancellation return is fixed only after the term's premium ledger carries a premium-written entry for the term." — connective "only after"; state named in table words; no tool/id/snake_case; strength = condition. Writers of a nonowner_premium_written row in this module: only book_renewal_written_premium (body inspected) -> one write. Derivation: renewal term in_force with no premium-written row -> the policy whose rule books the premium written on a renewal that went in force after expiration (P1) -> its tool.
- P4 (state): "The renewal offer premium is not fixed until the expiring term carries a package whose limits meet the minimum limits of every state with which the named insured has an Operator certificate filed, requested or rejected." — "not … until"; state; only change_nonowner_package writes variant_name; P3's own rule pins the package (50/100/50). Single reading within this charter (but see CG-1 for the fr base's competing cure).
- P4 (action): "A renewal offer is not issued before the additional premium for a package raised during the expiring term has been booked." — "not … before"; action in business words; fallback_reason tested: the record that the write leaves (a limits_increase additional-premium row) cannot tell the reader that one is missing, because no record states that a raise happened; fallback accepted (observation O-5).
- P6: "The increase charge for a raised package is worked out only after the term carries the raised package and its re-rated full-term premium." and "The increase charge is not worked out until the term's premium ledger carries a re-written premium entry for every reinstatement with a lapse recorded on the term." — both state form, "only after"/"not … until"; writers unique (change_nonowner_package; book_reinstatement_rewritten_premium is the only writer of reason reinstatement).
- No depended-on rule restates a sentence; no rule carries a second wording, a tool name or another problem's id; no cross-problem order sentence that grounds no edge (P1, P3, P5 rules carry none). No base sentence grounds an edge.

### override_declarations
Sentence-by-sentence against `base_policy_refs` (finding half only):
- P1 vs nonowner_premium_charging: S1 (status) followed; S2 (premium = full_term_premium) declared overwrite with scoped replaced_by (XF5a clean); S3/S4 untouched. vs nonowner_renewal: issue/statement/payment/window/SNL/carry-forward followed; "goes in force on the posting date plus reinstatement_effective_offset_days, with the lapse recorded" contradicted by tier 2's "coverage was bound at the moment of payment" — undeclared (CG-7). vs nonowner_lapse_attestation: followed.
- P2 vs nonowner_insured_cancellation: signed request, no backdating, requested/received date followed; return sentence declared; conversion sentence inherited. vs nonowner_unearned_premium_return: status followed; retention sentence declared; transaction-by-transaction sentence declared but its replaced_by does not restate the still-in-force formula (CG-6); "credited to the billing plan within refund_issue_days" inherited.
- P3 vs nonowner_lapse_attestation: mid-term change sentence declared with scope and restated (clean). vs nonowner_eligibility: "A mid-term package change meets the same limits" inherited (not weakened). vs the fr charter's in-force cure: undeclarable contradiction (CG-1).
- P4 (`overwrite: []`) vs nonowner_renewal: base fixes no renewal premium, so pricing adds no conflicting quantity; issuance-day sentence followed (the added gates can only delay, observation O-12). vs agg_multi_holding / nonrenewal: followed. Base gives no premium for a re-tiered renewal that P4 hands back to it (O-10).
- P5 vs nonowner_reinstatement: re-written-premium sentence declared, without-lapse case restated (clean); other sentences inherited. vs premium_charging: followed.
- P6 vs nonowner_premium_charging: limits-increase sentence declared; the same sentence's non-conflicting reinstatement half is retired and restated (O-6).
- Disguised forms: no anonymous intermediate (every departure sits in a declared quantity), no 0/1 multiplier, no dropped base branch; no author note calls base output wrong.

### factor_ladders
| policy | factor | effect | decides | tiers | multi-source | cross_difficulty | method pair test (XF10) |
|---|---|---|---|---|---|---|---|
| P1 | lapse_length_load | param | lapse_length_load | 3 (>=6 / 3-5 / 1-2 d) | no | — | |
| P1 | late_fee_load | param | late_fee_load | 3 | no | billing | |
| P1 | returned_payment_load | param | returned_payment_load | 3 | no | billing | |
| P1 | certificate_form_load | param | certificate_form_load | 3 | no | fr | |
| P1 | lapse_exposure_days | method | late_renewal_charged_days | 3 | no (T1 single condition) | fr | T1 DAYS(eff,exp) vs T3 DAYS(lapse_end,exp)-1: FAIL (window start only); T1/T2, T2/T3 PASS (T2 data-selected start from billing) |
| P2 | requirement_relief | param | requirement_relief | 3 | yes (request reason x fr filing) | fr | |
| P2 | elapsed_term_scale | param | elapsed_term_scale | 3 | no | — | |
| P2 | advance_notice_credit | param | advance_notice_credit | 3 | no | — | |
| P2 | certificate_runoff | method | unearned_days | 3 | no | fr | T1 adds tariff params; T2 adds MX + cross-record date; all pairs PASS |
| P3 | 5 relativities (late, notice, return, lapse, certificate) | param | each its own | 3 each | no | billing x2, fr x1 | |
| P3 | rerate_rate_table | "method" | rerate_rate_table_rate | 3 | no | — | T1 K(spring_p50) / T2 K(winter_p50) / T3 K(summer_p50): every pair FAIL — constant substitution (CG-2) |
| P4 | 5 relativities | param | each | 3 each | no | billing x2, fr x1 | |
| P4 | offer_rate_table | "method" | offer_rate_table_rate | 3 | no | — | every pair FAIL (CG-2) |
| P5 | reinstatement_lapse_load | param | | 3 | no | — | |
| P5 | reinstatement_late_fee_load | param | | 3 | no | billing | |
| P5 | payment_default_load | param | | 3 | yes (term notices OR/AND billing returns) | billing | |
| P5 | reinstatement_certificate_load | param | | 3 | no | fr | |
| P5 | certificate_lapse_rewrite | method | reinstatement_rewritten_days | 3 | no | fr | T1 DAYS(cancel,exp) vs T3 DAYS(reinst,exp): FAIL (window start only); T2 adds subtraction of a cross-record span: PASS vs both |
| P6 | increase_unearned_basis | method | increase_before_loads | 3 | syntactically yes, but both operands of each test come from the same ledger rows (O-8) | — | T1 adds return + re-written inputs; T2 adds entry-days divisor; all pairs PASS |
| P6 | increase_short_term_load | param | | 3 | no | — | |
| P6 | increase_plan_credit | param | | 3 | no | billing | |
| P6 | increase_certification_load | param | | 3 | no | fr | realism RED (CG-4) |

Counts: P1 5 (4p/1m), P2 4 (3p/1m), P3 6 (5p/0 honest m), P4 6 (5p/0 honest m), P5 5 (4p/1m), P6 4 (3p/1m). Every factor's `decides` is an input, never `result`; bindings disjoint within each policy (sweep found no shared binding); every fall-through equals its baseline value/expression; no two tiers of a parameter ladder share a value. XF1: no factor reads another factor's binding (shared selections operator_certificate_on_file, cancellation_date, standard_unearned_days, days_from_reinstatement, days_from_in_force are plain bindings; P1 duplicates the certificate selection as two factor-owned reads, O-7). XF2/XF3: every policy states one generic combination sentence fixing order (replacement first, floor where present, then one combined multiplier, rounding last). XF9: ladders gap-free and disjoint on the real domain; P3's FR-44 certificate tier is reachable only through a re-tiered renewal (O-4). XF12: CFIELD/CPARAM keyed by exact values; P6 plan read keyed on nonowner_policy_id=HID. XF15: no factor id is a substring of a tool name. Stamp: `nonowner_policies.financial_responsibility_filing` (enum none/sr22/fr44, "state certificate the term is written to back") names the outcome of every certificate-form ladder and of every "Operator certificate on file" method tier — whether it agrees with the tier is a per-task fact (CG-5, demonstrated in the task files).

### findings
- **CG-1 SOURCE-POLICY RED — P3's cure contradicts the fr charter's in-force cure.** Symptom: two published clauses name different target packages for the same event. Evidence: P3 rule "the term is moved mid-term to the Cardinal Point Non-Owner 50/100/50 package"; fr base `fr_transmission` "A policy_limits_insufficient rejection is cured only by moving the backing term to the minimum backing package before retransmitting", with SR-22 Operator Certificate `minimum_backing_package_by_state: VA: Cardinal Point Non-Owner Minimum Limits` (fr.yaml, SR-22 Operator variant). Root cause: an extended nonowner policy contradicts another product's base clause, which no nonowner `overwrite` can retire (XF5d). Consequence: in a VA limits rejection of an SR-22 Operator certificate on a Minimum Limits term, the fr reading says the term is already at the minimum backing package (no package move is the cure), the P3 reading moves it to 50/100/50; terminal variant and every downstream premium differ. Bears on task 1 (demonstrated there).
- **CG-2 SOURCE-FACTOR RED — P3 `rerate_rate_table` and P4 `offer_rate_table` are mislabelled `method`.** Each tier substitutes a different constant base rate into the same formula (P3: 730 / 798 / 760; P4: the per-package spring/winter/standard constants). XF10 pair test fails for every pair; the skill's "a factor labelled method whose tiers only substitute a different number (a rate …)". With the label struck, P3 and P4 each carry 0 `method` factors (< 1). Bears on task 1.
- **CG-3 SOURCE-FACTOR RED — failing method pairs in P1 and P5.** P1 lapse_exposure_days T1 "days counted from the renewal term's effective date to its expiration date" vs T3 "from the in-force date": both are DAYS(start, expiration) over the same term row, differing only in the start (a window length). P5 certificate_lapse_rewrite T1 "days from the cancellation effective date to the expiration date" vs T3 "days from the reinstatement effective date": same. Two tiers of one ladder select the same method. Bears on task 0 (P1 realises T1 against baseline T3) and task 1 (P5 realises T1 against baseline T3).
- **CG-4 SOURCE-FACTOR RED (realism) — P6 `increase_certification_load`.** "follows the state that rejected the named insured's Operator certificate for insufficient limits: Virginia … carries 1.06, Texas, Georgia, Arizona or Ohio … carry 1.03". The quantity is the additional premium for raising the term to the same 50/100/50 package; its price is already fixed by the re-rated package premium (rate table x residence factor x points x relativities). Which state's DMV rejected the filing changes neither the limits bought nor the risk insured (the residence state already rates it); no carrier files an endorsement surcharge keyed on the rejecting state. Condition no business in the line weighs for that quantity. Bears on task 1.
- **CG-5 SOURCE-FACTOR RED (stamp, structural half).** The term field `financial_responsibility_filing` stamps the certificate form the certificate-form ladders (P1 certificate_form_load, P3 rerate_certificate_relativity, P4 offer_certificate_relativity, P5 reinstatement_certificate_load) select from, and the presence the method tiers P1 lapse_exposure_days T1, P2 certificate_runoff T1, P5 certificate_lapse_rewrite T1 test. Where the seed's stamp agrees with the tier the score cannot tell reading the stamp from reading the rule; demonstrated per task.
- **CG-6 SOURCE-POLICY RED (XF5a) — P2's replaced_by drops the still-in-force formula.** Retired: "each premium written and additional premium row multiplied by the days from the cancellation effective date to expiration and divided by that row's premium_days (term_days for premium written), less the same share of earlier returns …". Restated for out-of-scope cases only as "nonpayment, underwriting and conversion cancellations are still returned pro rata with no retention, transaction by transaction". Consequence: for a nonpayment cancellation of a term carrying an additional-premium row (e.g. after a reinstatement), the merged text gives two readings (each row over its own premium_days vs over term_days; earlier returns netted or not) and two return amounts. No task of this difficulty books such a cancellation; charter-only.
- **CG-7 SOURCE-POLICY RED (XF5f) — P1 T2 contradicts base nonowner_renewal.** P1: "coverage was bound at the moment of payment, so the late-renewal charged days run from that payment's posting date"; base: a late renewal "goes in force on the posting date plus reinstatement_effective_offset_days, with the lapse recorded". Same situation (no certificate, agent-channel payment): base puts the first covered day at posting+1, P1 at the posting date; no overwrite names the base sentence. Neither task reaches T2; charter-only.
- **CG-8 SOURCE-POLICY RED (XF8/XF11) — "Operator certificate" selection.** Rule: "the SR-22 or FR-44 filing of the named insured whose status is filed"; compute `CFIELD('fr', …, status='filed')` (P1, P2, P3, P4, P5) and `CFIELD('fr','certificate_end_date', status='cancellation_filed')` (P2, P5) filter neither to Operator forms nor state which certificate counts when two are on file (the fr charter allows one open filing per driver per state, so FR-44 FL + SR-22 VA can coexist on one non-owner term). Consequence: certificate-form ladders give 1.04 or 1.02 (P1), 1.15 or 1.04 (P3/P4), 1.05 or 1.03 (P5) by row order; an Owner certificate in cancellation_filed would drive P2/P5 tier 2 though the rule says Operator. Neither task world has two matching rows; charter-only.
- **CG-9 SOURCE-POLICY RED (XF8/XF11) — P6 tier 2 on a zero-day record.** Rule: "when there is no such re-written entry but the premium written records fewer days than the term's days, the charge is … less the premium written multiplied by the increase days and divided by its days"; every seeded new-business premium-written row records premium_days 0 (both worlds), so the literal rule divides by zero while compute (`written_days_recorded and …`) falls to tier 3. Not on task 1's gold path (tier 1 applies there); charter-only.

Observations (no demonstrated consequence): O-1 P2 advance_notice_credit (10+ days' notice cuts the short-rate retention) has no known industry counterpart, though a company could publish it. O-2 P3 re-rates mid-term with billing-history relativities counted at the processing date while its rate table is fixed at term inception — mixed rating basis. O-3 P1 T1 and P5 T1 charge premium for days recorded as lapse and stack a lapse load on top. O-4 P3 FR-44 tier reachable only via a re-tiered renewal. O-5 P4<-P6 action-form fallback accepted. O-6 P6 retires and restates the non-conflicting reinstatement half of its superseded sentence. O-7 P1's shared certificate selection is two factor-owned bindings (no cross-read). O-8 P6 increase_unearned_basis compound tests read one ledger's rows (not multi-source in substance; immaterial since task 1 carries P5's payment_default_load). O-9 P1 has no multi-source factor (task 0 relies on P2's requirement_relief). O-10 P4 hands re-tiered renewals to a base rule that prices nothing. O-11 fr follow-ups triggered by the writes (VA retransmission, SR-26) have no tool here — outside this difficulty. O-12 P4's gates may delay issuance past base's offer day.

## closing_checklist
Written after both reveals. Not closed: task 0 and task 1 carry RED verdicts.
- Per-task files 0.md, 1.md correspond one-to-one with tasks 0..1; _difficulty.md alongside; revision_1 is the first revision. Comparison sections: task 0 SOURCE-FACTOR RED; task 1 SOURCE-POLICY RED + SOURCE-FACTOR RED.
- Coverage and scope: charter_scope task 0 = {P1, P2}, task 1 = {P5, P3, P6, P4} — equal to the pre-reveal partition; disjoint; all six extended policies covered; task tools disjoint; uuid8s independent.
- Trees: task 0 one prerequisite, one value_input, owner=user root; task 1 three prerequisites, three value_input, owner=user P3; difficulty graph acyclic — holds.
- Factors: every computation's baseline is self-sufficient and gives a definite non-gold fall-back (1332.91, 1332.21, 972.80, 122.99, 95.14, 972.80); every declared factor moves its scored value; but CG-2 (P3/P4 no method), CG-3 (P1/P5 method realised as a window start), CG-4 (unreal ladder), CG-5 (outcome stamp agrees) fail.
- Gate re-run on the final form: not performed by the auditor (outside the audit brief; the coordinator's snapshot is the only gate evidence).

VERDICT revision_1: task0=RED task1=RED charter=CG-1,CG-2,CG-3,CG-4,CG-5,CG-6,CG-7,CG-8,CG-9

## revision_2

### charter_global_frozen (revision_2)
- Frozen 2026-10-18 (before any revision_2 GT reveal); auditor erl-task-policy-audit. revision_1 text above is left untouched.
- Entry evidence: `tail -1 tasks/nonowner_policies_and_renewals/worklog.md` = "REWORK round 2: gates 7/7 green" (only that line read). `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 2` (2026-10-18T16:31:58): check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks --check REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK (all rc=0). Hashes: r2/0.masked.json e715bbeb…87c9, r2/1.masked.json 3ebc3bb9…28c4, nonowner.extended.yaml d1f66e3f…2d2b (changed from 67df3e94… -> charter sections re-derived), task_tools.py 1fc353ab…cc (unchanged -> § action_binding_and_uuids carried forward from revision_1 on that hash).
- Read: the above plus `rework_r2_claims.md` (claims only), XF_recipe points 1-19. Masked: tasks/*.json, plan.md, worklog.md beyond its last line.
- Base copy lines 1-1889 still byte-identical to blueprint/products/nonowner.yaml.

### sweep results (revision_2)
- Scratch sweep: every compute_basis quote, every baseline sentence, every replaced_by and every prerequisite policy_source is verbatim in its own rule; every compute binding has a basis; no factor id is a tool-name substring; no shared binding; no `decides: result`; no authoring-viewpoint phrasing.
- Factors: P1 5 (lapse, return, paperless, plan param; charging_basis method); P2 4 (unchanged); P3 6 (lapse, nonpay, return, paperless, plan param; filer_basis method); P4 6 (same shape as P3); P5 5 (lapse, nonpay, return param; filer_basis, exposure_basis method); P6 4 (unearned_basis method; short_term, service_charge, filer_load param).
- prerequisite graph: same six edges, same kinds/forms/resolvers as revision_1; acyclic; P4 sentence (a) now "…a package at or above the minimum backing package of every Operator certificate the named insured has requested, filed or had rejected." Each state-form sentence still has one writer.
- XF10 pair tables of the new methods: P1 charging_basis T1 share 1 (drops the day ratio) / T2 MX(ratio, 1/2) (adds a floor) / T3 ratio — all pairs PASS. P5 exposure_basis T1 whole return / T2 return x MX(d, MN(45, return days))/return days / T3 return x d/return days — all PASS. P3, P4, P5 filer_basis T1 1+(c-1)·share (adds the share operation) / T2 c / T3 1.0 — T1 pairs PASS, **T2 vs T3 FAIL** (the tier only substitutes the multiplier c(form, points) for 1.0, a number in the same formula). P2 certificate_runoff, P6 unearned_basis unchanged (PASS).

### round-1 RED closure (charter half)
- CG-1 closed in the rule: P3 now cures only an FR-44 Operator limits rejection, by moving to that certificate's fr minimum backing package (VA 100/200/50, FL 100/300/50), matching fr.yaml FR-44 Operator `minimum_backing_package_by_state` and fr_transmission. The world that reaches it is a new finding (R2-F).
- CG-2 closed: the seasonal rate tables are gone (single base-rate table, no tiered table).
- CG-3 closed for the round-1 members: no remaining method tier differs only by its start date. The filer_basis T2/T3 pair (number substitution) is a new member of the mislabelled-tier class (R2-G).
- CG-4 closed (state-of-rejection load deleted).
- CG-5 closed: every certificate rule says "the term's own record of the certificate it was written to back is not read", and both worlds carry stamp "none" while the read certificate is SR-22 (task 0) / FR-44 (task 1). A stale "none" is producible (no nonowner event rewrites financial_responsibility_filing after binding; renewal issue copies it).
- CG-6 closed (replaced_by restates the full transaction-by-transaction formula with no retention, and the voided-term return).
- CG-7 closed (agent-office tier deleted; no tier moves the in-force date).
- CG-8 closed: every certificate read filters by Operator variant, prefers FR-44, fixes status order (requested, filed, rejected) and first-recorded within a status, in rule and compute.
- CG-9 closed: P6 tier 2 requires "more than zero days and fewer than the term's days" in rule and compute.

### findings (revision_2, charter-global)
Each class lists every member found in one pass over P1-P6.
- **R2-A SOURCE-FACTOR RED (XF17, incidental key) — paperless credit middle tier.** Members: P1 late_paperless_credit, P3 rerate_paperless_credit, P4 offer_paperless_credit (P2, P5, P6 have none). The 0.98 tier is keyed on "some document on the term was sent by mail alone", which counts the delivery of whatever document went by post, including the company's own mailed nonpayment notices and an insured's mailed Statement of No Loss. Real paperless discounts follow the insured's enrollment in electronic delivery, not a count of past mailings. Bears on both tasks (the 0.98 tier is the one taken in both worlds).
- **R2-B SOURCE-FACTOR RED (XF17, add-on without a published counterpart / one dimension charged twice).** Members: P2 advance_notice_credit (a cut in the short-rate retention for ten-plus days' notice; no carrier publishes one for that charge); P6 increase_service_charge (a % surcharge for five-installment plans on the increase charge, which is the difference of P3's re-rated premium that already carries the plan credit 0.97 for the same EFT/autopay plans, and on top of the billing charter's per-installment fee); P6 increase_filer_load (an SR-22/FR-44 load on the increase charge, whose re-rated premium already carries the filer class for the same certificate form). Bears on task 0 (P2) and task 1 (P6).
- **R2-C SOURCE-FACTOR RED (XF9, tier unreachable or universal within the policy's own scope).** Members: P1 late_lapse_relativity — scope is "a renewal term … so that a lapse is recorded", so "no lapse recorded" is never reached (result returns full_term_premium without a lapse): 2 reachable tiers. P5 rewrite_lapse_relativity — a reinstatement with a lapse always records one: same. P5 rewrite_nonpay_relativity — every reinstatement with lapse follows a nonpayment cancellation at most reinstatement_window_days (<= 30) + offset 1 days before the reinstatement effective date, so the 0-90-day tier holds of every customer who reaches this write; the 91-365 and none tiers are unreachable. (Not members: P3/P4 lapse and nonpay ladders — terms without a lapse or cancellation are in scope.) Observation in the same pass: P1's baseline nonpayment relativity reads a cancellation "recorded on the renewal term" before its effective date, which no renewal term can carry — a dead baseline clause. Bears on task 0 (P1) and task 1 (P5).
- **R2-D SOURCE-POLICY RED (XF8/XF11, undefined period boundary).** Members: P1 "late-renewal period", P3 "re-rated package period", P5 "reinstatement re-write period", P4 "renewal offer period". None is defined; compute anchors P1/P3 at the term's effective date and term months, P4 at the renewal term, P5 at the reinstatement date to expiration. Second readings: P1 period = the days in force (from the in-force date); P3 period = from the day of the change (the re-rate "taking effect on the day it is made"); P5 period = from the cancellation date under the flat exposure tier. A required-through date between the two candidate starts gives "inside -> share" in one reading and "before the period begins -> no filer class" in the other. P4 is the weakest member (its share counts from the renewal effective date = renewal term start). No task world places the date in that gap (charter-only).
- **R2-E SOURCE-POLICY RED (XF9/XF8, overlapping or ambiguous tier condition "or none").** Members: P1 late_charging_basis T1 "when the named insured has an … certificate on file … whose required-through date is on or after the first lapse day, or has none, … flat" — "or has none" reads as "has no certificate", which overlaps T2 "when no such certificate is on file and the renewal term runs twelve months"; P5 rewrite_exposure_basis T1 "had an … certificate on file … with a required-through date on or after it, or none, … flat amount, booked from the cancellation effective date". Compute reads "none" as "no required-through date". Bears on task 1 (P5, demonstrated there); task 0's P1 world has a qualifying certificate (no consequence).
- **R2-F SOURCE-FACTOR RED (XF13, cross-category seed not producible) — task 1's FR-44 request.** fr base fr_filing_eligibility: "The backing term's package must be at or above the certificate's minimum backing package for the filing state" (FR-44 Operator VA: Cardinal Point Non-Owner 100/200/50); nonowner_eligibility: "an FR-44 Operator certificate only where the residence state is in fr44_filing_states" (Minimum Limits with UM: []). The seeded VA FR-44 Operator request 57cf04bc (and its 35.00 fee) on a Minimum Limits with UM term is a request both charters refuse, so its policy_limits_insufficient rejection is not a state the fr charter produces. The reworker's own claims file discloses this ("the seeded request was transmitted on a term below its minimum backing package"). P3's trigger is reachable only through a renewal re-tier to a lower package, which task 1's term-1 world is not. Bears on task 1.
- **R2-G SOURCE-FACTOR RED (XF10, method pair that substitutes a number).** Members: P3 rerate_filer_basis, P4 offer_filer_basis, P5 rewrite_filer_basis, pair T2 (full class c) vs T3 (no filer class, 1.0). Consequence is per task: where the world realises T2 against baseline T3, the method contributes only a number (task 1: P3 and P5 realise T2; P4 realises T1).
- **R2-H SOURCE-POLICY RED (XF2, assembly sentence names a factor quantity).** Members: P3 "the re-rated package filer class and every re-rated package relativity and credit are multiplied into one combined relativity", P4 "the renewal offer filer class and every renewal offer relativity and credit …", P5 "then the reinstatement re-write filer class and every reinstatement re-write relativity …". (P1, P2, P6 combination sentences are generic.) Charter-only consequence: the hub/computation document must name the filer factor.
- Observations (revision_2): O2-1 P5 T2 floors the re-write days at the return's 38 days, so the entry is booked from the reinstatement date for more days than remain to expiration. O2-2 the tool docstring requires "a positive number" for rewritten_amount, while P5's rule states a zero re-write for a term with no nonpayment return (unreachable, since base always books that return). O2-3 P1 re-rates the late renewal from scratch rather than from the offered full_term_premium (declared overwrite). O2-4 the fr follow-up retransmission after P3 still has no tool here (O-11 carried). O-5, O-6, O-10, O-12 carried unchanged.

### closing_checklist (revision_2)
Not closed: both tasks RED.
- Round-1 charter REDs CG-1…CG-9: all closed in the charter text (§ round-1 RED closure); none regressed.
- Scope: task 0 {P1, P2}, task 1 {P5, P3, P6, P4}, disjoint and complete; tools unchanged; graph acyclic, no deadlock on reachable worlds (XF19: every edge sentence matches its condition; withdrawn/terminated/cancellation_filed filings cannot satisfy P4's sentence; P6's "for every reinstatement" cannot be met by a stale earlier re-write alone).
- Every scored figure of both tasks equals the auditor's blind recomputation. Open: R2-A, R2-B, R2-C, R2-D, R2-E, R2-F, R2-G, R2-H.
- Gates: coordinator snapshot round 2 all OK (cited above); not re-run by the auditor.

VERDICT revision_2: task0=RED task1=RED charter=R2-A,R2-B,R2-C,R2-D,R2-E,R2-F,R2-G,R2-H

## revision_3

### charter_global_frozen (revision_3)
- Frozen 2026-10-19, before any revision_3 GT reveal; auditor erl-task-policy-audit; revision_1/2 text untouched.
- Entry evidence: worklog last line "REWORK round 3: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 3` (2026-10-19T12:21:06): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r3/0.masked.json c9984d67…83e9, r3/1.masked.json 3e78acd6…9253, nonowner.extended.yaml 8f1a4900…2d0e (changed), task_tools.py fe078886…11a3 (changed) -> every charter-global section re-derived.
- Read: the above, rework_r3_claims.md (claims only), XF_recipe points 1-23 (point 23 applied exactly as written). Masked as before.
- Base copy lines 1-1889 still identical to blueprint/products/nonowner.yaml.

### tools (revision_3)
- Six tools, same names/uuid8s/owners. Changes: book_package_increase_premium docstring now "for a package change" and `additional_amount` "a positive number" (was "0 or more"); body unchanged (writes event nonowner_additional_premium, transaction_reason "limits_increase", unconditionally). No body judges a prerequisite; no ordering words; no example values; XF14 unchanged.

### sweep results (revision_3)
- Every compute_basis quote, baseline sentence, replaced_by and policy_source verbatim in its own rule; every binding has a basis; no shared binding, no factor id inside a tool name. "paperless" occurs nowhere; "or none"/"or has none" occur nowhere; no rule uses an undefined "period" (every day count states its included and excluded ends).
- Factors: P1 5 (filer_class, lapse, return, plan param; charging_basis method); P2 4 (relief, elapsed, term_origin param; certificate_runoff method); P3 6 (filer_class, lapse, nonpay, return, plan param; change_basis method); P4 5 (filer_class, nonpay, return, plan param; lapse_window method); P5 4 (lapse, return, plan param; exposure_basis method); P6 6 (filer_class, lapse, nonpay, return, plan param; deduction_basis method).
- XF10 pairs: P1 charging_basis flat (share 1) / certified-days (term days less the lapse days after the fr required-through date — data-selected window) / per-day — PASS. P3 change_basis MX(current, new base) / day-weighted blend / new base — PASS. P4 lapse_window share / share floored at 1/2 / full — PASS. P5 exposure flat / certified-days / per-day — PASS. P6 deduction entry-by-entry / own-days / term-days — PASS. P2 runoff — PASS.
- Graph: P2<-P1 (vi, state); P4<-P3 (vi, state: "…not fixed until the expiring term carries a package that accepts a DUI or DWI conviction within 60 months whenever the named insured has a DUI-related FR-44 Operator certificate requirement recorded."); P4<-P6 (state_gate, action: "A renewal offer is not issued before any increase charge owed for a package change made on the expiring term has been booked."); P6<-P3 (vi, state: "…worked out only after the term carries the package it moves to."); P6<-P5 (vi, state). Acyclic; one writer per state-form sentence.
- XF20: P6 states that a charge that is not above zero, or one with fewer than 15 days left, owes nothing and books nothing, and P4 waits only on an "increase charge owed" — consistent with the now-positive tool contract. P5 books nothing when no nonpayment return exists, while P6 waits on a re-written entry "for every reinstatement with a lapse"; unreachable (a nonpayment cancellation always books its return) — observation O3-1.
- XF21: both worlds' billing ledgers run from the customer's first plan; 12-month windows fall inside seeded history.
- XF23 keys: filer status, lapse, prior nonpayment cancellation, plan/EFT, package, state, points, day-based methods, new-business vs renewal origin on a short-rate retention, cancellation reason on a short-rate retention — all rating-plan or rule-manual dimensions, stated as company relativities; no statute cited. Returned-payment history (P1, P3, P4, P5, P6) is not on point 23's list; I cannot show that no filing uses it — observation O3-2 (reworker discloses the same residual risk).

### revision_2 RED closure
- R2-A closed (paperless credit struck everywhere). R2-B closed (advance-notice, service charge, filer handling load struck; P2's replacement, term origin, is a real rule-manual dimension — new-business minimum earned/short-rate — not an add-on). R2-C closed (P1/P5 lapse ladders 1-2 / 3-5 / >=6 days, all reachable; P5 nonpayment ladder struck). R2-D closed (no undefined period). R2-E closed ("or none" gone; each exposure tier has one booking date). R2-F closed (task 1's FR-44 is filed on a 250/500/100 term, which fr eligibility and fr44_filing_states allow; the DUI makes that package's dui_within_60_months_accepted=false the trigger). R2-G closed (every method pair PASS). R2-H closed (one generic combination sentence per policy, naming no factor quantity).

### findings (revision_3, charter-global)
- **R3-A SOURCE-POLICY RED (XF3, non-commuting order) — P6.** The rule defines "The standard increase charge is the increase rated premium multiplied by the increase days and divided by the term's days, less the increase deduction", the increase rated premium being "base rate … by the state factor, by the increase points class factor and by the term's months over six" (no relativity), and then: "The increase adjustments below are applied to that standard figure … every adjustment stated as a relativity or credit is multiplied into one combined relativity that multiplies the figure once". Read as written, the relativities multiply the charge after the deduction; compute (`increase_rated_share` carries filer, lapse, nonpay, return and plan factors; `result = MX(0, increase_rated_share - increase_deduction)`) multiplies before it. Multiplication and subtraction do not commute, so the two readings differ whenever the combined relativity is not 1. Member check over all six: P1 (rated x share), P3, P4 (products), P5 (return x days x relativities), P2 (multipliers into the retention percentage) commute; P6 is the only member. Bears on task 1.
- **R3-B SOURCE-POLICY RED (XF5f, undeclared departure) — P6 charges an increase on a limits decrease.** P6: "The additional premium for a package change during the term is worked out by this rule"; base event meanings: nonowner_additional_premium "Additional premium for a reinstatement or limits increase", nonowner_return_premium "Unearned premium returned for a cancellation or limits decrease". P6's overwrite retires only the premium_charging sentence on a limits increase; nothing names the decrease case, and the tool stamps transaction_reason "limits_increase" on every change. Same situation (a move to lower limits), two conclusions: base -> a return-premium entry for the decrease; P6 -> an additional-premium entry labelled limits increase. Bears on task 1, whose move is 250/500/100 -> 100/300/50 (a decrease).
- Observations: O3-1 (above). O3-2 (above). O3-3 P3 stores a re-rated full-term premium (blended base, whole-term relativities) that no charge derives from — P6 re-rates the remaining days on the new package's full base independently. O3-4 P2's lapse-origin retention 1.10 and P1's lapse relativity both bear on the lapse, but in two different charges (written premium vs cancellation retention) — not one charge. O3-5 P4 waits for a DUI-accepting package, which P3 supplies only when points <= 12; above that only an insured-elected base change resolves it (no deadlock: 50/100/50 and the minimum packages accept a DUI). O3-6 the seeded final bills put the whole remaining balance in past_due_amount ("unpaid amounts of earlier invoices carried onto this invoice"), which overstates what had been invoiced (task 1: 344.31 vs 266.16 invoiced and unpaid); no rule reads it. O3-7 rework_r3_claims.md says task 0 values were "re-verified unchanged", but the revision_3 world re-prices both terms and the figures move (see 0.md). O-5, O-6, O-10, O-12 carried.

### closing_checklist (revision_3)
Not closed: task 1 RED.
- revision_2 REDs R2-A…R2-H: all closed; round-1 CG-1…CG-9 still closed; no regression found (stamp, certificate selection, replaced_by restatement, agent tier, zero-day tier re-checked on the revision_3 text).
- Scope {P1, P2} / {P5, P3, P6, P4}, disjoint and complete; tools re-read (hash changed); graph acyclic; every scored figure of both tasks equals the blind recomputation.
- Open: R3-A (P6 order of relativities vs deduction), R3-B (P6 additional premium on a limits decrease, labelled limits_increase).
- Gates: coordinator round-3 snapshot all OK (cited); not re-run by the auditor.

VERDICT revision_3: task0=PASS task1=RED charter=R3-A,R3-B

## revision_4

### charter_global_frozen (revision_4)
- Frozen 2026-10-19, before the revision_4 reveal; revisions 1-3 untouched.
- Entry: worklog last line "REWORK round 4: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 4` (2026-10-19T22:07:46): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r4/0.masked.json c9984d67…83e9 (= revision_3, task 0 world unchanged), r4/1.masked.json 3ff28317…3d35, nonowner.extended.yaml 4c5d8919…5ec4 (changed), task_tools.py cd8e7684…c8c (changed). Claims read: rework_r4_claims.md.
- Base copy still identical. Sweep over all six policies: every basis quote, baseline sentence, replaced_by and policy_source verbatim in its rule; factor lists unchanged from revision_3. Recomputing P1-P5 on the revision_4 worlds reproduces every revision_3 figure and baseline (P1 1449.71, P2 1183.94, P3 2107.45, P5 439.70, P4 1765.28, plus all factor-sensitivity figures), so the claimed change set (P6 text, P4 edge condition, one tool, task 1's final-bill row) is consistent with what moved.

### R3 closure
- **R3-A closed.** P6's combination sentence now reads "…one combined relativity that multiplies the increase rated premium once, before the increase deduction is subtracted…", which is the compute (`increase_rated_share` carries the relativities; `result = MX(0, increase_rated_share - increase_deduction)`). Only one reading remains: task 1 = 64.89.
- **R3-B closed.** P6's overwrite replaced_by now declares the departure in its own words: a move to a lower base rate whose charge "by this rule is above zero … is charged as additional premium and not returned, and only such a move", booked with reason limits_decrease (limits_increase for a higher base rate); "every other move to a lower base rate still returns unearned premium as a return-premium entry for the limits decrease". The tool takes `change_direction` ("higher_base_rate" -> limits_increase, "lower_base_rate" -> limits_decrease; both in the db_schema enum) and maps it without judging state; the docstring matches the body, has no ordering words and no example values. P4's state_gate condition names either reason; the sentence is unchanged; XF20 still holds (P6 books nothing when nothing is owed, and P4 waits only on an owed charge).
- XF 1-23 re-checked on the changed P6, P4 edge and tool: no new member. Observation O4-1: the restated "every other move to a lower base rate still returns unearned premium" points at a base return no base policy computes; not on any task path, and the gap is in the base, not introduced here.
- O3-6 fixed (task 1 final bill: past due 266.16 = invoice 3 unpaid + NSF + late fee; unbilled premium 43.15 = earned 1008.59 - billed 965.44; unbilled fee 35.00 = the FR-44 fee; total 344.31). O3-7 corrected in the claims. O3-1/2/3/4/5 carried as observations.

### findings (revision_4)
- None new. Task 0: world and figures identical to revision_3 (no regression).

### closing_checklist (revision_4)
- Per-task files 0.md, 1.md and _difficulty.md carry revisions 1-4; every revision_4 comparison is PASS.
- Every extended policy is covered: task 0 = {P1, P2}, task 1 = {P5, P3, P6, P4}. The scopes are disjoint, the tools are disjoint, and the six uuid8s are independent and unchanged.
- Trees:
  - task 0 has 1 prerequisite with 1 value_input edge;
  - task 1 has 3 prerequisites with 3 value_input edges;
  - each tree has an owner=user write (P2, P3);
  - the difficulty graph is acyclic and has no deadlock on any reachable world.
- Factors:
  - every computation has a self-sufficient baseline giving a definite non-gold fall-back (1196.46, 1254.56, 1143.04, 380.16, 0.00, 1211.62);
  - every computation has 4-6 factors with at least 2 parameter and at least 1 method; every method pair passes the shape test;
  - each task has a multi-source factor and a cross-difficulty factor;
  - every ladder has >= 3 reachable tiers; stamps disagree with the tiers; keys meet XF17/XF23.
- Every round-1/2/3 RED is closed: CG-1…CG-9, R2-A…R2-H, R3-A, R3-B.
- Observations carried (no RED ground): O3-1 (unreachable nil re-write), O3-2 (returned-payment relativity disclosed residual risk), O3-3, O3-4, O3-5, O4-1, O-5, O-6, O-10, O-12.
- Gates: coordinator round-4 snapshot all OK (cited); not re-run by the auditor.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global_frozen (revision_5)
- Frozen 2026-10-20, before the revision_5 reveal; revisions 1-4 untouched.
- Entry: worklog last line "REWORK round 5: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 5` (2026-10-20T07:56:23): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r5/0.masked.json c9984d67…83e9 and r5/1.masked.json 3ff28317…3d35 (both = revision_4, worlds unchanged), nonowner.extended.yaml e13b59fe…acad6 (changed), task_tools.py 66fd633c…d7d8f (changed). Read: render_source/nonowner_policies_and_renewals/render_r1.md (F1-F3, this round's REDs), rework_r5_claims.md, XF_recipe points 1-26. Not read: render_source/physical_damage_claims (sibling difficulty).
- Base copy identical. Sweep: every basis quote, baseline sentence, replaced_by and policy_source verbatim in its own rule (all six policies). Recomputing all six policies on the revision_5 worlds reproduces every revision_4 figure, baseline and factor-sensitivity value.

### F1-F3 closure (render_r1 items)
- **F1 closed.** The clause ", as when the package re-rate rule's DUI realignment brings a filer class and other relativities onto the remaining days," is gone from P6's rule and replaced_by; the operative "whose increase charge by this rule is above zero" stays. Class pass over all six rules and replaced_by texts (search for "<x> rule", "rule's", "realignment", "filer class", "re-rate" outside a policy's own quantities): no other sentence names an extended policy's action or a factor quantity outside its own factor text. One phrase reviewed and kept as an observation (O5-1): P6's restatement "a reinstatement still re-writes premium under the reinstatement rule" is the XF5(a)-mandated restatement of the retired base clause "a reinstatement re-writes premium under nonowner_reinstatement". It names the base policy, not an extended id or tool, and the renderer's own scan left it unflagged.
- **F2 closed.** P2: "in every case the unearned days are never fewer than zero" and "when the unearned days come to zero nothing is returned and the cancellation books no return entry". Compute `unearned_days: MX(0, …)`. cancel_nonowner_term now takes `return_amount` "zero or more", always cancels, and books the return row only when amount > 0. The docstring states this. The branch is on the amount given, not a prerequisite check, and no 0.00 row is posted. Nothing waits on P2 (root), so XF20 holds. Class pass over the other day counts and amounts: P1 days in force >= 1 in scope; P5 re-write days >= 0 with "nothing is booked" stated for the nil case; P6 nil and <15-day cases book nothing; P3/P4 premiums positive. No other member.
- **F3 closed.** Filer required-through reads now sit inside each filer-class factor's `*_active` bindings (P1, P3, P4, P6). `request_reason` is in requirement_relief's bindings. `offer_window_left` is a plain binding defined by P4's baseline. Mechanical pass: the plain bindings that only one factor reads are late_standard_share, standard_unearned_days, offer_lapse_value + offer_window_left, and written_on_term (with per_day_rewrite in P5). Each is exactly that method factor's baseline expression (late_charge_share: late_standard_share; unearned_days: standard_unearned_days; offer_lapse_factor: offer_lapse_value if offer_window_left > 0; increase_deduction: written_on_term x increase_days / term_days; rewrite_amount_basis: per_day_rewrite). No factor reads another factor's binding; no factor binding is read outside its factor.

### XF 24-26 (all policies)
- XF24/25: no computation is a flat service charge; all six price premium. No member.
- **R5-A SOURCE-FACTOR RED (XF26, factor embedded in a recorded amount) — P1 late_filer_class and late_return_relativity.** P1 re-rates the late renewal as base x state x points x months x filer class x lapse x returned-payment x plan. The renewal term's recorded full_term_premium is the renewal offer the company issued 30 days before expiration (P4's rate-plan product), and it already carries the filer class and the returned-payment relativity of the same requirement and the same 12-month history. P1 changes nothing about either. Only the lapse (new since the offer) and the plan credit (the renewal term's plan, not the expiring term's) act on what the record does not embed. Class pass: P3's factors act on a binding-time premium that carried none of them (certificate, lapse, cancellation and plan change all came after binding). P5's act on a return derived from that premium. P6 and P4 read a package and premium the same task writes (observation O5-2). P2's act on no recorded premium. Member: P1 only. Bears on task 0.
- Observations: O5-1 (above). O5-2: P6's five relativities and P4's four parameter relativities repeat the ones already in P3's re-rated full_term_premium (written in the same task). That premium uses a blended base (P3 change_basis), so it cannot be read back into P6/P4 without redoing P3. Not a usable embedded figure. O3-1…O3-5, O4-1, O-5, O-6, O-10, O-12 carried.

### closing_checklist (revision_5)
Not closed: task 0 RED on R5-A.
- render_r1 F1, F2, F3: closed across their classes.
- Earlier closures still hold (CG-1…CG-9, R2-A…R2-H, R3-A, R3-B). Both tasks' scored figures are unchanged and equal the blind recomputation.
- Open: R5-A (XF26). P1's filer class and returned-payment relativity are already carried by task 0's recorded renewal full_term_premium. R5-A is a new XF26 member, not a regression of this round's rework.
- Gates: coordinator round-5 snapshot all OK (cited); not re-run by the auditor.

VERDICT revision_5: task0=RED task1=PASS charter=R5-A

## revision_6

### charter_global_frozen (revision_6)
- Frozen 2026-10-20, before the revision_6 reveal; revisions 1-5 untouched.
- Entry: worklog last line "REWORK round 6: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 6` (2026-10-20T14:40:04): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r6/0.masked.json d12ebb3e…fe19 (changed), r6/1.masked.json 3ff28317…3d35 (= revision_4/5), nonowner.extended.yaml 52eb39df…1f9a (changed), task_tools.py 66fd633c…d7d8f (= revision_5; tool section carried forward on that hash). Claims read: rework_r6_claims.md. The worklog is not read before the freeze.
- Base copy identical. Sweep: every basis quote, baseline sentence, replaced_by and policy_source verbatim in its rule (all six). P2-P6 recompute on task 1's unchanged world to every revision_5 figure, so only P1 changed in substance.

### R5-A closure (P1)
- P1's standard figure is now "the renewal term's recorded full-term premium, the premium its renewal offer was issued at and rated on the records of the offer's issue date, the renewal term's opened date". The rate table, state and points class are gone from P1. Its five factors act only on what that premium does not carry:
  - filer change: the class of a requirement requested after the issue date, divided by the class of a certificate whose SR-26 was sent after it;
  - the renewal term's own lapse (the offer carries only the expiring term's lapse);
  - returned-payment change;
  - plan change: the renewal plan's credit divided by the expiring plan's credit;
  - charging basis (the transaction's own method).
- Labels honest: four parameter and one method. Ladders have three reachable tiers each. Filer, returned-payment and plan change are multi-source. No factor reads another factor's binding. The single-factor plain binding late_standard_share is the method's baseline. The combination sentence is generic and unchanged. F1 (no cross-policy scope text), F2 (P2 floor) and F3 (binding allocation) still hold. XF26 class pass over P2-P6 is unchanged from revision_5 (no member).
- **R5-A closed for task 0** (demonstrated in 0.md).

### findings (revision_6)
- **R6-A SOURCE-FACTOR RED (point 23 / XF22 one dimension charged twice; XF12 words describe a case the compute does not price) — P1 late_return_change.** Rule: "carries a payment returned unpaid after the renewal term was issued, which the recorded premium, rated on the payments returned before the issue date, does not carry: … the payments returned unpaid whose posting date lies fewer than twelve whole months before the processing date are counted … and the recorded premium is taken to carry the relativity of one fewer". The "one fewer" convention stands in for the offer-date count the rule itself describes. It is wrong on reachable worlds. Demonstration: an offer issued with one return 11.5 months old (offer rated x 1.04). One more return posts after the issue date, and by processing the old return has left the window, so the count is again one. The rule's convention gives exactly one -> x 1.04 on top of the recorded premium, which already carries 1.04: the returned-payment dimension is charged twice for one return in the window, where the rule's own description (rated on the returns before the issue date) gives no change. Converse case: two returns posted after the issue date with none before. The description gives 1.08 (offer rated with none); the convention gives 1.08/1.04. No task world is of either shape: task 0 has one return before (2026-06-09, inside both windows) and one after (2026-09-14). Charter-only. Member pass: P1's filer change counts from records (requested_date vs issue date, SR-26 date), and so does its plan change (expiring term's plan). Neither uses a convention. No other policy has a "change since a recorded figure" factor.
- Observation O6-1 (the coordinator asked me to judge the SR-22 fee placement in task 0): the fr fee_billing_rule is "on the backing term's billing plan with the down payment or next invoice". The fee for the request of 2026-09-15 is posted on the backing term 7bd61466's plan a6e1e964 (billing a5d7ef2b, fr 43fde651). That plan issued no invoice after 2026-09-15: its last installment invoice and the renewal bill predate the request. The fee is collected in the customer's 2026-09-15 debit-card payment of 253.65 (= installment 203.65 + NSF 25.00 + filing fee 25.00), and the plan closes at 0.00. The literal rule does not cover a backing plan with no next invoice. This seed takes the right plan, collects the fee with the next payment, and leaves the ledger balanced. No rule or factor reads the fee. Judged acceptable (not RED).
- Observations carried: O5-1, O5-2, O3-1…O3-5, O4-1, O-5, O-6, O-10, O-12.

### closing_checklist (revision_6)
- R5-A closed: task 0's P1 factors now act only on changes since the recorded offer, and every factor moves the figure. render_r1 F1-F3 still closed. Earlier closures hold (CG-1…CG-9, R2-A…R2-H, R3-A, R3-B). Both tasks' scored figures equal the blind recomputation; task 1 is unchanged from revision_5.
- Open (charter-only, no task world affected): R6-A — P1's returned-payment change assumes "one fewer" return at the offer date. On reachable worlds (an old return leaving the window, or two returns after the offer) this misstates what the recorded premium carries, and charges the dimension twice or under-charges it.
- SR-22 fee placement in task 0 judged acceptable (O6-1).
- Gates: coordinator round-6 snapshot all OK (cited); not re-run by the auditor.

VERDICT revision_6: task0=PASS task1=PASS charter=R6-A

## revision_7

### charter_global_frozen (revision_7)
- Frozen 2026-10-20, before the revision_7 reveal; revisions 1-6 untouched.
- Entry: worklog last line "REWORK round 7: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 7` (2026-10-20T15:45:47): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r7/0.masked.json d12ebb3e…fe19 and r7/1.masked.json 3ff28317…3d35 (both = revision_6), nonowner.extended.yaml f6280343…49d1 (changed), task_tools.py 66fd633c…d7d8f (unchanged). Claims read: rework_r7_claims.md.
- Base copy identical. Sweep (all six): basis quotes, baseline sentences, replaced_by and policy_source verbatim. Factor counts: P1 3 param + 1 method; P2 4 param + 1 method; P3 5+1; P4 4+1; P5 3+1; P6 5+1. P3-P6 recompute on task 1's unchanged world to every revision_6 figure.

### R6-A closure
- P1's returned-payment change is struck. The words "return"/"returned" no longer occur in P1's rule, and no `nsf` parameter remains. P1's four factors (filer change, lapse, plan change, charging basis) count from records only, so there is no convention left. XF26 still holds.
- Probes on task 0's world (my own, scratch):
  - (a) aged-out: the 2026-06-09 return moved to 2025-10-01, inside the offer's window and outside the processing window;
  - (b) two-post-offer: both returns after 2026-09-10, none before;
  - (c) no returns.
  P1 = 1449.71 and P2 = 1205.23 in all three, the same as on the seeded world: returned payments no longer move P1. Class pass: no other policy has a "change since a recorded figure" factor; the returned-payment relativities of P3-P6 rate the current window directly.
- P2's new factor plan_retention_scale (Paid-in-Full 0.80, Monthly EFT / Card Autopay 0.90, other 1.00 on the short-rate retention) is a point-23 key (payment plan / paid-in-full) applied to a short-rate return. Ladder: three reachable tiers. Its bindings are its own (cancel_billing_plan). The combination sentence is generic ("every retention multiplier is multiplied into the package's retention percentage"). It acts on the retention percentage, which no recorded amount carries (XF26). XF22: a real dimension already in the records, not a new add-on.
- render_r1 F1-F3, R5-A, R3-A/B, R2-*, CG-* re-checked on the revision_7 text: still closed.

### findings (revision_7)
- None new (RED).
- Observations:
  - O7-1: P1 still says of the recorded premium "what changed after that date is carried by the adjustments below". A returned payment after the offer date (task 0: 2026-09-14) is now not carried. No P1 schedule prices it, so there is no computable second reading; the sentence is broader than the adjustments.
  - O7-2: in P2's return the plan dimension appears both in the written premium the return refunds (P1's plan change) and in the retention multiplier. These are two different charges (the premium vs the cancellation retention), handled as O3-4 was.
  - Earlier observations carried.

### closing_checklist (revision_7)
- R6-A closed: the factor is struck, and the aged-out, two-post-offer and no-return probes leave P1/P2 unchanged.
- All earlier REDs still closed: CG-1…CG-9, R2-A…R2-H, R3-A, R3-B, render_r1 F1-F3, R5-A.
- Every policy carries 4-6 factors (>= 2 parameter, >= 1 method). Each task has a multi-source and a cross-difficulty factor. Every factor bears weight against an honest baseline with a definite non-gold fall-back. Trees hold (an owner=user write in each), the graph is acyclic, scopes are disjoint and complete, and tools are unchanged.
- Both tasks' figures equal the blind recomputation.
- Observations only (O7-1, O7-2 and carried items).
- Gates: coordinator round-7 snapshot all OK (cited); not re-run by the auditor.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

### charter_global_frozen (revision_8)
- Frozen 2026-10-20, before the revision_8 reveal; revisions 1-7 untouched.
- Entry: worklog last line "REWORK round 8: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 8` (2026-10-20T16:14:46): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r8/0.masked.json d12ebb3e…fe19 and r8/1.masked.json 3ff28317…3d35 (both = revision_6/7), nonowner.extended.yaml 63b0174b…ccd5 (changed), task_tools.py 66fd633c…d7d8f (unchanged). Read: render_source/nonowner_policies_and_renewals/render_r2.md (F4, F5) and rework_r8_claims.md.
- Base copy identical. Sweep (all six): basis quotes, baseline sentences, replaced_by and policy_source verbatim; every compute binding has a basis; no unused binding.

### F4/F5 closure
- **F4 closed.** Every `params` key of every policy is read by a `K('…')` in compute or a factor ladder/baseline. P1 no longer declares lapse_window_months, nonpay_recent_months, nonpay_window_months, rel_nonpay_recent or rel_nonpay_later, and P5 no longer declares lapse_window_months. Class pass over P2, P3, P4 and P6: no unused key.
- **F5 closed.** The four filer readings (P1 late_filer_change, P3 rerate_filer_class, P4 offer_filer_class, P6 increase_filer_class) now read: "for each form the filing read is its requested filing, otherwise its filed one, otherwise its rejected one, the one recorded first within a status, and that filing counts when its required-through date is on or after <date> or is not recorded, no other filing of the form being read when it does not; when both forms count the FR-44 one counts". This is exactly the compute: status-priority pick, then the through test with no fallback; `*_sr22_active` requires `not *_fr44_active`. The renderer's case — a stale requested filing beside a current filed one — has a single reading: nothing counts for that form. The release clause behind late_released_form now states the compute's order: FR-44 form first, then SR-22. Within a form the first cancellation_filed filing is read, then the first terminated one when that does not qualify. The qualification test is requested on or before the issue date, required-through on or after the renewal effective date or not recorded, and SR-26 date after the issue date.
- Scored values: unchanged (recompute below and in the task files).

### findings (revision_8)
- None. Observations carried (O7-1, O7-2, O6-1, O5-1, O5-2, O4-1, O3-1…O3-5, O-5, O-6, O-10, O-12).

## closing_checklist (final, revision_8)
- **Files:** per-task files 0.md and 1.md match tasks 0..1 one to one, with _difficulty.md alongside. Revisions 1-8 are kept in order and the older text is untouched. Every revision_8 comparison section is PASS.
- **Coverage and scope:**
  - task 0 = {nonowner_ext_late_renewal_written, nonowner_ext_insured_cancel_return};
  - task 1 = {nonowner_ext_reinstatement_rewritten, nonowner_ext_package_rerate, nonowner_ext_package_increase_premium, nonowner_ext_renewal_offer_premium};
  - each scope spans its whole problem tree; the two are disjoint and cover all six extended policies;
  - task tools are disjoint and closed, and the six uuid8s (ed68a083, 6aabad38, 23563ff0, 67dc97ad, 8b98e0ec, bf43cbc7) are independent and frozen.
- **Problem trees:**
  - task 0: one prerequisite problem (P1) on one value_input state-form edge; root P2 is the customer's own write (cancel_nonowner_term, owner=user);
  - task 1: three prerequisite problems (P5, P3, P6) with three value_input edges plus one state_gate action-form edge (fallback reason tested and accepted); P3 is the customer's own write (change_nonowner_package, owner=user);
  - every edge is unmet at the opening and bears weight (task 0: skip P1 -> 0.00; task 1: skip P3 -> P6 170.98, P4 2192.66; skip P5 -> P6 89.09; skip P6 -> P4's gate fails);
  - the difficulty graph is acyclic and no edge deadlocks on a reachable world; no tool validates a prerequisite.
- **Factors:**
  - P1 4 (3 parameter + 1 method), P2 5 (4+1), P3 6 (5+1), P4 5 (4+1), P5 4 (3+1), P6 6 (5+1);
  - every ladder has >= 3 reachable, distinct tiers stated in full in its rule; method pairs pass the shape test; keys are rating-plan dimensions (XF17/23); no factor's evidence sits in a recorded amount (XF26); stamps disagree with the tiers (XF18);
  - each task has multi-source factors (task 0: P1 filer change, P2 requirement relief and term origin; task 1: filer classes, P5 exposure basis) and cross-difficulty factors (fr, billing);
  - every baseline is self-sufficient and gives a definite non-gold fall-back (1244.32, 1254.56, 1143.04, 380.16, 0.00, 1211.62);
  - every declared factor moves its scored value on its task's world.
- **Unique solution:** both tasks' write sequences, owners, order, arguments and terminal states equal the auditor's blind derivation. No second reading remains for any item raised in revisions 1-7 or in render_r1/render_r2.
- **Gates:** this difficulty's instantiate gates on the final form are taken from the coordinator's round-8 snapshot (7/7 OK, 2026-10-20T16:14:46). The auditor did not re-run them.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

### charter_global_frozen (revision_9)
- Frozen 2026-10-21, before the revision_9 reveal; revisions 1-8 untouched.
- Entry: worklog last line "REWORK round 9: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 9` (2026-10-21T19:50:16): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: r9/0.masked.json 204f5d2d…3ff8 (changed), r9/1.masked.json 35ea3a35…e0f7 (changed), nonowner.extended.yaml 53a9ceec…ae65 (changed), task_tools.py 66fd633c…d7d8f (unchanged). Claims read: rework_r9_claims.md (route: scoped charter change plus re-seed). Items S1-S4 are taken from the coordinator brief. The policy_kb audit file is not read; published docs/fr and docs/billing are read as needed.
- Base copy identical. Sweep (all six): basis quotes, baseline sentences, replaced_by and policy_source verbatim; no unused param or binding; no factor binding read outside its factor (XF1).

### changed reads, audited as a first round (P1 late_charging_basis, P5 rewrite_exposure_basis)
- New rule (same in both): the certificate "that was on file during the lapse" is the first of: the FR-44 form's filed, cancellation_filed and terminated filings (each the one recorded first), then the same for the SR-22 form, "whose filing date is on or before the first lapse day". Its "certified-through date is the earlier of its required-through date and its certificate end date, a date not recorded leaving the other, and there is none when neither is recorded". The tiers are unchanged in shape: flat when certified-through is on or after the last lapse day or none; certified-days when it falls inside the lapse; per-day otherwise, including no such certificate.
- Compute: `*_cert_pick` takes cases 1-6 in exactly that order (CFIELD first match = recorded first, filed_date <= lapse_start_date). Certified-through is `MN(required_through, certificate_end)` with the stated fallbacks; the tier tests are unchanged. Rule and compute match word for word, and the basis quotes are verbatim.
- Realism (point 23): the certificate end date is the SR-26 date plus the fr run-off, the day the state stops treating the driver as certified (docs/fr certificate_end_date_rule). Lapse days are charged only while the state still held the company to the certificate, so no premium is kept for days with no exposure.
- Probes on task 1's world (P5): certificate end 2026-10-11 gives certified-days 51/53 -> 395.67 basis; end 2026-10-05 gives per-day 49/53 -> 380.16; end 2026-10-25 (seeded) gives flat 411.19. All three tiers are reachable, and the pick skips the refiling e02f79a7 (filed 2026-10-15, after the first lapse day). XF10 shapes are unchanged (flat / data-selected window / per-day). The factor bindings hold the new reads (XF1).

### S1-S4 closure (against the published docs)
- **S1 closed.** Task 1: FR-44 c236dc0d (requested 2026-09-21, filed 2026-09-22) received its SR-26 on 2026-10-12 (reason policy_cancelled), inside the lapse window that starts on the lapse start date 2026-10-10 (docs/fr lapse_sr26_transmission). Certificate end 2026-10-25 = SR-26 date + 13 days of lapse run-off:
  - run-off counted from the lapse start: 10 listed days less 2 (lapse of 4 days, band "more than 3, up to 10") = 8 (docs/fr lapse_runoff_counting_by_lapse_length);
  - plus form notice days 0 (the term records "none"), type 1 (Operator on a non-owner term), state 4 (Virginia), out-of-state 0 (VA filed in VA) = 13.
  The reinstatement refiling e02f79a7 (requested 2026-10-14, filed 2026-10-15, prior c236dc0d, required-through carried) has fee 26.00 = basis 13 (half of the flat 25.00, rounded up, because the end date 2026-10-25 >= refiling date) + type 2.00 + restoration 5.00 (lapse > 3 days) + state 6.00 + form 0 + out-of-state 0 (docs/fr refiling_* tariff and charges). The fee is billed on the backing plan (f6640e02, 2026-10-14). At the opening no fr write is owed: no further SR-26 is due; termination of c236dc0d is due only from 2026-10-25; no release or copy is owed. No billing write is owed either: inst 4 (due 2026-10-12, inside the lapse) is re-billed on the next invoice under docs/billing reactivation_after_reinstatement, and inst 5's invoice date is 2026-11-02.
- **S2 closed.** The FR-44 was requested 2026-09-21 while the term was in force; the nonpayment notice is dated 2026-09-25.
- **S3 closed.**
  - Inst 1 is invoiced 2026-06-12 and due 2026-07-02: one month after the 2026-06-02 effective date, with the Six-Pay 20-day lead.
  - The due-day change 2 -> 12 is recorded with the EFT switch. The authorization of 2026-07-10 is >= 3 days and >= 5 days before the next due date 2026-08-12, the shift is 10 days (<= 10), it is 1 change of 1 allowed, and the plan was current after the 2026-07-09 payment rescinded the first notice.
  - EFT invoices carry the 10-day lead. The 2026-09-12 draft (a Saturday) posts on the next banking day, 2026-09-14, and is returned 2026-09-16; the NSF fee is 25.00 and the late fee 10.00 (2026-09-18, after the 5-day grace).
  - Notice 2026-09-25 (>= 5 days after the due date) is effective 2026-10-10 (Virginia 15 days). The FR-44 fee 35.00 is on inst 4's invoice.
  - Return 411.19 = 1419.78 x 53/183. Final bill 348.31 = the ledger balance after the credit. The reinstatement payment of 266.16 = the noticed minimum due.
  - Ledger balance 128.15 = 348.31 - 266.16 + 20.00 reinstatement fee + 26.00 refiling fee.
- **S4 closed.** Task 0's renewal plan a8ca8a85 (Paid-in-Full, balance -1265.17, no installment to bill) now reads paid_in_full (docs/billing delinquency_status_rule).

### findings (revision_9)
- None (RED).
- Observation O9-1: task 1's final bill carries 348.31 as past_due_amount. 82.15 of it is inst 4's residual, whose due date (2026-10-12) fell inside the lapse. The 2026-10-13 reinstatement payment covered only inst 3's noticed 266.16. This is producible only under the reactivation rule's reading that an installment due inside the lapse is re-billed on the next invoice rather than counted past due at reinstatement. No scored figure reads it.
- Earlier observations carried.

### closing_checklist (revision_9)
- S1-S4 closed against docs/fr and docs/billing.
  - At either task's opening, no write that another product's rules call owed can move a scored figure.
  - Both tasks' seeded fr and billing histories reproduce the owning rules' figures (lapse run-off 13 days, refiling fee 26.00, due-day change limits, invoice leads, notices, return, final bill, ledger balances), subject to O9-1.
- The changed reads (P1/P5 exposure on the certificate in force during the lapse) were audited as a first round.
  - Rule = compute, three reachable tiers, honest method shape.
  - No premium for days without certification.
- Gold re-derived blind and equal to GT in both tasks.
- Nothing regressed: CG-1…CG-9, R2-A…R2-H, R3-A, R3-B, R5-A, R6-A and render F1-F5 all still closed.
- The final closing checklist of revision_8 holds on the revision_9 form: scope, trees, factor floors, multi-source and cross-difficulty factors, baselines, uuid8s.
- Gates: coordinator round-9 snapshot all OK (cited); not re-run by the auditor.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN

## revision_10

### charter_global_frozen (revision_10)
- Frozen 2026-10-21, before the revision_10 reveal; revisions 1-9 untouched.
- Entry: worklog last line "REWORK round 10: gates 7/7 green". `/tmp/erl0071_coord/snapshot.sh nonowner_policies_and_renewals 10` (2026-10-21T20:22:06): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (all rc=0). Hashes: nonowner.extended.yaml 53a9ceec…ae65 and task_tools.py 66fd633c…d7d8f, **byte-identical to revision_9 as required** (all charter-global sections carried forward on these hashes). r10/0.masked.json 204f5d2d…3ff8 (= revision_9); r10/1.masked.json a6e0aea4…fbf4 (changed: only fr_filings c236dc0d.certificate_end_date 2026-10-25 -> 2026-11-14 and final bill 1d27736f's split). Claims read: rework_r10_claims.md.

### N1/N2 closure (task 1 seed, against docs)
- **N1 closed.** The SR-26 of 2026-10-12 (reason policy_cancelled) was sent while term 1fb5c071 stood cancelled and not yet reinstated: the reinstatement was processed 2026-10-13, effective 2026-10-14. It is therefore a cancellation SR-26 (docs/fr cancellation_sr26_transmission), inside its window: closed date 2026-10-10 as day 0, + 3 transmission days. Certificate end date:
  - run-off by reason, nonpayment with 2 days from the closed date to the SR-26 date, within the 250/500/100 reinstatement window of 30 days: max(listed 10, 30 - 2) = 28 (docs/fr cancellation_runoff_by_reason);
  - + type 1 (Operator on a non-owner term) + state 4 (Virginia) + out-of-state 0 (VA filing, VA resident) (docs/fr cancellation_notice_days_*) = 33 days;
  - so the end date is 2026-10-12 + 33 = 2026-11-14, as seeded.
  The certificate has had its SR-26, so no second (lapse) SR-26 is owed after the reinstatement (docs/fr lapse_sr26_transmission rule 2, one SR-26 per certificate). Its termination is due only from 2026-11-14. The refiling fee basis is unchanged: end 2026-11-14 >= refiling date 2026-10-14 -> half of 25.00 rounded up = 13; fee 26.00 as seeded. No fr write is owed at the opening.
- **N2 closed.** The final bill of 2026-10-11 now reads past due 266.16 (inst 3: 231.16 + NSF 25.00 + late fee 10.00), premium 43.15 (inst 4's premium after the 411.19 unearned credit) and fee 39.00 (inst 4's 4.00 + FR-44 35.00). The total of 348.31 is unchanged and equals the ledger balance. Inst 4 (due 2026-10-12) was not past due on the bill date, which matches the field meanings. The 2026-10-13 reinstatement payment of 266.16 covers every past-due amount (docs/billing reactivation_after_reinstatement: "The reinstatement payment itself must already have covered every past-due amount"). O9-1 is resolved.

### findings (revision_10)
- None. Observations carried.

### closing_checklist (revision_10)
- Seed-only round confirmed: charter and tools byte-identical (53a9ceec…, 66fd633c…).
- N1 and N2 closed against docs/fr and docs/billing; O9-1 resolved.
- Gold re-derived blind and equal to GT in both tasks; every scored and sensitivity figure is unchanged.
- No write another product's rules call owed at the opening can move a scored figure.
- Nothing regressed: all earlier closures and the revision_8 closing checklist hold.
- Gates: coordinator round-10 snapshot all OK (cited); not re-run by the auditor.

VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN
