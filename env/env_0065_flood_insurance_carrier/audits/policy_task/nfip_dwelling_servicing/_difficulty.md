# Policy-task audit — nfip_dwelling_servicing / charter-global

## charter_global_frozen
- Frozen: 2026-10-15T22:26Z, auditor: independent policy-task auditor (round 1, no prior revision).
- Hashes (sha256 prefix, verified equal to the coordinator snapshot): `dwelling.extended.yaml` 2bbcceeaa3b49db3; `task_tools.py` 8cc858ee248a5ae8; masked views 0.json 34edd24d4a7fb307, 1.json 6678acf0e5da404b.
- Read: blueprint/{blueprint.yaml headers, db_schema.json, share_tools.py, products/dwelling.yaml, products/homeflood.yaml (cross-category rules only)}, the extended charter, task_tools.py, the two masked views, erlbench DSL semantics (skills/erl-task-instantiate/scripts/check_compute.py build_env: RND = Python `round`, COUNT/SUM/LATEST scoped to the holding, CFIELD = first matching cross holding, MONTHS = whole months).
- Masked / not read before this section was written: tasks/nfip_dwelling_servicing/tasks/*.json, the difficulty worklog.md, every masked key (evaluation_criteria, computations, design_rationale, solvability_contract, prerequisite_closure, charter_scope, required_documents, db_closure). This section contains nothing derived from GT.
- Entry conditions: gate snapshot present (all instantiation gates OK; traceability miss = unlock tool-name provenance only; validate INVALID = documents 0, pre-render). Masked views present with hashes. Entry conditions met.
- Base copy: lines 1–1431 of the extended charter are byte-identical to blueprint/products/dwelling.yaml (diff empty).

### policy_conflict_scan
Seven extended policies, two problem trees:
- Tree A (renewal): `dwelling_ext_renewal_remittance` (pay_renewal_premium_abaf74a5, owner=user) ← `dwelling_ext_coverage_increase_charge` (bill_coverage_increase_e35332a0) ← `dwelling_ext_certificate_rerate_credit` (apply_elevation_certificate_36dc84dc); and ← `dwelling_ext_residence_redesignation_credit` (record_primary_residence_225abe6c).
- Tree B (replacement cancellation): `dwelling_ext_replacement_refund_payout` (disburse_premium_refund_739bd910) ← `dwelling_ext_replacement_cancellation_credit` (process_policy_cancellation_6794673f) ← `dwelling_ext_replacement_cancellation_date` (sign_cancellation_request_cbba569e, owner=user).
- Subjects overlap (rerate credit and residence credit both `[dwelling_rating_updated, dwelling_premium_credit]`; rerate credit and cancellation credit both compute `risk_premium_credit`) but every (target_tool, computes) pair is distinct, so no two policies claim one write. Scopes of the two trees are disjoint and together cover all seven policies (task-level scope confirmation is per task).
- Cross-policy conflicts found: see findings P2 (coverage-increase effective date vs inherited `dwelling_waiting_period`), P4 (refund payout vs inherited `dwelling_payment_application` / `dwelling_ec_rating` refund sentences), P6 (ICC lines vs tools and the base RFA sentences), P8 (inherited claim bar never applied by the cancellation-credit compute).

### rule_compute_equivalence
Mechanical sweep (every `compute_basis` quote, every `policy_source`, every `replaced_by`, every `baseline.rule` sentence searched verbatim in its own `rule`, whitespace-normalised): all verbatim except **`dwelling_ext_coverage_increase_charge.compute_basis.charged_days`** — the quote ends "…the submitter relief, the review relief and the renewal-bill relief." but the rule says "…less the desk relief, the certificate relief, the submitter relief and the review relief." (finding P1). Semantic sweep (rule ⇄ compute), all charter-wide:
- Rounding: every rule says "rounded half-up to the cent"; `RND` is Python `round` on binary floats (ties do not round up) — finding P3.
- Inventions in compute with no rule basis: CI `charged_days: MX(0, …)` and `risk_rise: MX(0, …)` (rule states no floor); cancellation-credit `claims_days` adds `original_effective_date < term_start` (rule: "2 when no flood claim … in the last 60 months has been paid" — a first-term policy gets 2 by rule, 0 by compute); `debit_days` adds `risk_charge > 0`; cancellation-date `anchor_date` adds `replacing_effective <= NOW`; renewal `residence_pool` and payout `overpay_amount` apply `RND(x/2, 2)` where the rule states no rounding — finding P9.
- Claim counts: every "flood claim … has been paid" is computed as COUNT of `dwelling_claim_paid` event rows (payments, voids ignored), while the base measure `dwelling_msr_term_claims_paid` counts distinct claim_number with net payment above zero — finding P7.
- Unscoped / first-match reads: finding P11.
- Factor ladders: every tier named in `factors[].ladder` is stated in its rule and is a branch of its `decides` binding, and every branch of each `decides` binding is a rule tier (no tier lives only in compute).

### action_binding_and_uuids
- (target_tool, computes) unique per policy (7 pairs, 7 tools). Each tool performs only its write, validates nothing, refuses nothing (function bodies read: no status/prerequisite checks, no error paths).
- Docstrings: no ordering word, no other tool named, no sequence position; no numeric example values (no docstring gold leak).
- uuid8 tails 36dc84dc, e35332a0, 225abe6c, abaf74a5, cbba569e, 6794673f, 739bd910: distinct, no shared prefix or sequence pattern — independently generated.
- Arguments with no computing policy and their rule source: `reserve_fund_credit` / `reserve_fund_charge` (rule: reserve fund % of the risk line, half-up) — sourced; cancellation `reserve_fund_credit`/`hfiaa_credit` (credit-base rule per line) — sourced; `payee` (base payment_application) — sourced; `payment_method` (persona) — sourced; `cancellation_reason`/`supporting_document` (base cancellation_refund reasons/documents) — sourced; **`rerate_effective_date` — no in-force sentence states it** (finding P5); `change_effective_date` (CI effective date rule) — sourced but contested (P2).

### prerequisite_graph
Every policy has `prerequisite` (three `[]`). Edges: CI→rerate (value_input, gate rated_now), renewal→CI (value_input, collected_increase), renewal→residence (value_input, surcharge_next), credit→date (value_input, cancel_date), payout→credit (value_input, cancel_credits). All `problem` ids are extended policies in this file, none self, graph acyclic. Every `policy_source` verbatim in its own rule; all `form: state`, no `fallback_reason` (correct). `resolved_by` = the depended-on policy's target_tool in all five; each `gate` names an existing compute binding. `condition` vs sentence: renewal→residence condition adds "with the re-designation surcharge credit booked on the expiring term", stronger than the sentence ("the policy shows the residence designation …"); the one resolving write produces both, so no handling-time consequence — observation O1. No authoring-viewpoint phrasing.

### prerequisite_sentences
1. CI ← rerate: "The coverage-increase charge is fixed only after the policy's rated risk premium carries the certified first floor height of every Elevation Certificate received before the request was rated." Ordering connective "only after"; record-visible state (`dwelling_policies.ec_on_file`, `first_floor_height_ft`, `rated_risk_premium` vs the certificate rows); no tool/id. Only write that changes those fields from a certificate: apply_elevation_certificate (bill_coverage_increase writes the endorsement's figure, not a certificate's height). Single reading where one certificate was received before the request; "every … certificate" is broader than the `condition` ("the governing Elevation Certificate") when two were received before the request — observation O2 (not met in task 0, where one was).
2. renewal ← CI: "…fixed only after the premium account for the expiring term carries the charge for every coverage increase recorded during that term." State: ENDORSEMENT charges referencing each COVERAGE_INCREASE change row; one writer (bill_coverage_increase). PASS.
3. renewal ← residence: "…not fixed until the policy shows the residence designation the insured holds on the coming term start." State `dwelling_policies.primary_residence`; one writer (record_primary_residence). What the insured "holds" is not a field: it is derived from the customer's statement and the ended HomeFlood policy on the former home — reachable (persona answers when asked; HomeFlood record queryable). PASS with O1.
4. credit ← date: "The cancellation credit is fixed only after the policy carries the named insured's signed cancellation request stating the date the cancellation takes effect." One writer (sign_cancellation_request). PASS.
5. payout ← credit: "The premium refund is not paid out until the premium account carries the cancellation credits for the signed request it settles." One writer (process_policy_cancellation). PASS.
No rule restates another policy's sentence; no undeclared cross-problem order found in any extended rule. Base sentences stating order (e.g. cancellation "processed only on the named insured's signed cancellation request on file") ground no edge on their own — the extended rules carry their own sentences.

### override_declarations
Sentence sweep per `base_policy_refs` (and inherited base policies the extended quantity touches):
- rerate credit vs `dwelling_ec_rating`: pro-rata clause declared. Undeclared: base "the RESERVE_FUND_ASSESSMENT credit is reserve_fund_assessment_pct of those two pro rata credits" vs extended "reserve fund assessment percentage of the risk premium credit" (diverges whenever an ICC credit exists) — P6. Declared clause also removes "An applied certificate takes effect on the date it is received" with no replacement — P5. Scope phrase "whose certificate is applied at the servicing desk" holds of every application (all go through the desk tool) — observation O3. `dwelling_cancellation_refund`, `dwelling_nullification` refs: no sentence followed or contradicted (decorative refs, O4).
- CI vs `dwelling_endorsement_premium`: pro-rata clause declared; RFA-on-two-components sentence undeclared conflict (P6). Inherited `dwelling_waiting_period` (not in refs): "take effect … after the date the signed application (or endorsement request) and the full premium are received", "The loan-transaction exception applies only when the application and full premium are received no later than the date the loan closes", "When both exceptions could apply, the one giving the earlier effective date is recorded" — all contradicted by the extended effective-date rule/compute without declaration — P2.
- residence vs `dwelling_premium_components`: HFIAA-never-on-endorsement sentence declared; rest followed. Base refs ec_rating/cancellation_refund/nullification decorative (O4).
- renewal vs `dwelling_renewal`, `dwelling_ec_rating`: both conflicts declared with scope tails. `dwelling_payment_application` "applied to the policy and term named on the payment" vs the remittance collecting the expiring term's increase inside a coming-term payment — ledger allocation only, no scored consequence (O5).
- cancellation date vs `dwelling_cancellation_refund`: declared, scope tail keeps base date rule for the other three reasons.
- cancellation credit vs `dwelling_cancellation_refund`: PRO_RATA clause declared (drops the ICC line by declaration — realism O6). Inherited claim bar ("No refund at all is due for the current term under the reasons in claim_bar_reasons when a claim … has been paid … or is still open") never applied by the compute — P8.
- payout vs `dwelling_cancellation_refund`: declared. Undeclared vs `dwelling_payment_application` ("When the amount received exceeds the total due, the excess is refunded to the payor"; "Every refund is paid to the payor of record") and vs `dwelling_ec_rating` ("The credit is refunded to the payor of record", overwritten only for the renewal remittance) — P4.

### factor_ladders
Declared counts (all within 4–6, ≥2 parameter, ≥1 method as labelled): rerate 6 (3m/3p; cross: relocation→homeflood), CI 6 (1m/5p; no cross), residence 6 (1m/5p; cross: residence_start, former_home→homeflood), renewal 6 (4m/2p; no cross), date 4 (1m/3p; cross: anchor, backdate, lead→homeflood), credit 5 (2m/3p), payout 4 (2m/2p). Multi-source tiers exist (e.g. backdating: claims × payor; lender allowance: mortgage flag × payment rows; increase_limit: claims × zone; backdate window: HomeFlood ledger × dwelling claims). Cross-difficulty factors exist in each tree (tree A: relocation, residence_start, former_home; tree B: anchor, backdate, lead). Bindings disjoint; every `decides` is an intermediate, never `result`; every ladder ≥3 tiers stated in the rule.
Structural failures (findings F1–F4, F6, F7): realism of conditions/outcomes (F1), duplicated tiers (F2), mislabels (F3), incoherent baselines (F4), assembly sentences (F6), a tier read off a field that does not carry the stated condition (F7). After striking failing factors, every computation falls below 4 surviving factors (detail in F1).

### findings
Each: verdict — symptom — root cause/evidence — demonstrated consequence — location — tasks.

**P1 SOURCE-POLICY RED** — CI charged-days sentence omits a relief the compute subtracts. Rule: "The charged days are the days from the effective date to the term end less the desk relief, the certificate relief, the submitter relief and the review relief." compute: `charged_days: MX(0, effective_days - desk_relief - cert_relief - submitter_relief - review_relief - bill_relief)`; `compute_basis.charged_days` quotes a sentence that is not in the rule. A reader of the rule computes charged days without the renewal-bill relief while the rule also defines that relief (dangling). Consequence: two readings whenever the renewal-bill relief is non-zero (task 0: demonstrated there). Location: dwelling_ext_coverage_increase_charge rule / compute_basis.charged_days. Tasks: 0.

**P2 SOURCE-POLICY RED** — undeclared override of `dwelling_waiting_period`. Extended: "an increase whose request records a loan closing date and was received no later than that date takes effect on the loan closing date; … any other increase takes effect 30 days after receipt" (compute ignores premium receipt; picks loan-closing first). Base (not in base_policy_refs, not in overwrite): increases "take effect at 12:01 a.m. on the day that is standard_waiting_days calendar days after the date the signed application (or endorsement request) and the full premium are received"; "The loan-transaction exception applies only when the application and full premium are received no later than the date the loan closes"; "When both exceptions could apply, the one giving the earlier effective date is recorded". Same situation (increase request received before closing, increase premium not received by closing) → base: no loan exception and no standard date until premium received; extended: loan closing date. Same situation with both exceptions applicable and closing later than receipt+1 → base: day after receipt; compute: closing date. The renewal rule's "still unpaid when it took effect" presupposes the extended reading. Real NFIP practice requires premium receipt for an endorsement's waiting period. Tasks: 0 (demonstrated there).

**P3 SOURCE-POLICY RED** — rounding mode. Every extended rule states "rounded half-up to the cent"; `RND` = Python `round` on floats (a tie stored below .5 in binary rounds down; true ties round to even). Members: every `result` RND, rerate/CI/residence/credit/payout results, renewal `limited_figure`, `fund_next`, `carried_credit`; plus `RND(x/2,2)` in renewal `residence_pool` and payout `overpay_amount` where the rule states no rounding at all. Demonstrated on task 0 (`limited_figure`: 1021.37 × 1.25 = 1276.7125 → rule 1276.72, compute 1276.71).

**P4 SOURCE-POLICY RED** — refund payout contradicts in-force base refund sentences without declaring it. Payout rule: "The standard payout is the cancellation credits referencing the signed request alone"; overpayment "half the excess" when escrow paid last, "nothing otherwise" outside the window; re-rate part "nothing otherwise" outside the window. Base `dwelling_payment_application`: "When the amount received exceeds the total due, the excess is refunded to the payor in the same way as a cancellation refund … Every refund is paid to the payor of record"; base `dwelling_ec_rating`: "The credit is refunded to the payor of record" (overwritten only for the renewal remittance). The payout overwrite names only `dwelling_cancellation_refund`. Same situation (card overpayment posted 130 days before payout): base → refund the excess; extended → 0. Tasks: 1 (consequence there: the base reading reaches the gold-side number without any factor — see F4).

**P5 SOURCE-POLICY RED** — the rerate overwrite deletes the only sentence fixing the certificate's effective date. Superseded clause begins "An applied certificate takes effect on the date it is received"; `replaced_by` states only the credit. apply_elevation_certificate requires `rerate_effective_date` ("the date the certificate's rating change takes effect"). In-force text offers: superseded base (receipt date), the credit start rule (term start / survey date / receipt date), nothing else. Two defensible values whenever the credit start rule does not select the receipt date. The value is read back by CI `cert_applied_on` (≥ term start test). Tasks: 0.

**P6 SOURCE-POLICY RED** — ICC lines have no channel and the RFA sentences conflict with base. Rerate and CI rules: "the ICC premium line is credited/charged the same way only where the term carries an ICC premium"; tools have no ICC argument and overwrite `rated_icc_premium`; extended RFA = % of the risk line only vs base RFA = % of risk + ICC pro-rata amounts (base sentences not superseded). Hypothetical: Primary Single-Family policy with rated ICC 75 and certificate ICC 60 → rule promises an ICC credit no tool can post; base RFA ≠ extended RFA. Both tasks carry ICC 0 → no task consequence.

**P7 SOURCE-POLICY RED** — claim counts. Rule "flood claim(s) … paid"; compute COUNT of `dwelling_claim_paid` rows (a claim with building + contents payments counts twice; a fully voided payment still counts). Members: rerate `recent_paid_losses`, rerate `loss_paid_count`, CI `paid_recent`/`reported_recent`, residence `loss_paid`/`loss_reported`, renewal `paid_ten_years`, date `recent_claims`, credit `paid_claims`. Hypothetical: one claim paid in two items → renewal increase limit 25 % (compute) vs 20 % (rule). Not moving tasks 0/1 (each paid claim has one payment row; no voids).

**P8 SOURCE-POLICY RED** — dropped inherited branch. Base claim bar (REPLACED_BY_PRIVATE_FLOOD ∈ claim_bar_reasons: "No refund at all is due for the current term … when a claim with a date of loss in the current term has been paid … or is still open") is not superseded by the credit overwrite, yet the credit compute never yields 0 for it. Hypothetical: current-term claim open → base 0, compute positive. Task 1 has no claim → no task consequence.

**P9 SOURCE-POLICY RED** — compute conditions/floors with no rule basis (members listed in rule_compute_equivalence). Hypothetical demonstration: first-term policy, no claims → rule claims-free days 2, compute 0. No task consequence on 0/1.

**P11 SOURCE-POLICY RED** — unscoped / first-match reads without decoy guard. Members: rerate `loss_date` (latest reported claim only; an earlier qualifying current-term claim is ignored), `loss_paid_on` (latest payment of any claim, not of the claim at `loss_date`); renewal `cert_figure`, `increase_figure`, `increase_effective` (not limited to the expiring term); CFIELD first match among the customer's cancelled HomeFlood policies (rerate `former_home_*`, residence `former_reason/former_end/former_status`) instead of "the HomeFlood policy on a former home … sold"; residence `former_refunds` (XCOUNT over every HomeFlood policy, not the former home's). Hypothetical: two cancelled HomeFlood policies (one sold 3 months ago, one cancelled for another reason 2 years ago) → dict order decides the tier. No decoy of this kind is seeded in task 0/1.

**F1 SOURCE-FACTOR RED** — unreal ladders. NFIP premium, credits and refunds on a Write-Your-Own Dwelling Form are FEMA's (Flood Insurance Manual / SFIP); a WYO company cannot add or remove days of federal premium for its own servicing reasons, and no flood carrier keys a re-rate, endorsement, surcharge or refund day count to these conditions. Members (condition or outcome no such business weighs/publishes):
- rerate: `backdating_allowance` (7/21/0 days by claim history × payor), `relocation_allowance` (days for a former HomeFlood home sold), `review_allowance` (days for desk delay on federal premium), `loss_exclusion` (days between a later loss and its payment removed from a rating credit).
- CI: `desk_relief_rule`, `certificate_relief_rule`, `submitter_relief_rule`, `review_relief_rule` (claims history lowers endorsement premium), `bill_relief_rule` (renewal-bill timing).
- residence: `lender_allowance`, `bill_allowance`, `loss_allowance`, `former_home_allowance` (another policy's refund paid out), `tenure_allowance`.
- renewal: `increase_limit` (a WYO cannot raise the statutory annual cap; "exactly one paid claim → 20 %" and "zone other than X" are not statutory cap tiers), `certificate_pool_rule` (RFA credit forfeited by renewal-bill timing), `residence_pool_rule` (half of a credit for a withdrawn designation), `increase_collection` (RFA part of an unpaid charge forgiven by timing), `carry_share_rule` (half of a credit by payment channel).
- date: `anchor_rule` tier 2 (cancel the federal policy from a pending replacement's application date — a coverage gap no carrier sets), `debit_window_rule` (ACH vs card/check governing backdating).
- credit: `day_count_rule` (tier-1 condition "carries the private policy's declarations" holds of every customer lawfully reaching this write — base: "REPLACED_BY_PRIVATE_FLOOD needs the private policy's declarations"; tiers 2–3 describe cancellations base would not process), `debit_days_rule`, `claims_free_rule`, `tenure_days_rule`.
- payout: `overpay_rule` (half an escrow overpayment to the insured), `overpay_window_rule` and `rerate_window_rule` (money owed forfeited after a window).
Surviving factors per computation: rerate 2 (rerate_start, engine_figure_choice), CI 1 (effective_date_rule), residence 1 (residence_start_rule), renewal ≤1 (limit_base_rule, itself F2), date 2–3 (backdate_window_rule, lead_window_rule, anchor_rule tier 1 only), credit 0–1 (credit_base_rule, itself F2), payout 0 (rerate_rule F2). All below 4. Tasks: 0 and 1.

**F2 SOURCE-FACTOR RED** — tiers that select the same value/method. renewal `limit_base_rule` tier 2 ("the certificate's re-rated figure") vs fall-through ("the rated risk premium on the policy"): apply_elevation_certificate writes `rated_risk_premium = rerated_risk_premium`, so whenever tier 2's condition holds the two are one number. credit `credit_base_rule`: all four tiers are "charge + endorsement charges − re-rate credits" with zero terms dropped. payout `rerate_rule`: tier 1 is tier 2 with refund 0.

**F3 SOURCE-FACTOR RED** — mislabelled effect: renewal `residence_pool_rule` and payout `overpay_rule` (labelled method) select a multiplier 1 / 0.5 / 0 on one formula — parameter tiers.

**F4 SOURCE-FACTOR RED** — incoherent baselines. rerate `baseline.rule` says the drop uses "the full-term risk premium the rating engine returned with the applied certificate" and also "using the figure the engine returned with the certificate received most recently" — two figures when they differ (task 0). renewal `baseline.rule` says "limits the increase to the statutory annual percentage measured from the rated risk premium on the policy" while the compute baseline keeps `rise_on_top` (two fall-back numbers). payout `baseline.rule` ("cancellation credits … alone") contradicts in-force base refund sentences (P4); the in-force base reading is the full credit balance.

**F5** — per task (task 0 cross-category seed); see 0.md.

**F6 SOURCE-FACTOR RED (assembly class)** — rule sentences that assemble factor quantities by name (cannot live in a computation document silent about variation, nor in factor documents that reference nothing). Members: rerate "The credited days are the days of the credit start rule, or, when fewer, … plus the backdating allowance, the relocation allowance and the review allowance; the days of the loss exclusion are then taken out."; CI "The charged days are … less the desk relief, the certificate relief, the submitter relief and the review relief." and the effective-date sentence; residence "The residence days are the days of the residence start rule plus the lender allowance, the bill allowance, the loss allowance, the former-home allowance and the tenure allowance…"; renewal "The limited figure is the limit base increased by the increase limit…", "The carried credit is the certificate pool plus the residence pool, multiplied by the carry share…", "The renewal remittance is the renewal premium less the carried credit plus the collected increase…"; date "the requested cancellation date is the anchor date when it passes the backdating window, the lead window and the debit window…" and the three "passes … window" sentences; credit "The credited days are the counted days plus the debit days, the claims-free days and the tenure days…"; payout "The refund payout is the cancellation credits … plus the overpayment part and the re-rate part…".

**F7 SOURCE-FACTOR RED** — CI `submitter_relief_rule` tier "the request was sent by the mortgagee of record named on the policy" is read off `dwelling_changes.new_mortgagee_name` (the mortgagee named on the endorsement), a field that does not record who sent the request; no record field carries the sender. Tasks: 0 (second reading demonstrated there).

Observations: O1 renewal→residence condition stronger than its sentence; O2 "every Elevation Certificate" broader than "the governing" certificate; O3 vacuous "at the servicing desk" scopes (rerate, CI); O4 decorative base_policy_refs (rerate and residence cite cancellation_refund/nullification); O5 coming-term payment absorbs an expiring-term charge; O6 ICC premium not refunded on a HomeFlood-replacement cancellation (declared, unreal vs NFIP pro-rata practice); O7 renewal "ICC premium and Federal Policy Fee of the coming term are the figures rated for the expiring term" (declared; unreal — the renewal bill carries the coming term's figures).

## closing_checklist
Written after both reveals (2026-10-15T22:29Z+); nothing above this heading was changed after the reveals.
- Per-task files 0.md, 1.md correspond one-to-one with tasks/0.json, tasks/1.json; this file alongside; round 1, no older revision.
- Coverage: the two tasks' charter_scope (task 0: rerate, CI, residence, renewal + their four tools; task 1: date, credit, payout + their three tools) are disjoint and cover all seven extended policies; uuid8s independent (action_binding_and_uuids).
- Trees: task 0 n = 3 (3 value_input), user write = root payment; task 1 n = 2 (2 value_input), user write = signature; difficulty graph acyclic, no cross-task edge.
- Factors: NOT closed — F1 (realism) leaves every computation of both tasks below 4 surviving factors; F2, F3, F4, F6, F7 open.
- Policy: NOT closed — P1, P2, P3, P4, P5 carry demonstrated task consequences; P6, P7, P8, P9, P11 are charter-wide with hypothetical demonstrations.
- Instantiation gates were not re-run by this audit (input snapshot only); a re-run on the reworked form belongs to the next round.
- Difficulty does NOT pass the source-layer audit.

task0=SOURCE-POLICY/SOURCE-FACTOR/SOURCE-TASK RED task1=SOURCE-POLICY/SOURCE-FACTOR RED
charter=P1,P2,P3,P4,P5,P6,P7,P8,P9,P11,F1,F2,F3,F4,F6,F7

## revision_2

### charter_global_frozen (revision_2)
- Started 2026-10-16T10:31Z; this section written ~10:40Z, before any revision_2 task JSON or GT field was opened. Round-1 text above is untouched.
- GATE FIRST: worklog tail `REWORK round 2: gates 7/7 green` — met. Coordinator snapshot round 2 (run by me via /tmp/erl0065_coord/snapshot.sh): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID = documents 0 (pre-render). Hashes: `dwelling.extended.yaml` f5defc8f5e3725e3 (round 1: 2bbcceeaa3b49db3), `task_tools.py` 98508f4af3857fcc (round 1: 8cc858ee248a5ae8), masked views 0.json deb125116e35c458, 1.json 559853817f024ea3. Both shared inputs changed → every charter-global section re-derived in full.
- Read: the reworked charter (base lines 1–1431 still byte-identical to blueprint/products/dwelling.yaml), task_tools.py, the masked views, homeflood.yaml / db_schema.json enums, audits/XF_recipe.md, and only the `## REWORK round 2 claims` section of the worklog (claims by id; I verified each against the artifacts and did not rely on them).
- Shape change: the payout policy and `disburse_premium_refund_739bd910` are gone; `dwelling_ext_replacement_cancellation_credit` now computes `refund_amount` through process_policy_cancellation_6794673f (which now also pays the refund and takes `payee`); a new policy `dwelling_ext_insured_increase_charge` → `bill_insured_increase_9da169e7` (owner agent); bill_coverage_increase gains `endorsed_risk_premium`. Seven policies, seven tools.

### checks re-derived (revision_2)
- **Mechanical sweep** (every compute_basis quote, policy_source, replaced_by, baseline.rule sentence verbatim in its own rule): all verbatim.
- **Actions/uuids**: (target_tool, computes) unique; new tail 9da169e7 independent; tool bodies check nothing; docstrings carry no ordering words and no example values. New arguments sourced: `endorsed_risk_premium` ("the rated risk premium on the policy is raised by the rise"), `refund_amount`/`payee` (credit rule: "total of the cancellation credits plus any credit balance … paid to the payor of record"), `rerate_effective_date` ("takes effect on the date its credit runs from").
- **Prerequisite graph**: CI → rerate (state_gate, gate `dwelling_changes.ec_applied`), renewal → CI (value_input, outside_rise), renewal → residence (value_input, term_surcharge), credit → date (value_input, cancel_date), credit → insured increase (value_input, endo_risk). Acyclic; all sources verbatim in the blocked rule; `form: state` throughout; gates name existing bindings. Two writers can book an ENDORSEMENT charge on a coverage increase (bill_coverage_increase, bill_insured_increase), but the two policies' scopes ("recorded for a loan transaction" / "the insured requested with no loan transaction", read off `loan_closing_date`) leave one policy per request, so each state-form hop resolves to one write. CI→rerate condition adds "its re-rate credit is booked on the current term" beyond the sentence — same write, observation O8.
- **Overrides**: rerate (dwelling_ec_rating, scope "tier that carries no ICC coverage", base text restated for ICC tiers), CI and insured increase (dwelling_endorsement_premium and dwelling_waiting_period, each scoped and naming the sibling), residence (premium_components), renewal (dwelling_renewal, dwelling_ec_rating and dwelling_payment_application refund sentences), date (cancellation_refund date clause), credit (PRO_RATA clause; claim bar, refund methods by reason and lines now implemented) — declared. Residual undeclared conflicts with `dwelling_waiting_period`: see P2 below.

### round-1 RED status (revision_2)
| id | status | evidence |
|---|---|---|
| P1 | closed | relief terms gone; charged-days quote verbatim |
| P2 | **open (residual)** | premium receipt now governs (fixed); but base "When both exceptions could apply, the one giving the earlier effective date is recorded" is not superseded, while CI/insured compute take the loan anchor first (`has_closing` → wait 0) — loan request received 09-01, premium 09-01, closing 09-25, map revision 6 months earlier: base 09-02, compute 09-25. Base map window "no later than map_revision_window_months calendar months after … a receipt on the last day of the window qualifies" vs extended "fewer than 13 whole calendar months" (`MONTHS(...) < 13`): receipt exactly 13 months after → base qualifies, extended does not. Neither moves task 0/1 (no map revision recorded). |
| P3 | closed | `+ K('eps')` half-up nudge on every RND whose rule says half-up; halving terms removed; no tie in either world |
| P4 | closed | payout policy removed; refund = credits + held credit balance to payor of record, consistent with base payment_application / ec_rating |
| P5 | closed | "the certificate's rating change takes effect on the date its credit runs from" |
| P6 | **open (residual)** | credit lines rule returns "the current term's HFIAA surcharge and ICC premium … for the days from the cancellation date", but process_policy_cancellation has only an `hfiaa_credit` ("the cancellation credit on the HFIAA surcharge line") — an ICC-tier cancellation has no ICC line to post (credit policy is not ICC-scoped). The rerate/CI/insured ICC-tier paths keep base text whose ICC component no tool posts (observation). Not engaged in task 0/1 (ICC 0). |
| P7 | closed | claim tests read the latest claim net of voids / reports with payment or denial |
| P8 | closed | claim bar implemented (`claim_bars` → no days, no lines) |
| P9 | closed | every floor/condition in compute stated in rule ("never below zero", "not charged on this term", etc.) |
| P11 | **open (residual)** | (a) credit claim bar: "a flood claim with a date of loss in the current term has been paid net of voided payments" is tested only on the claim with the latest paid date of loss (`paid_latest_claim`) — an earlier current-term claim paid, the latest one fully voided → rule bars, compute does not; (b) rerate tie tier: "the one of those two with the lower figure governs" — compute takes the lower figure but reads the governing survey/received/diagram/elevation/height (`gov_*`) from the most recently received certificate, which need not be the lower-figure one. Hypothetical; neither world has these shapes. |
| F1 | **open (residual)** | see F1 below |
| F2 | **open (new members)** | see F2 below |
| F3 | closed | labels honest (fractions/windows parameter; methods change shape) |
| F4 | **open (new members)** | see F4 below |
| F5 | closed | HomeFlood 82a4b0a4: application 2019-06-04 + 14 = effective 2019-06-18; term 2025-06-18..2026-06-18 on anniversary; refund 450 × 128/365 = 157.81 recomputed |
| F6 | **open (residual)** | see F6 below |
| F7 | closed | closing window reads the lender named on the request (`new_mortgagee_name`) against the mortgagee of record — the field carries exactly that |

**F1 SOURCE-FACTOR RED (residual)** — FEMA sets when a federal premium credit, endorsement or surcharge refund takes effect; a WYO company does not key it to these, and no flood carrier weighs them for that quantity:
- rerate: `diagram_window_rule` (survey-to-receipt allowance by building diagram number), `elevation_window_rule` (by lowest-floor margin over BFE), `floor_height_window_rule` (by first floor height), `age_window_rule` (certificate age allowance by zone) — they decide whether the federal re-rate credit is backdated.
- CI: `closing_window_rule` (60 days when the request names the current mortgagee, 30 for another lender — lender identity does not change the statutory loan-transaction exception).
- residence: `refund_window_rule` (the sold home's HomeFlood payment plan), `closure_window_rule` (whether the sold home's HomeFlood policy was mortgage-required), `report_window_rule` and `proof_window_rule` (a flood claim's adjuster report and proof of loss on this policy dated after the sale are required as residence evidence — a customer with no flood claim can never get the occupancy credit).
- renewal: `cap_percentage_rule` tier 3 ("no cap applies when no premium payment is on record for the expiring term, because the policy then lapsed") — an in-force policy renewed before term end has not lapsed; no statutory category removes the cap.
Kept as company-schedule observations (carrier-controlled): CI premium and quote windows, renewal bill and term-end windows on the set-off, date backdating/lead/paid-up windows, breadth test (mirrors the "at least as broad" deductible criterion).
Surviving factors: rerate 2 (engine_figure_choice, rerate_anchor_rule), residence 2 (occupancy_rule, sale_window_rule) — below 4.

**F2 SOURCE-FACTOR RED** — tiers no customer reaching the write can occupy, or tiers that select one method:
- insured increase `anchor_rule_increase` tier 1 and `waiting_days_rule` tier 1 ("the request records a loan closing date …") — the policy is scoped to "a pending coverage increase the insured requested with no loan transaction"; both ladders keep two reachable tiers.
- CI `quote_window_rule` tier 2 ("it records none [no loan closing date]") — the policy is scoped to requests "recorded for a loan transaction".
- rerate `diagram_window_rule` tier 3 (every certificate carries diagram 1A–9; schema NONE is "on other documents") and `age_window_rule` tier 3 ("no zone recorded" — `flood_zone` enum has no empty value).
- date `lead_window_rule` tier 2 (STANDARD basis, 10 days): a STANDARD HomeFlood policy takes effect `standard_waiting_days` = 14 days after application and payment, so application→effective ≥ 14 > 10 — the tier always fails, the same outcome as the fall-through.
- renewal `cap_percentage_rule` tier 3 (unreachable for an in-force policy, see F1); renewal `setoff_rule` tiers 1 and 2 ("add the balance owed" / "set the credit balance against") are one method — add the signed ledger balance (`setoff: ledger_balance` in both).

**F4 SOURCE-FACTOR RED** — fall-through tier ≠ baseline, or a straw-man baseline:
- fall-through ≠ baseline: CI `loan_rise_basis_rule` and insured `rise_basis_rule` (fall-through "no rise", baseline `request_figure − rated_risk_premium`); insured `waiting_days_rule` (fall-through 30, baseline 0); renewal `cap_percentage_rule` (fall-through "no cap", baseline 25 %); renewal `term_surcharge_rule` (fall-through "the other HFIAA surcharge", baseline `prior_surcharge` = surcharges booked for the expiring term); residence `occupancy_rule` (fall-through "no credit", baseline the standard credit); date `breadth_rule` (fall-through 500, baseline 0); credit `returned_days_rule` (fall-through cancellation-to-term-end days, baseline the whole term), `endorsement_fraction_rule` (fall-through 0, baseline 1), `lines_rule` (fall-through "no line", baseline `term_other + term_fees`).
- straw-man baseline.rule: credit "The standard credit returns every component booked for the current term in full" (a pro-rata reason refunding the whole term and the fully earned fees — base itself says PRO_RATA); insured increase "runs from the request date to the term end, with no waiting period, and is made only when the premium was received on the request date" (the statutory 30-day wait is the standard; base dwelling_waiting_period); renewal "cap … at 25 percent" (base parameter annual_risk_premium_increase_cap_pct is 18 on every tier).

**F6 SOURCE-FACTOR RED (residual, XF recipe item 2)** — assembly sentences naming factor quantities: CI and insured "The effective-date rule: the increase takes effect the waiting days after its anchor date" (CI adds "when every request acceptance window of this policy is met"); renewal "the cap base is the rated risk premium on the policy less the rise kept outside the cap; the cap figure is the cap base increased by the annual cap percentage …, and the rise kept outside the cap is then added" and "The renewal premium is the sum …: that risk premium, …, the term surcharges and the Federal Policy Fee". (rerate, residence, date and credit now use generic "every … window of this policy" / "the part of the term the rules below give back" — closed there.)

**F8 SOURCE-FACTOR RED (new, XF recipe item 4)** — a factor's tier reads another factor's output: CI `loan_waiting_rule` tier 2 and insured `waiting_days_rule` tier 2 ("the policy's recorded map revision date falls fewer than 13 whole calendar months before **the anchor date**") read `anchor_date`, the output of `loan_anchor_rule` / `anchor_rule_increase`; insured `waiting_days_rule` tier 1 reads `has_closing`, a binding of `anchor_rule_increase`.

Observations (revision_2): O8 CI→rerate condition stronger than its sentence; O9 credit ← insured edge weighs 0.15 in task 1 (see 1.md); O4 kept (base refs); O7 kept, declared; the renewal rule repeats the set-off scope sentence twice (once per overwrite).

### closing_checklist (revision_2)
Written after the revision_2 reveals (2026-10-16T10:39:30Z); nothing in the revision_2 sections above was changed after the reveals.
- Per-task files carry revision_2 sections (frozen → comparison → findings); revision-1 text untouched.
- Coverage: task 0 claims rerate, CI, residence, renewal; task 1 claims date, credit, insured increase — disjoint and covering all seven policies; uuid8s independent.
- Trees: task 0 n = 3 (2 value_input + 1 state_gate, weight shown), task 1 n = 2 (2 value_input; one edge thin, O9); user writes present; difficulty graph acyclic.
- Scored values: blind derivations equal GT on every argument of both tasks; no second reading found → SOURCE-TASK PASS for both.
- Not closed: P2, P6, P11 residuals (charter-wide, hypothetical worlds), F1 residual, F2, F4, F6 residual, F8 (both tasks). Gate snapshot round 2 green (input only; not re-run by me beyond the coordinator script).
- Difficulty does NOT pass the source-layer audit in revision_2.

VERDICT revision_2: task0=SOURCE-FACTOR RED task1=SOURCE-FACTOR RED
charter=P2,P6,P11,F1,F2,F4,F6,F8

## revision_3

### charter_global_frozen (revision_3)
- Written before any round-3 task JSON / GT was opened (shell times recorded in the comparison sections). Revision 1–2 text untouched.
- GATE FIRST: worklog tail `REWORK round 3: gates 7/7 green` — met. Snapshot round 3 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID with documents 36 (pre-render state of the scenario; not this audit's object). Hashes: charter 3eead1de182f46d0, tools 6cbbb9dfb946d9ae, masked views 0.json 3763bfcd87444e38, 1.json 33bbdc1e84bd109b — both shared inputs changed → all charter-global checks re-derived. Base lines 1–1431 still byte-identical to the blueprint.
- Trees not re-treed (same seven policies, same five edges); both worlds changed (task 0: increase request 2026-09-23, increase premium 17.23 on 2026-09-24; task 1: map revision 2025-09-15 recorded, increase premium 52.23 on 2026-07-20). Fresh blind derivations run on both.
- Mechanical sweep: every compute_basis quote, policy_source, replaced_by and baseline.rule sentence verbatim in its rule. Tools: process_policy_cancellation now takes `icc_credit`; no tool checks anything; no ordering words or example values in docstrings; uuid8s unchanged and independent.

### round-2 RED status (revision_3)
| id | status | evidence |
|---|---|---|
| P2 | closed | CI and insured compute take the earlier dating (`dated_days = MX(anchor − wait, map_days)`); map window counted by adding calendar months with the last day qualifying (`MONTHS(receipt, revision) >= −13` checked at month-end and mid-month boundaries) |
| P6 | closed | `icc_credit` line on process_policy_cancellation; certificate/increase policies scoped to no-ICC tiers. Observation O10: the lines rule rounds HFIAA + ICC as one figure while the tool posts two lines (a cent can split differently on an ICC tier) |
| P11 | **open (residual)** | (a) rerate `request_window` tier 3 "the policy already shows an applied certificate **for the current term**" — `applied_count` counts applied certificates of any term (a prior-term certificate gives 0 days by compute, 30/60 by rule); (b) credit `paid_window_net` uses `within_months = MONTHS(term_start, NOW) + 1` by date of loss, which also admits a prior-term loss in the month band before the term start (task-1 calendar: term 2026-07-15, NOW 2026-10-13 → a loss dated 2026-07-14 counts and bars the refund; rule: "a date of loss in the current term"); (c) the claim windows of rerate, residence and renewal ("such a claim was reported and has a payment or a denial / … is still open") are decided on the latest-loss claim only; with two current-term claims, one closed and one open, both rule tiers hold and the compute picks one — the rule names no claim (the date policy's backdating window does: "the most recent of them") |
| F1 | **open (residual; the reworker's claim concedes it)** | rerate: `certificate_bill_window_rule` (certificate before/after the renewal bill), `certificate_payment_window_rule` (term premium paid), `certificate_claim_window_rule` (claim open/closed), `request_window_rule` (a coverage-increase request after the certificate) decide whether the federal re-rate credit is backdated — FEMA sets that; none of these is weighed for it. residence: `certificate_window_rule` (an Elevation Certificate received after the sale), `bill_window_rule_residence`, `payment_window_rule_residence`, `claim_window_rule_residence` are offered as "residence evidence" — none is evidence of where the insured lives. Surviving: rerate 2 (engine_figure_choice, rerate_anchor_rule), residence 2 (occupancy_rule, sale_window_rule) — below 4. Kept as company-schedule observations: CI premium/transaction/quote windows, insured premium/quote windows, renewal set-off windows (bill, term-end, claim), date windows. |
| F2 | **open (residual, small)** | rerate and residence payment windows, tier 3 "nothing has been paid on the current term": an in-force or pending NFIP policy always has a payment on its current term (full premium with application/renewal; pay_renewal books the payment to the coming term) — unreachable tier. Every other round-2 member closed: insured loan tiers removed, CI quote tiers both reachable in the loan scope, diagram/zone factors removed, lead window STANDARD 20 days ≥ HomeFlood's 14-day wait, renewal cap no longer a factor, set-off tiers now distinct (credit ≤ premium / credit > premium / nothing). |
| F4 | **open (residual; conceded)** | credit `returned_days_rule` (fall-through cancellation-to-term-end days, baseline whole term) and `lines_rule` (fall-through "no line", baseline `term_other + term_fees`); credit baseline.rule "The standard credit returns every component booked for the current term in full, endorsement charges included and re-rate credits left aside" remains a straw man for a PRO_RATA reason (base: PRO_RATA). All other factors: fall-through = baseline (checked one by one). |
| F6 | **open (residual, 1 member)** | CI "The dating rules: the waiting days are counted from the anchor date" — two factor quantities (`loan_anchor_rule` → anchor, `loan_waiting_rule` → waiting days) assembled by name. Closed elsewhere: insured ("counted from the receipt date" — one factor, plain date), renewal cap and premium sentences generic, rerate/residence/date/credit generic. |
| F8 | closed | waiting tiers read plain `has_closing`, `with_renewal`, `map_ok` bindings, never another factor's output |
| O8 | closed | CI→rerate condition = its sentence |
| O9 | closed | see 1.md (skip the increase: 536.92 vs 532.56) |

### new (revision_3)
**P12 SOURCE-POLICY RED (new, charter-wide)** — renewal set-off tier 2: "when the credit balance is larger than the renewal premium and the insured is the payor of record, nothing is remitted and the rest of the balance is refunded to the insured". The remittance becomes 0.00, but pay_renewal_premium takes "the amount paid … as a positive number", and no tool of this difficulty issues a stand-alone refund (disburse_premium_refund was removed; process_policy_cancellation refunds only with a cancellation). Hypothetical world: credit balance 2000.00, renewal premium 1664.08 → the rule requires a 335.92 refund and a zero remittance that no tool can execute. Neither task reaches this tier (task 0 credit 221.80 < premium).

### closing_checklist (revision_3)
Written after the revision_3 reveals (2026-10-16T12:01:35Z); revision_3 sections above unchanged after the reveal.
- Per-task files carry revision_3 (frozen → comparison → findings); older revisions untouched. Scopes disjoint and complete (task 0: rerate, CI, residence, renewal; task 1: date, credit, insured increase); uuid8s independent; graph acyclic; trees n = 3 (2 value_input + 1 weighted state_gate) and n = 2 (2 value_input); user writes present.
- Blind derivations equal GT on every argument of both tasks → SOURCE-TASK PASS both; SOURCE-CHAIN PASS both; no SOURCE-POLICY consequence on either world.
- Closed this round: P2, P6, F8, O8, O9; F2, F4, F6 reduced to the members listed.
- Open: P11 residual (3 members, hypothetical), P12 new (hypothetical), F1 residual (rerate and residence windows; both computations below 4 sound factors), F2 residual (payment-window tier 3, inside F1-struck factors), F4 residual (credit returned-days and lines baselines; straw-man credit baseline), F6 residual (CI dating sentence).
- Difficulty does NOT pass the source-layer audit in revision_3.

VERDICT revision_3: task0=SOURCE-FACTOR RED task1=SOURCE-FACTOR RED
charter=P11,P12,F1,F2,F4,F6

## revision_4

### charter_global_frozen (revision_4)
- Written before any round-4 task JSON / GT was opened. Revisions 1–3 untouched.
- GATE FIRST: worklog tail `REWORK round 4: gates 7/7 green` — met. Snapshot round 4 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID (documents 36) is the scenario's render state. Hashes: charter fe350be42588df33, tools ce8a2a1d63ba2a9c, 0.json 90e04b36167f132b, 1.json 2784904a8d036b07 — all changed → everything re-derived. Base lines 1–1431 byte-identical to the blueprint. Mechanical sweep (compute_basis, policy_source, replaced_by, baseline sentences): all verbatim.
- **Task 0 re-treed**: the certificate re-rate and residence policies and their tools (apply_elevation_certificate, record_primary_residence) are gone; new `dwelling_ext_contents_increase_charge` → `bill_contents_increase_55716379` and `dwelling_ext_deductible_decrease_charge` → `bill_deductible_decrease_87aa0055`; the building-limit increase keeps bill_coverage_increase_e35332a0. Tree: renewal ←vi deductible decrease ←vi contents increase ←vi building increase. Task 1 tree unchanged (credit ←vi date, credit ←vi insured increase). Seven policies, seven tools; uuid8 tails 55716379 and 87aa0055 independent; no tool judges anything; docstrings clean.
- Prerequisite sentences (new): contents "fixed only after the policy shows the building limit that the same loan transaction raised"; deductible "fixed only after the premium account carries the charge for every limit increase of the same loan transaction"; renewal "… carries the charge for every coverage change recorded during that term". State form, one writer per hop (each pending request is selected by exactly one policy: the building request leaves the contents limit unchanged, the contents request carries the building limit now on the policy, the deductible request is DEDUCTIBLE_DECREASE). Acyclic.
- Realism judged from scratch for the new factors: the three loan-closing endorsement policies use the statutory dating (loan-closing exception with premium by closing, map-revision 1-day exception within 13 months, renewal-premium dating, 30-day standard, earlier date when several apply), cumulative rise ("rated on top of" the prior request of the same closing) and company acceptance windows (premium, transaction, quote) — real or carrier-controlled. Renewal: outside-cap rise (RR2.0 cap excludes coverage-change increases), statutory 18 % / 25 % cap by residence category, HFIAA × probation surcharge, set-off and its windows (carrier-controlled). See F1 for the residence basis.

### round-3 RED status (revision_4)
| id | status | evidence |
|---|---|---|
| P11 | **open (residual, reframed)** | (a) closed (certificate policy removed); (c) closed (renewal claim window now names "the most recent of them, the one with the latest date of loss"). (b) rule and compute now agree ("either the paid claim with the latest date of loss on the policy has a date of loss in the current term and payments net of voided payments above zero, or the claim with the latest date of loss reported on the policy has a date of loss in the current term and neither a payment nor a denial on record"), but this narrows the in-force base claim bar — "No refund at all is due for the current term … when a claim with a date of loss in the current term has been paid (dwelling_msr_term_claims_paid above zero) or is still open (dwelling_msr_term_claims_open above zero)" — which the credit overwrite does not supersede. Same situation: current-term claim A (DOL 08-01) still open, later current-term claim B (DOL 09-01) denied → base: no refund (A open); extended: the latest reported claim B is closed and no paid claim → full refund. Undeclared override; hypothetical (task 1 has no claim). |
| P12 | closed | a credit balance larger than the renewal premium is scoped out in words and restated to the base refund clause. Observation O13: that base refund path has no tool in this difficulty (same as the base ICC paths noted earlier). |
| F1 | **open (residual, 1 member)** | renewal `term_surcharge_rule` (and the cap percentage that follows it): "the coming term is rated as the insured's primary residence when … either the policy is designated a primary residence or the insured's former home, insured with Tidemark under a HomeFlood policy, was cancelled because that home was sold before the coming term start, the closing of that sale standing as the residence documentation". The primary-residence category (HFIAA surcharge 25 vs 250; statutory cap 18 % vs 25 %) is a FEMA status that needs documentation that the insured lives at *this* building (FEMA's examples: driver's license, vehicle registration, voter registration, school records, or the insured's signed statement); a closing statement on the sale of a different home shows where the insured no longer lives, and here neither the designation nor any statement from the insured is recorded. The other F1 members of revision_3 are gone with the removed policies. |
| F2 | closed | payment-window members removed; new ladders reachable on recorded fields; set-off tiers distinct (subtract a credit ≤ premium / add a balance owed / nothing); credit lines tiers distinct |
| F4 | closed | credit baseline.rule = base PRO_RATA on the current term as booked; every credit factor's baseline = its fall-through (returned days to term end, fractions and lines at the term share); every endorsement, renewal, date and insured factor checked: fall-through = baseline. Observation O12: on task 1 (cancellation date before the term start) the term share is 390/365 > 1, so the baseline returns more than a line's charge (all-baseline 636.77) — definite and ≠ gold, but outside the fall-through's own domain. |
| F6 | closed | endorsement dating sentence generic ("the date the dating rules of this policy give; … the earlier effective date is recorded"); the anchor sentence describes only its own quantity |

New checks: no factor reads another factor's output (shared selections `has_closing`, `with_renewal`, `map_ok`, `prior_billed` are plain bindings); compute_basis verbatim; rounding half-up with eps nudge; no decoy-scope gaps found in the new reads (prior request selected by the same loan closing and contents/deductible fields; outside rise from the deductible decrease recorded last). Observation O14: task 0's seed carries no HomeFlood ledger rows for the cancelled HF1180336 (a PROPERTY_SOLD cancellation would book a refund under the homeflood charter); nothing in this charter reads them.

### closing_checklist (revision_4)
Written after the revision_4 reveal (2026-10-16T15:10:31Z); revision_4 sections above unchanged after it.
- Per-task files carry revision_4; older revisions untouched. Scopes disjoint and complete (task 0: building, contents, deductible, renewal; task 1: date, credit, insured increase); uuid8s independent; graph acyclic; trees n = 3 (3 value_input) and n = 2 (2 value_input); user writes present.
- Blind derivations equal GT on every argument of both tasks (task 0 freshly derived on the re-treed world).
- Closed this round: P12, F2, F4, F6, P11(a), P11(c). Open: P11 residual (credit claim bar narrower than the in-force base claim bar, undeclared; hypothetical world), F1 residual (renewal residence basis from a former-home sale; task 0).
- Task 1 passes all four relationships; task 0 does not; the difficulty does NOT pass the source-layer audit in revision_4.

VERDICT revision_4: task0=SOURCE-FACTOR RED task1=PASS
charter=P11,F1

## revision_5

### charter_global_frozen (revision_5)
- Written before any round-5 task JSON / GT was opened. Revisions 1–4 untouched.
- GATE FIRST: `REWORK round 5: gates 7/7 green` — met. Snapshot round 5 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID (documents 104) is the scenario's render state. Hashes: charter d4552c9d8f4d18f4 (changed), tools ce8a2a1d63ba2a9c (unchanged since round 4), 0.json 11e52e3714e2a69f (changed), 1.json 2784904a8d036b07 (unchanged). Charter-global sections re-derived; tool contract section carried forward (hash unchanged; still seven tools, nothing judged, docstrings clean). Base lines byte-identical. Mechanical sweep: all compute_basis / policy_source / replaced_by / baseline sentences verbatim.
- Trees unchanged (task 0: renewal ←vi deductible ←vi contents ←vi building; task 1: credit ←vi date, credit ←vi insured increase).

### round-4 RED status (revision_5)
| id | status | evidence |
|---|---|---|
| F1 | closed | the coming term is rated primary only on the recorded designation ("the designation being the record of the residence documentation the insured gave"); the HomeFlood sale now only dates the move for a current-term residence credit whose test ("a primary residence is the home the insured lives in for more than half of the term") follows FEMA's more-than-50 % definition. |
| P11 | **open (residual, one member)** | The route is stated and computed: whole-month placement of losses (inner months are provably on/after the term start because MONTHS is monotone; the boundary month is placed only through the latest paid / latest reported claim), a declared scoped overwrite of the base claim-bar clause that HOLDS the current-term return (refund booked zero, hold stated) for the residue the reading cannot place, and the base clause restated for every other cancellation. Barred and clear verdicts are sound against the base measures for paid claims (net per claim ≥ 0, so inner net > 0 ⇒ a paid claim exists; "clear" requires the latest paid loss before the term start). **But "open" is defined differently from the base measure**: the reading's "An open claim bars the refund when the claim with the latest date of loss reported on the policy has a date of loss on or after the term start and has neither payments net of voided payments above zero nor a denial on record", while the restated base clause uses `dwelling_msr_term_claims_open` = "claim_number values reported … that have neither a dwelling_claim_paid row nor a dwelling_claim_denied row on record". Probe (task-1 calendar, added claim DOL 2026-08-10 with a 500.00 payment and a 500.00 void, no denial): the reading says **barred** (compute: open_bar true → refund 0.00), which sends the case to "every other cancellation", where the restated base clause finds the claim neither paid (net 0) nor open (it has a paid row) → **refund due** (595.95 on that world). Two conclusions from the charter's own sentences. The other claim-status reads with this definition (renewal claim window, date backdating window, the credit's own open-clear test) are extended-only and conflict with nothing. Not engaged on task 1 (no claims). |

### new (revision_5)
**P13 SOURCE-POLICY RED (new; task 0)** — the residence credit is promised as a booking that no write performs. Overwrite/rule: "the current term's HFIAA surcharge is reduced by the residence credit of this policy and the credit is deducted from the remittance". record_primary_residence (the only tool that ever posted an HFIAA re-rate credit) was removed in round 4; pay_renewal_premium only creates one payment row; no tool of this difficulty posts an HFIAA credit. Consequence on task 0: the remittance is reduced by 162.74 but the expiring term's HFIAA charge stays 250.00 on the ledger, so after the gold payment and the coming term's booking the account owes exactly 162.74 — the reduction the rule states never reaches the record, and the terminal state the policy describes is unreachable by any tool sequence.

### second-record class sweep (revision_5, one pass)
Checked every read for a second record of the same kind: endorsement selections (most recently recorded pending request; a later no-loan request makes the loan policy charge nothing and is billed by the insured-increase policy, whose selection now requires no loan closing date — stated in the rule); prior-request and billed-charge reads (same loan closing); payment reads (latest payment on the policy, renewal-premium dating separate); re-rate credit after the request; renewal bill (most recently issued for the coming term); deductible/increase recorded last; HomeFlood sale (latest PROPERTY_SOLD; other cancellations ignored); claim windows (latest-loss claim, named in the rule); date backdating window ("the most recent of them"); credit request (latest signed); increase most recently put into effect; applied certificate most recently recorded; term-scoped ledger sums. All rule-stated and computed alike. Remaining member of the class: the credit's "open claim" definition vs the base measure (P11 above).

Observations (revision_5): O15 a HOLD is stated only in conversation — process_policy_cancellation records no hold, so the held return is indistinguishable from a bar in the records (declared route, kept as observation); O16 the residence credit takes "the latest" PROPERTY_SOLD HomeFlood cancellation as the move date even if that sale is of a home other than the one the insured moved from (no such record in either world). O12, O13, O14 carried.

### closing_checklist (revision_5)
Written after the revision_5 reveal (2026-10-16T16:43:33Z); revision_5 sections above unchanged after it.
- Per-task files carry revision_5; older revisions untouched. Scopes disjoint and complete; uuid8s independent; graph acyclic; trees n = 3 (3 value_input) and n = 2 (2 value_input); user writes present; blind derivations equal GT on every argument of both tasks.
- Closed this round: F1. Open: P11 residual (the credit reading's "open claim" — no net payment and no denial — is not the base measure's "no paid row and no denied row"; voided-payment probe gives barred vs refund due), P13 new (residence credit booked by no write; task 0).
- Task 1 passes; task 0 does not; the difficulty does NOT pass the source-layer audit in revision_5.

VERDICT revision_5: task0=SOURCE-POLICY RED task1=PASS
charter=P11,P13

## revision_6

### charter_global_frozen (revision_6)
- Written before any round-6 task JSON / GT was opened. Revisions 1–5 untouched.
- GATE FIRST: `REWORK round 6: gates 7/7 green` — met. Snapshot round 6 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID (documents 104) is the scenario render state. Hashes: charter d935d45f1b510cc8, tools e81be49e1d3478c7, 0.json 846c48b18de8ebad (all changed), 1.json 2784904a8d036b07 (unchanged). Charter-global sections re-derived. Base lines byte-identical; mechanical sweep (compute_basis, policy_source, replaced_by, baseline sentences): all verbatim; trees unchanged.
- Tool change: pay_renewal_premium_abaf74a5 takes `residence_credit` and, when positive, books it as an RERATE credit on the current term's HFIAA line before posting the payment; no other tool changed; no tool judges anything; docstrings carry no ordering words or example values.

### round-5 RED status (revision_6)
| id | status | evidence |
|---|---|---|
| P11 | closed | the open-claim test is now the base measure ("neither a payment nor a denial on record, as the base open-claim measure counts it"; compute: no paid row and no denied row) in the credit's open bar and open-clear test, the renewal claim window and the date policy's backdating window. Soundness re-checked: open bar ⇒ the latest current-term claim is open by the base measure; open-clear ⇒ no current-term open claim (all claims before the term start, or the single claim of the whole-month window plus boundary month has a paid or denied row); paid bar/clear unchanged and sound; the residue is HELD by a declared scoped overwrite. Probes on task 1's world: current-term claim paid 500.00 then voided 500.00 → neither barred nor held → refund 595.95 (base: neither paid net nor open → refund due — same); current-term claim reported with no payment or denial → barred → 0.00 (base: open → no refund — same). Whole "second record" class: no member left. |
| P13 | closed | "the credit being booked with the remittance as a re-rate credit on the current term's HFIAA surcharge line and deducted from the remittance" — pay_renewal_premium books it (RERATE, HFIAA_SURCHARGE, current term_start). Task 0 ledger: −47.62 before the payment, −1734.88 after the credit and the payment = the coming term's premium paid in advance; nothing left unbooked. Persona covers the entry ("entering any credit figure the representative tells you to enter exactly as given"). Observation O17: an insurer-side credit is posted through the customer-owned payment write (a modelling choice: the credit travels with the remittance it reduces); the customer only keys the figure the agent states. |

New-defect sweep: no new factor, edge or read; XF recipe classes re-checked on the changed sentences (renewal residence-credit sentence and claim-test sentences): generic assembly, no factor reads another, fall-through = baseline, rounding half-up with eps, decoy reads scoped. Nothing regressed.

### closing_checklist (revision_6)
Written after the revision_6 reveal (2026-10-16T16:58:30Z); revision_6 sections above unchanged after it.
- Per-task files 0.md, 1.md carry revision_6; older revisions untouched; every comparison section of this revision carries PASS.
- Coverage: seven extended policies, task 0 (building, contents, deductible, renewal) and task 1 (date, credit, insured increase) disjoint and complete; seven tools with independent, frozen uuid8s; no tool judges a prerequisite.
- Trees: task 0 n = 3, 3 value_input; task 1 n = 2, 2 value_input; each has an owner=user write (renewal payment; cancellation signature); difficulty graph acyclic.
- Factors: every computation declares 4–6 factors with ≥ 2 parameter and ≥ 1 method; each task has multi-source and cross-difficulty (homeflood) factors; every factor bears weight against a baseline equal to its fall-through; ladders real (FEMA rules) or carrier-controlled; blind derivations equal GT on every argument of both tasks.
- Gates: round-6 coordinator snapshot all green (traceability: unlock tool-name provenance only, pre-render as the brief states).
- Observations carried (not grounds for rework): O12, O14, O15, O16, O17.
- The difficulty PASSES the source-layer audit in revision_6.

VERDICT revision_6: task0=PASS task1=PASS
charter=CLEAN

## revision_7

### charter_global_frozen (revision_7)
- Written before any round-7 task JSON / GT was opened. Revisions 1–6 untouched.
- GATE FIRST: `REWORK round 7: gates 7/7 green` — met. Snapshot round 7 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID (documents 155) is the scenario render state. Hashes: charter 5f9b12709e04b35a (changed), tools e81be49e1d3478c7 (unchanged since round 6 → tool-contract section carried forward), 0.json 846c48b18de8ebad (unchanged), 1.json e05ebd18c5ef1c6d (changed). Base lines byte-identical; mechanical sweep (compute_basis, policy_source, replaced_by, baseline sentences): all verbatim. Factor-independence sweep (every factor binding's expression scanned for any other factor's bindings): no cross reads. Trees unchanged.
- This round verifies the renderer's findings (audits/render_source/nfip_dwelling_servicing/render_r1.md) item by item, plus regression of revision_6.

### renderer findings (revision_7)
| item | status | evidence |
|---|---|---|
| 1 map-revision dating in compute, not in rule (building, contents, deductible) | closed | one dating per request: `dated_days = MX(0, anchor_days − wait_days)`; `map_days` and the earlier-of step removed; declared scoped overwrite of base "When both exceptions could apply, the one giving the earlier effective date is recorded": "the loan-transaction dating governs whenever it applies and the map-revision dating applies only to a request that neither the loan-transaction dating nor the renewal dating reaches". The insured-increase policy keeps "when more than one dating applies, the earlier" and its compute does exactly that (map tier first, renewal only when no map revision). |
| 2 windows/amounts measured from another factor's result | closed (structure) | endorsement and insured windows are limits between record dates (request→payment, request→closing, request→billing day / receipt date), each giving "no earlier than the standard dating"; "the effective date is the latest of the dates the dating and limit rules give" (`MN(dated, limits)`). Date policy: backdating measured from the replacing policy's effective date (a record), each limit dates the request no earlier than the signing date, result = latest of the dates; breadth is now an explicit limit. Renewal: windows are floors in a stated order ("adjustments first, then limits, then the credits booked with the remittance"); set-off reads only the account; baseline and cap rule name no factor quantity; the outside-cap rise states its own effect. **But see F1-new below for the loan quote window's new measure.** |
| 3 claim-bar reading used only by factors | closed | the bar/hold now sits in the baseline ("no credit at all is returned when a claim bars the refund or the return is held") and in `result`; refund-method and lines factors carry no bar tier; refund-method (inception / current term in full / term share) replaces returned-days, fall-through = baseline (term share). |
| lower: ICC scope not computed | closed | all five scoped policies compute `P('icc_available') == False`, else 0 with the stated referral; probe (task-0 policy switched to the Primary Single-Family tier) → renewal 0, as stated. |
| lower: hold not recordable | closed | "no cancellation credit and no refund are booked with the cancellation" — expressible with the existing tool (credits 0, refund 0). |

### new (revision_7)
**F1 SOURCE-FACTOR RED (new members: `building_quote_window`, `contents_quote_window`, `deductible_quote_window`)** — the loan-closing quote window is now "measured from the request date to the day the request is billed … when the request is billed outside the window, the change may take effect no earlier than the standard dating" (`quote_limit` uses `DAYS(request_date, NOW)`). The day Tidemark bills is the carrier's own processing time: under the NFIP the effective date of a coverage increase follows the request, the premium receipt and the statutory loan-closing exception, and a WYO company's billing delay cannot strip a loan-closing exception the customer met (premium received 2026-09-24, before the 2026-09-25 closing) and push the federal coverage date back to receipt + 30. No flood carrier weighs its own billing lag for the effective date. (The insured-increase quote window measures request→premium receipt, a customer-side date — not a member.) Each of the three bears weight on task 0 (baseline → 3.16 / 0.53 / 0.79 instead of 14.60 / 2.43 / 3.65).

Regression of revision_6: P11 (base open-claim measure in the credit's bar and clear tests, renewal claim window, date backdating window) unchanged and sound; P13 (residence credit booked by pay_renewal_premium) unchanged; F1/F2/F4/F6/F8 earlier members stay closed.

### closing_checklist (revision_7)
Written after the revision_7 reveal (2026-10-17T14:48:08Z); revision_7 sections above unchanged after it.
- Renderer findings: items 1, 2, 3 and both lower items closed as the render file states them; blind derivations equal GT on every argument of both tasks; no regression of revision_6.
- Open: F1-new — the three loan-closing quote-window factors now measure to the carrier's billing day (task 0).
- Task 1 passes; task 0 does not; the difficulty does NOT pass the source-layer audit in revision_7.

VERDICT revision_7: task0=SOURCE-FACTOR RED task1=PASS
charter=F1

## revision_8

### charter_global_frozen (revision_8)
- Written before any round-8 task JSON / GT was opened. Revisions 1–7 untouched.
- GATE FIRST: `REWORK round 8: gates 7/7 green` — met. Snapshot round 8 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID (documents 279) is the scenario render state. Hashes: charter b4e4bf1bd0789bc6 (changed), tools e81be49e1d3478c7, 0.json 846c48b18de8ebad, 1.json e05ebd18c5ef1c6d (all unchanged since round 7 → tool-contract and world sections carried forward). Base lines byte-identical; mechanical sweep: all verbatim; factor-independence sweep: no factor binding reads another factor's bindings; trees unchanged.

### round-7 RED status (revision_8)
| id | status | evidence |
|---|---|---|
| F1 (loan quote windows) | closed | building, contents and deductible: "The quote window is measured from the request date to the receipt date … when the receipt date falls outside the window, the change may take effect no earlier than the standard dating"; compute `quote_limit: … DAYS(request_date, receipt_date) <= quote_window …` — customer/lender-side record dates only. Class sweep for carrier-side dates: the only `NOW` reads left are the renewal floors (the insured's remittance day), the cancellation date's limits and anchor (the insured's signing day) and the credit's month placement of losses (processing date, no effect on an effective date) — no member left. |

Render items (render_r1.md) re-verified: 1 one dating per request with the declared loan-dating overwrite — closed; 2 no window measured from a factor's result, limits/floors with stated order, baseline and cap rule name no factor quantity — closed; 3 claim bar in baseline/result — closed; ICC scope computed in the five scoped policies — closed; hold recordable — closed.
Regression: P11 base open-claim measure, P13 residence credit booked by the remittance, F2/F4/F6/F8 — all still closed. Observation O18: in the loan policies the premium window and the quote window now both measure request → premium receipt; each bears weight on task 0, and on any world the tighter one governs.

### closing_checklist (revision_8)
Written after the revision_8 reveal (2026-10-17T18:47:43Z); revision_8 sections above unchanged after it.
- Per-task files carry revision_8; older revisions untouched; both comparison sections carry PASS.
- Seven extended policies fully covered by the two disjoint task scopes; seven tools with independent frozen uuid8s; no tool judges a prerequisite.
- Trees: task 0 n = 3 (3 value_input), task 1 n = 2 (2 value_input); owner=user writes present (renewal payment, cancellation signature); graph acyclic.
- Factors: 4–6 per computation with ≥ 2 parameter and ≥ 1 method; multi-source and cross-difficulty (homeflood) factors in both tasks; every factor bears weight against a baseline equal to its fall-through; ladders are FEMA rules or carrier-controlled, and no ladder reads a carrier-side processing date.
- Render items (render_r1.md) all closed; no regression of earlier verdicts; round-8 gate snapshot all green (traceability: unlock tool-name provenance only, pre-render).
- Observations carried (not grounds for rework): O12, O14, O15/hold, O16, O17, O18.
- The difficulty PASSES the source-layer audit in revision_8.

VERDICT revision_8: task0=PASS task1=PASS
charter=CLEAN

## revision_9

### charter_global_frozen (revision_9)
- Written before any round-9 task JSON / GT was opened. Revisions 1–8 untouched.
- GATE FIRST: `REWORK round 9: gates 7/7 green` — met. Snapshot round 9 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate INVALID (documents 279) is the scenario render state. Hashes: charter c09a482e0ff2da38 (changed), tools e81be49e1d3478c7, 0.json 846c48b18de8ebad, 1.json e05ebd18c5ef1c6d (unchanged). Base lines byte-identical; mechanical sweep: all verbatim; compute_basis keys = compute bindings, every factor binding and gate exists; factor-independence sweep clean; trees unchanged; compute unchanged in effect (all scored figures and sensitivities reproduce revision_8 exactly).

### renderer round-2 mismatches (revision_9)
| item | status | evidence |
|---|---|---|
| A cancellation credit names a removed "returned-days rule" | closed | rule, baseline.rule and overwrite[0].replaced_by now read "the risk premium and reserve fund assessment charges are returned as the refund-method rule of this policy states, the HFIAA surcharge and ICC premium as the lines rule of this policy states, and each endorsement charge and re-rate credit of the term is taken back in the part this policy's fractions give"; both rules are defined in the policy; prerequisite effect text says "the refund method, both fractions and the lines". |
| B loan policies' closing effective-date sentence omits the limit rules | closed | building, contents and deductible now say "The change takes effect on the latest of the dates the dating and limit rules give", matching "The effective date is the latest of the dates the dating and limit rules of this policy give" and `MN(dated_days, premium_limit, transaction_limit, quote_limit)`. |

Class sweep (sentences naming removed rules or bindings): every rule, baseline, replaced_by, prerequisite source/condition/effect and ladder text scanned for the retired vocabulary (returned days / returned-days rule, acceptance windows, billing-day measure, "the dating rules give", credit start rule, governing certificate, occupancy rule, evidence windows, re-designation, gated set-off, "effective date the exception gives", stated-only hold): none present. Every "the X rule" a sentence names is either a base rule or defined in its own policy (anchor, rise, cap, set-off, replacement date, refund-method, lines, dating). No member left.
Regression: render_r1 items 1–3 and lower items, P11, P13, F1 (quote windows to premium receipt), F2/F4/F6/F8 — all still closed.

### closing_checklist (revision_9)
Written after the revision_9 reveal (2026-10-17T19:09:54Z); revision_9 sections above unchanged after it.
- Render mismatches A and B closed and the stale-reference class empty; render_r1 items and every earlier verdict remain closed; blind recomputations equal GT on every argument of both tasks; coverage, scope exclusivity, uuid8s, tree shape, owner=user writes and factor requirements as in revision_8; round-9 gate snapshot all green (traceability: unlock tool-name provenance only).
- Observations carried (not grounds for rework): O12, O14, O15, O16, O17, O18.
- The difficulty PASSES the source-layer audit in revision_9.

VERDICT revision_9: task0=PASS task1=PASS
charter=CLEAN

## revision_10

### charter_global_frozen (revision_10)
- Written before any round-10 task JSON / GT was opened. Revisions 1–9 untouched.
- GATE FIRST: `REWORK round 10: gates 7/7 green` — met. Snapshot round 10 (run by me): all gates OK; traceability miss = unlock tool-name provenance only; validate_scenario now VALID (documents 353). Hashes: charter 51e25f548d9988d7 (changed), tools e81be49e1d3478c7, 0.json 846c48b18de8ebad, 1.json e05ebd18c5ef1c6d (unchanged). Base lines byte-identical; mechanical sweep: all verbatim; scored figures and sensitivities reproduce revision_9 exactly.

### KB-audit item S1 (revision_10)
| item | status | evidence |
|---|---|---|
| S1 insured-increase rise lines out of compute order | closed | rule: "The rise rule: when the request carries no full-term risk premium from the rating engine, there is no rise; otherwise, when a re-rate credit from an applied Elevation Certificate was booked … ; otherwise …"; `rise_basis_rule` ladder in the same order (no figure → re-rate → standard); compute `0 if (request_figure == None or request_figure <= 0) else (… rerate … else …)` — one first-match reading. |
| K1 (source check) | no source defect | the three loan policies' replaced_by for the base earlier-effective-date clause names the sibling loan kinds and the no-loan insured requests before restating the base clause — complete in the source. |

Class sweep (tier order vs compute precedence, every factor whose tiers can overlap): rise in all four endorsement policies (figure-first, then prior-request where present, then re-rate, then standard), loan anchors (closing before renewal), waiting days (loan/renewal before map in the loan policies; map before renewal in the insured policy, matching its "earlier dating" sentence), refund method and lines (inception reasons first), outside-cap rise (deductible decrease first) — rule order = compute order in each. No member left. Regression: every earlier closure (render_r1, render_r2 A/B, P11, P13, F1, F2/F4/F6/F8) stays closed.

### closing_checklist (revision_10)
Written after the revision_10 reveal (2026-10-17T20:12:01Z); revision_10 sections above unchanged after it.
- S1 closed in the source; tier-order class empty; K1 needs no source change; all earlier closures hold; blind recomputations equal GT on every argument of both tasks; coverage, scopes, uuid8s, tree shapes, owner=user writes and factor requirements as in revision_9; round-10 gate snapshot all green and validate_scenario VALID.
- Observations carried (not grounds for rework): O12, O14, O15, O16, O17, O18.
- The difficulty PASSES the source-layer audit in revision_10.

VERDICT revision_10: task0=PASS task1=PASS
charter=CLEAN
