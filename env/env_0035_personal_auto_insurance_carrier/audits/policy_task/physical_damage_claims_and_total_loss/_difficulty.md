# Policy-task audit — physical_damage_claims_and_total_loss / charter-global

## charter_global_frozen

- Scenario: env/env_0035_personal_auto_insurance_carrier, difficulty physical_damage_claims_and_total_loss, category physdmg, M = 2.
- Freeze hashes (verified by the auditor with sha256sum against both the conductor's view copies and the live files under tasks/physical_damage_claims_and_total_loss/; identical):
  - physdmg.extended.yaml 31c7dfbef5d32b8ae80e0d9efb375890d2d1ce4a688e522ab98f1220c198d73d
  - task_tools.py 7aa768357605d103e8aed8fb11632972578e6e7df6d8263aa9cc5e50cec0892f
  - task_0.view.json 100c6c3fa8888a6ccaaf5a60e15457362ca15235e148d64f07201c5cb87e47b2
  - task_1.view.json 34b48877a3946c1527e6fe36f643a85f0d5aec6dc1a934226909c11624122353
- Freeze time: 2026-10-05T10:52Z (written before any task's GT was opened). Auditor: independent erl-task-policy-audit run (not the authoring agent).
- Fields read: blueprint/blueprint.yaml (not needed beyond package names), blueprint/products/physdmg.yaml (base; verified byte-identical to lines 1-1225 of the extended file, the extended copy only adds one blank line), blueprint/products/auto.yaml, telematics.yaml, billing.yaml, rental.yaml, roadside.yaml (targeted greps for package parameters, reason codes and enums only), blueprint/db_schema.json, blueprint/share_tools.py, the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state only). For DSL semantics (LATEST/COUNT scoping, MONTHS, DAYS, RND) the evaluator source skills/erl-task-instantiate/scripts/check_compute.py lines 224-415 was read (source only; nothing executed; it holds no task data).
- Fields masked and not read before the freeze: everything in tasks/physical_damage_claims_and_total_loss/tasks/*.json beyond the views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the difficulty worklog.md, the scenario worklog.md, any previous audit. No recursive search was run over env/ or tasks/.
- Entry conditions (Step 0): gate snapshot /tmp/erl35_views/physical_damage_claims_and_total_loss/GATES.txt supplied with commands and output lines: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred (KB not published). Masked views and MANIFEST.sha256 supplied; hashes re-verified. Entry conditions met.

### policy_conflict_scan

Extended policies (5): physdmg_ext_accident_deductible (A, record_claim_acceptance_ec9cfb06 / deductible_amount, agent), physdmg_ext_surrender_settlement (S, accept_total_loss_settlement_c07cd979 / settlement_amount, user), physdmg_ext_loan_payoff_benefit (L, pay_loan_lease_payoff_8a830e94 / amount, agent), physdmg_ext_claim_free_credit (C, grant_claim_free_credit_c23d8d33 / amount, agent), physdmg_ext_kept_vehicle_settlement (K, keep_total_loss_vehicle_b04c3b51 / settlement_amount, user).

Overlap-by-overlap:
- A vs base physdmg_claim_coverage / physdmg_evt_deductible / physdmg_agg_occurrence_deductible / physdmg_newly_acquired_vehicle: A restricts itself to "a claim that is the only claim of its occurrence" and defers multi-vehicle occurrences to the base one-deductible rule — no overlap left. A's newly-acquired sentence ("When the loss date falls before the date physical damage took effect...") only runs on accepted claims; base newly-acquired coverage conditions decide whether the claim is covered at all, so no conflicting conclusion.
- S vs K: mutually exclusive by settlement option ("a vehicle the customer keeps is settled under the kept-vehicle rules instead" / "a vehicle surrendered to Cardinal is settled under the surrender rules instead"). They treat the same Deductible Rewards balance differently (S weights it by package and earned claim-free credits; K applies it dollar for dollar) — each is declared against base Step 4 or follows it; no single situation reaches both.
- S vs L: L reads S's accepted figure and the decided deductible. L's "excluded deductible" is the decided deductible on the accepted coverage decision, not the deductible actually charged in S after S's total-loss deductible waiver and Deductible Rewards weighting. On a non-Premier package where S's waiver or credit lowered the charge, L removes from the shortfall a deductible amount that the settlement never deducted (see findings O-7). No task world reaches it (task 0 is Premier: excluded deductible 0).
- A vs S: A's repeat-claim surcharge and S's total-loss deductible waiver both read "claims closed as paid within the last 36 months" on the coverage; S applies its share to A's recorded figure. Sequential, compatible.
- C vs K: C raises deductible_credit_balance; K reads it. Compatible; C is K's declared prerequisite.
- K vs base physdmg_total_loss new-car-replacement sentence: undeclared override (finding P-1).
- Cross-category read boundaries: every cross read is a read (auto policies/transactions, telematics enrollments, billing accounts/ledger); no extended policy writes another category.
- Terminal states: A creates one accepted coverage decision; S and K each create one accepted settlement row with title_received False; L creates one loan_lease_payoff claim payment; C creates one claim_free_year credit row and raises the balance. No two policies write the same row or field except C (balance) which no other extended write touches.
- Claimed scopes (inferred from the views and the charter before reveal; to be confirmed at reveal): task 0 = {A, S, L} (customer asks for the loan payoff payment), task 1 = {C, K} (customer keeps the hail-totalled truck). Pairwise disjoint, jointly complete over the 5 extended policies.

### rule_compute_equivalence

Swept binding by binding against compute_basis and back against the rule prose.

- A: every binding has a verbatim basis; ladder tiers of all four factors are rule sentences and branches of their decides bindings. Drifts without world consequence: (a) option_deductible uses the current variant (P()), while inherited base Step 1 says "The option in force is the one effective on the loss date" — no deductible change in either world; (b) paid_claims counts physdmg_claim_closed rows (a claim reopened and re-closed paid would count twice) where the rule says "claims"; (c) RND is Python round(), the rule says half up — no .xx5 tie arises in either world (recomputed with Decimal ROUND_HALF_UP; identical).
- S: all bindings grounded. The `result` basis quotes the composition sentence without the allowance while compute adds `allowance`; the rule's own allowance paragraph says it "is added to the surrender settlement", so not an empty promise and not an invented basis. sales_tax_pct/title_fee use K() copies whose values equal the variant's sales_tax_rate_by_state / title_fee_by_state (5.75/7.00/6.00/4.15/6.00; 15/15/9/15/15) — equivalent.
- L: all bindings grounded; option_added implements "the vehicle's latest option change in the auto policy's transactions" literally (any option change of that vehicle, not specifically the loan/lease payoff option; see O-9).
- C: period_anchor implements the three-tier anchor plus the base anchor sentence exactly; credit_period_end (a tool argument, not a computed binding) follows the rule sentence "ends claim_free_months months later, on the same day of the month".
- K: all bindings grounded. The `result` basis is the composition sentence without the retitling allowance; compute adds retitle_allowance, grounded in the retitling paragraph whose wording ("on top of the kept-vehicle settlement") is the root of finding T-1 in 1.md.
- No compute binding invents a basis; no rule sentence of an extended policy is left unimplemented.

### action_binding_and_uuids

- (target_tool, computes) pairs: (record_claim_acceptance_ec9cfb06, deductible_amount) A; (accept_total_loss_settlement_c07cd979, settlement_amount) S; (pay_loan_lease_payoff_8a830e94, amount) L; (grant_claim_free_credit_c23d8d33, amount) C; (keep_total_loss_vehicle_b04c3b51, settlement_amount) K — each claimed once.
- Docstrings: no docstring names another tool, states a position in a sequence or carries before/after/first wording about another action ("as the claims desk gives it to the customer before the call" refers to the claim number, not to an action). No confirmation, review or wait is added.
- Function bodies validate nothing: each finds the claim report / coverage, rounds, creates one row (C also updates the balance) and returns a receipt. No prerequisite, eligibility or amount check (task_tools.py lines 36-46, 73-86, 108-120, 143-155, 178-189).
- uuid8s: ec9cfb06, c07cd979, 8a830e94, c23d8d33, b04c3b51 — five distinct values, no shared prefix or suffix, no sequential pattern. PASS.

### prerequisite_graph

- prerequisite filled on all five: A [] ; S [A] ; L [S] ; C [] ; K [C]. Every problem id names an extended policy in this file, never a base policy or itself. Graph A→S→L, C→K: acyclic.
- policy_source verbatim in the blocked policy's own rule: S "The surrender settlement is fixed only after the claim carries an accepted coverage decision stating its deductible." (rule, 2nd sentence); L "The loan or lease payoff benefit is not paid until the claim carries a surrender settlement the customer has accepted." (rule, 2nd sentence); K "The kept-vehicle settlement is not worked out until the vehicle's Deductible Rewards balance carries a credit for every completed claim-free year." (rule, 2nd sentence). All locatable.
- form state on all three; no fallback_reason, correctly absent.
- condition vs sentence: same strength and scope on all three (S: accepted decision with a deductible_amount; L: accepted surrender_to_cardinal row with the payoff; K: a claim_free_year entry for every year whose end date has passed and the balance including them).
- resolved_by = depended-on target_tool on all three; kind value_input with gate naming a real compute binding (decided_deductible, accepted_settlement, credit_balance).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field. PASS.

### prerequisite_sentences

Four-point test:
1. S edge: connective "only after"; waited-on state "the claim carries an accepted coverage decision stating its deductible" — record-visible (physdmg_claim_events coverage_decision accepted, deductible_amount), no actor, no tool, no id. Exactly one write of this difficulty creates a coverage decision: record_claim_acceptance_ec9cfb06 (its docstring: "Record the claims desk's decision accepting a reported physical damage claim ... and the deductible that applies"). Derivation: sentence + claim file (no decision on the claim) + A's rule ("The accepted-claim deductible is the deductible recorded when the desk accepts a reported claim") → A's write. Single reading.
2. L edge: connective "not ... until"; state "the claim carries a surrender settlement the customer has accepted" — physdmg_total_loss_settlements settlement_option surrender_to_cardinal, offer_status accepted. Only accept_total_loss_settlement_c07cd979 writes a surrender_to_cardinal row (keep_total_loss_vehicle_b04c3b51 writes owner_retained_salvage). Derivation: sentence + no settlement row + S's rule ("The surrender settlement is the net settlement a customer accepts when a total-loss vehicle and its title go to Cardinal") → S's user-owned write. Single reading.
3. K edge: connective "not ... until"; state "the vehicle's Deductible Rewards balance carries a credit for every completed claim-free year" — physdmg_payments claim_free_year entries and physdmg_coverages.deductible_credit_balance. Only grant_claim_free_credit_c23d8d33 adds such an entry. Derivation: sentence + credit history (latest year end) + C's rule ("Each claim-free year earns one credit ...") → C's write. Single reading.
- No rule restates another edge's sentence, names another problem's tool or id, or aggregates the chain; A's and C's rules (the depended-on rules) do not mention S or K.
- No undeclared cross-problem order in any extended rule. Base observation: physdmg_total_loss carries base cross-problem orders ("The settlement is paid only after the customer has accepted the settlement offer", "A loss payee is paid first ...") and physdmg_evt_repair_payment "A repair payment is issued only after the claim is accepted"; none of them grounds a declared edge of this difficulty (each edge has its own extended sentence), so they are recorded as observation O-11 only.
PASS.

### override_declarations

Sentence-by-sentence against base_policy_refs:

- A → physdmg_evt_deductible: lead-in "fixed in this order" — declared (overwrite 1). Step 1 base sentences — followed verbatim as the "option deductible". "The option in force is the one effective on the loss date" — inherited (compute drift noted above). Step 2 waiver — declared (overwrite 2), merged meaning unique (full waiver kept, partial tier added). Step 3 occurrence — deferred to base. Step 4 credit — untouched (A records the deductible before credit, consistent with the base field meaning "after waivers, before any Deductible Rewards credit"). "taken once per claim ... never from towing ..." — not A's quantity. The new cap / surcharge / DriveSense terms change the scored quantity relative to base Step 1; the base sentence that fixes how the steps combine is the one named, so declared. → A/physdmg_agg_occurrence_deductible, physdmg_newly_acquired_vehicle, physdmg_claim_coverage: followed.
- S → physdmg_total_loss: total-loss threshold and ACV-report sentences followed; the settlement composition sentence declared (overwrite 1) — covers prior damage, custom equipment, deductible charge and the added allowance; the new-car-replacement sentence declared (overwrite 2; age now counted from the vehicle's addition to the policy instead of acquisition date). Payment-timing, theft, buy-back, appraisal and removal sentences are not S's quantity. → physdmg_evt_deductible Step 4 declared (overwrite 3). PASS.
- L → physdmg_total_loss loan/lease payoff sentence declared (L's Premier tier puts the deductible back into the difference, which the named base sentence forbade). Other refs (repair payment, recovery, transportation, occurrence, deductible): followed or not L's quantity. PASS.
- C → physdmg_deductible_rewards: annual-credit/cap sentence and period sentences declared (two overwrites); enrollment, forfeiture and no-cash sentences followed. PASS.
- K → physdmg_total_loss: composition sentence declared. The new-car-replacement sentence ("Where the auto package has new_car_replacement_included true and the vehicle was bought new, is no more than new_car_replacement_max_age_months months past its acquisition date and has no more than new_car_replacement_max_miles miles at the loss, replacement_cost_new replaces actual cash value in the first step and no prior damage is deducted.") governs the first step of every total-loss settlement, owner-retained included, and K's rule replaces it with "The kept value is the actual cash value less the unrepaired prior damage noted" without naming it in overwrite — a dropped branch. FAIL → P-1.

### factor_ladders

Counts are given as declared / after the honesty tests.

A (4 factors; declared parameter 3, method 1):
- package_deductible_cap — parameter, decides package_cap, bindings {package, package_cap}; 3 tiers (Premier 500 / Preferred 750 / uncapped); single-source (auto variant); cross_difficulty auto. Rule states all tiers. Coincidence: Preferred 750 equals the uncapped option on the $750 option and Premier 500 on the $500 option — a cap that does not bind, acceptable for a cap. Realism: a package perk that caps the chosen deductible below the option rated with deductible_factor — unusual but customer-favourable; observation O-1.
- repeat_claim_surcharge — parameter, decides repeat_surcharge; tiers 250 / 100 / 0; single-source (claim history); not cross-difficulty. UNREAL LADDER (F-1).
- drivesense_deductible_discount — parameter; tiers 100 / 50 / 0; conjunction over one telematics row (status, final_score) — not multi-source; cross_difficulty telematics. Realism: safe-driving deductible reductions exist (vanishing-deductible programs reward safe driving); acceptable.
- uninsured_driver_waiver — labelled method; tiers multiply the combined figure by 0 / partial_waiver_share_pct (50 %) / 1. MISLABELLED: the tiers substitute a rate into one formula (F-2). Multi-source (loss cause on the claim report, collision_deductible_waiver on the coverage's option, fault row).
- After tests: method 0 → A fails "at least 1 method" (F-2); parameter 3 (repeat_claim_surcharge struck by F-1 leaves 2 + the relabelled waiver).

S (6 factors; declared parameter 4, method 2):
- replacement_cost_value — method; tiers replacement cost new / max(ACV, 75 % of RCN) / ACV; multi-source (auto package parameter, coverage inspection_due_date, auto_vehicle_add, TL declaration odometer); cross_difficulty auto. Honest method.
- prior_damage_already_paid — parameter; tiers max(noted, insured repair payments) / 0 / noted. Tier 1 introduces a different computation (a max over a second aggregate) — label borderline (observation O-3); realism of "the larger of" also O-3.
- package_custom_equipment_limit — parameter; tiers premier_custom_limit 3000 / preferred_custom_limit 2500 / option custom_equipment_limit (1000/1000/1500/1500/2500/5000 by option). UNREAL TIER and coinciding tiers (F-4).
- total_loss_deductible_waiver — parameter; tiers 0 / 75 % / 1; multi-source (auto inception, claim history); cross_difficulty auto. Tenure-plus-claim-free deductible waivers on total losses exist as loyalty features; acceptable.
- deductible_rewards_weighting — labelled method; tiers multiply the balance by 1.25 / 1.1 / 1. MISLABELLED (F-3). Multi-source (auto package, credit history).
- prompt_settlement_allowance — parameter; tiers 1.5 % / 0.75 % / 0; single-source (dates). Realism: a flat percentage keyed to days from report to acceptance only loosely mirrors prompt-payment interest, which runs from proof of loss; observation O-4.
- After tests: method 1 (replacement_cost_value), parameter ≥ 2; S passes the counts; F-3 and F-4 stand as individual REDs.

L (4 factors; declared parameter 3, method 1):
- payoff_to_loss_date — labelled method; tiers reduce the stated payoff by lease_rollback_pct 0.4 % or loan_rollback_pct 0.5 % per whole month, or by nothing. MISLABELLED: one formula stated_payoff × (1 − r × months) with r ∈ {0.4 %, 0.5 %, 0} (F-2 shape, recorded as F-5). Concept (measure the payoff as of the loss date) is real; the per-month flat rate is a stylisation (O-6).
- package_deductible_coverage — parameter; tiers 0 / 50 % / 100 % of the decided deductible; cross_difficulty auto. Realism acceptable (some loan/lease payoff products cover the deductible); but see O-7 on decided vs charged deductible.
- option_seasoning — parameter; tiers 50 % / 75 % / 100 % benefit share by whole months the option has been carried before the loss. UNREAL LADDER (F-6).
- tenure_credit — parameter; tiers +15 / +10 / +0 points added to the seasoning share by policy tenure. Its outcome exists only against F-6's share and policy tenure is not a quantity loan/lease payoff coverage weighs (F-6).
- After tests: method 0 → L fails "at least 1 method" (F-5); parameter count after F-6 strikes option_seasoning and tenure_credit = 1 (package_deductible_coverage) + relabelled payoff_to_loss_date = 2.

C (6 factors; declared parameter 5, method 1):
- non_restarting_claims — method; tiers: anchor stays at last credit end / restarts from loss date (other comprehensive) / restarts from payment date. Honest method (changes which record date anchors the period). Multi-source (estimate row, payments, recoveries, fault row). Realism: glass-repair and fully-subrogated not-at-fault claims not breaking the claim-free run is real practice; choosing loss date for comprehensive vs payment date for collision is invented but harmless (O-8).
- loyalty_escalator — parameter 150 / 125 / annual credit (100). Acceptable.
- package_credit_cap — parameter; Premier = option collision_deductible / Preferred = max + 100 / max credit. Premier tier equals fall-through on the $500 and $250 options (500=500, 250=250); distinct expressions coinciding on two options — observation O-8.
- drivesense_credit_bonus — parameter 50 / 25 / 0; single-row conjunction; cross_difficulty telematics.
- tenure_credit_bonus — parameter 25 / 10 / 0; cross_difficulty auto.
- payment_record_bonus — parameter 25 / 10 / 0; multi-source (billing account autopay flag + billing ledger returns); cross_difficulty billing. Realism: autopay perks are normally premium discounts, not deductible credits — unusual but customer-favourable (O-8).
- After tests: 6 factors, 5 parameter, 1 method, multi-source and cross-difficulty present. PASS structurally.

K (5 factors; declared parameter 3, method 2):
- salvage_value_basis — method; tiers 30 % of ACV (bid lapsed) / 25 % of ACV (bid below floor) / highest bid. Tiers 1-2 share a method with different rates, tier 3 is a different method — acceptable as method. Realism: a floor that deducts more than the highest salvage bid actually obtained is customer-adverse and departs from the base definition of salvage value ("Highest salvage bid"); some states require the owner-retained deduction to be the actual bid — observation O-5 (not raised to RED: estimated-salvage formulas exist in practice).
- kept_vehicle_loyalty_discount — parameter 20 % / 10 % / 0 on the salvage deduction. Invented perk; observation O-5.
- retained_equipment — parameter 0 / 50 % / 100 %; multi-source (drivable on the loss report, estimate and ACV on the declaration). Acceptable as a proxy for whether equipment survived on a kept vehicle.
- retitling_allowance — parameter 75 / 40 / 0 by state; cross_difficulty auto. Acceptable.
- kept_vehicle_tax_basis — method; tiers tax on (kept value − salvage deduction) / no tax (no vehicle added since the loss AND drivable) / tax on kept value. UNREAL LADDER (F-7).
- After tests: method 1 (salvage_value_basis) once F-7 strikes tax basis; parameter 3; counts still within bounds; F-7 stands as an individual RED.

Per-task aggregate (pre-reveal inference of scopes): task 0 {A, S, L} has multi-source factors (uninsured_driver_waiver, replacement_cost_value) and cross-difficulty factors (auto, telematics). Task 1 {C, K} has multi-source (payment_record_bonus, non_restarting_claims, retained_equipment, kept_vehicle_tax_basis) and cross-difficulty (auto, telematics, billing).

### findings

P-1 SOURCE-POLICY RED — undeclared override (dropped base branch) in physdmg_ext_kept_vehicle_settlement. Bears on task 1.
- Symptom: K values a kept vehicle at ACV in every case; base values a qualifying new vehicle at replacement cost new with no prior damage deducted.
- Root cause: K's overwrite names only the composition sentence of physdmg_total_loss; the separate base sentence "Where the auto package has new_car_replacement_included true and the vehicle was bought new, is no more than new_car_replacement_max_age_months months past its acquisition date and has no more than new_car_replacement_max_miles miles at the loss, replacement_cost_new replaces actual cash value in the first step and no prior damage is deducted." is not named, while K's rule says "The kept value is the actual cash value less the unrepaired prior damage noted, rounded to the cent." (S, by contrast, names that sentence in its overwrite 2.)
- Demonstrated consequence (same situation, two conclusions): Cardinal Auto Premier (new_car_replacement_included true), vehicle bought new 10 months before the loss, 8,000 miles, ACV 30,000, RCN 38,000, prior damage 500, customer keeps it: base first step = 38,000 with no prior damage; K kept value = 29,500. Two clauses rendered together in the KB fix the same quantity differently.
- Affected: physdmg.extended.yaml, physdmg_ext_kept_vehicle_settlement.overwrite / rule ("The kept value is ..."). Task 1's world does not reach it (2016 truck, 142,380 miles, $1,000 option on Premier: not bought new — inspection_due_date 2021-06-20 is set) — see 1.md.

F-1 SOURCE-FACTOR RED — unreal ladder: repeat_claim_surcharge (A). Bears on task 0.
- Tier values two_claim_surcharge 250 / one_claim_surcharge 100 are added at claim time to the deductible of the option the customer bought because of earlier paid claims. A US personal auto policy applies the deductible shown in the declarations; claim frequency is priced through premium (this scenario's own auto charter does exactly that: auto.yaml claim_free_discount_pct "no paid physical damage claim in the lookback"). No carrier publishes "your deductible on this claim is $100 higher because you had a paid claim last year"; the condition is one the line weighs for premium/underwriting, not for the deductible of a covered loss, and the outcome is a treatment no such business publishes.

F-2 SOURCE-FACTOR RED — mislabelled effect and no honest method factor: uninsured_driver_waiver (A). Bears on task 0.
- Its ladder ("multiplied by zero" / "multiplied by partial_waiver_share_pct percent" / "the combined figure stands") substitutes a share 0 / 0.50 / 1 into the single expression RND(MX(0, capped + surcharge − discount) × waiver_share, 2); that is a rate, i.e. a parameter. A's other three factors are parameters, so A declares no honest method factor (bound: at least 1).

F-3 SOURCE-FACTOR RED — mislabelled effect: deductible_rewards_weighting (S). Bears on task 0.
- Tiers multiply the credit balance by 1.25 / 1.1 / 1 inside one formula MN(RND(balance × weight, 2), charge) — a number substituted, labelled method. S keeps one honest method (replacement_cost_value), so S's counts still hold.

F-4 SOURCE-FACTOR RED — unreal tier outcome and coinciding tiers: package_custom_equipment_limit (S). Bears on task 0 (charter-level; task 0's world takes the Premier tier that raises 1,500 to 3,000).
- The Premier and Preferred tiers replace the option's custom_equipment_limit instead of raising it: on the $100 option (custom_equipment_limit 5000) a Premier policy is paid up to 3,000 and a Preferred policy up to 2,500, less than any lower package on the same option — a premium package cutting a limit the customer bought, which no carrier publishes. On the $250 option (limit 2500) the Preferred tier and the fall-through select the same value.

F-5 SOURCE-FACTOR RED — mislabelled effect and no honest method factor: payoff_to_loss_date (L). Bears on task 0.
- One formula stated_payoff × (1 − r/100 × months) with r = lease_rollback_pct 0.4, loan_rollback_pct 0.5, or 0 (used as stated): a rate substituted, labelled method. L's three other factors are parameters → L declares no honest method factor.

F-6 SOURCE-FACTOR RED — unreal ladder: option_seasoning and tenure_credit (L). Bears on task 0.
- option_seasoning pays 50 % of the loan/lease payoff benefit when the option was added under 3 months before the loss and 75 % under 12 months. Loan/lease payoff (gap) coverage pays the defined shortfall up to its cap once the option is in force on the loss date; carriers control anti-selection through eligibility (new vehicle, original owner, add-by deadline), not by prorating the benefit by how long the option has been carried. No carrier publishes a seasoning share for this benefit.
- tenure_credit adds 15/10 points of benefit share for auto-policy tenure; its only effect is to offset the unreal seasoning share, and policy tenure is not a quantity loan/lease payoff coverage weighs when settling the shortfall.

F-7 SOURCE-FACTOR RED — unreal ladder: kept_vehicle_tax_basis (K). Bears on task 1.
- Tier 2 makes sales tax on the kept vehicle depend on whether the truck "could be driven after the loss" — drivability is not a condition sales-tax reimbursement weighs anywhere (states that condition it look at whether a replacement vehicle is purchased, and otherwise pay tax on the ACV basis). The ladder also pays a not-replaced, undrivable vehicle tax on the full kept value while a customer who did buy a replacement is taxed on the smaller kept value less salvage — inverted relative to practice.

Observations (no RED):
- O-1 package_deductible_cap: a package cap below the option the deductible_factor was rated on — unusual product design, customer-favourable.
- O-2 (blueprint-level) physdmg charter physdmg_option_update has triggers [] while auto.yaml auto_coverage_change says physical damage options emit reason_code option_change; the seeded option_change row of task 0 follows the auto charter. Not this difficulty's artifact.
- O-3 prior_damage_already_paid: tier 1 deducts the larger of the noted prior damage and every repair payment ever made to the insured, presuming all insured-paid repairs went unrepaired — a punitive proxy for real "previously paid unrepaired damage" deductions; its tier 1 is a computation change labelled parameter (borderline).
- O-4 prompt_settlement_allowance keyed to report→acceptance days rather than to proof of loss.
- O-5 salvage floor above the actual highest bid, and the tenure discount on the salvage deduction — customer-adverse / invented respectively.
- O-6 payoff_to_loss_date flat per-month percentage and the "Leasing"-in-name test as a proxy for lessor vs lender.
- O-7 L excludes the decided deductible rather than the deductible charged in S; for a non-Premier policy where S's total-loss waiver or weighted credit lowered the charge, the shortfall is cut by deductible dollars the settlement never took (base: "the deductible ... never part of that difference" refers to the deductible actually taken). No task world reaches it.
- O-8 C: Premier credit-cap tier coincides with the fall-through on the $500/$250 options; autopay bonus on deductible credit; comprehensive-vs-other anchor dates — unusual, not demonstrable as a business impossibility.
- O-9 L option_added reads the vehicle's latest option change of any kind, not specifically the loan/lease payoff option; a later rental or roadside option change would be read as the payoff option's add date.
- O-10 RND is Python round() while every rule says half up; no tie in either world.
- O-11 base cross-problem orders in physdmg_total_loss / physdmg_evt_repair_payment ground no edge (each edge has its own extended sentence).
- O-12 K reads "the deductible stated on the claim's latest accepted coverage decision" but carries no prerequisite sentence on it (unlike S); in a world without the decision K's result is undefined. Task 1 seeds the decision.

## closing_checklist

Written 2026-10-05T11:00Z, after both comparisons (0.md, 1.md). Everything above this heading was on disk before any reveal and is unchanged.

The difficulty does NOT pass the source-layer audit; the close-out is not reached. Checklist state:
- Per-task files 0.md and 1.md correspond one-to-one with tasks 0-1; `_difficulty.md` alongside; first revision. Comparison verdicts: task 0 SOURCE-CHAIN RED + SOURCE-FACTOR RED (blind derivation = GT on every write); task 1 SOURCE-POLICY RED (P-1) + SOURCE-CHAIN RED + SOURCE-FACTOR RED + SOURCE-TASK RED (blind derivation = GT, but a second defensible figure exists). Not all PASS.
- Coverage and scope: 5 extended policies fully covered; charter_scope task 0 {accident_deductible, surrender_settlement, loan_payoff_benefit}, task 1 {claim_free_credit, kept_vehicle_settlement} — pairwise disjoint over whole trees; task tools closed; five independent uuid8s. PASS.
- Trees: task 0 two prerequisites, two value_input edges, user write accept_total_loss_settlement_c07cd979; task 1 one prerequisite, one value_input edge, user write keep_total_loss_vehicle_b04c3b51; difficulty-wide graph acyclic. Structure PASS; both tasks fail on the persona hint (C-1 in each file).
- Factors: every declared factor bears weight on its task's world against the declared baseline, and every all-baseline number differs from gold (750.00 / 29,635.83 / 5,024.02 / 0.00 / 12,189.00). Fails: F-1…F-7 (unreal ladders, mislabelled method factors leaving accident_deductible and loan_payoff_benefit with no honest method factor), K-NM (no near-miss in the kept-vehicle computation).
- Gate re-run on the final form: not performed — reserved for close-out once every relationship passes; the auditor edits no artifact and the artifacts are unchanged since the conductor's snapshot (hashes re-verified above).
- Cross-check of proof fields against the world: every figure in computations (expected, baseline_result, factor_sensitivity) and prerequisite_closure (why_false, flips_to_true_by, edge_load_bearing) matched the auditor's recomputation; the two no_user_hint sentences were contradicted by the personas (C-1 in 0.md and 1.md); the K near-miss claim in 1.json design_rationale does not qualify (K-NM).

## revision_2

### charter_global_frozen (revision 2)

- Inputs: /tmp/erl35_views/physical_damage_claims_and_total_loss.r2/ — hashes re-verified by the auditor against MANIFEST.sha256 and against the live files: physdmg.extended.yaml 2a64330330b93e081ad3f24bc08ddeb29f578f15dc7903d55abffed37b649fb3 (CHANGED from 31c7dfbe…), task_tools.py 7aa768357605d103e8aed8fb11632972578e6e7df6d8263aa9cc5e50cec0892f (UNCHANGED), task_0.view.json 1e593799…907e5b, task_1.view.json 6ed30f05…db81c0. Base section still byte-identical to blueprint/products/physdmg.yaml (lines 1-1225). Gate snapshot GATES.txt (r2): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred. Entry conditions met.
- Freeze time 2026-10-05T12:17Z, before any revision-2 task JSON was opened.
- Re-derivation scope: the charter changed, so every charter-global section is re-derived except § action_binding_and_uuids, whose only input (task_tools.py) is byte-identical — carried forward by reference on hash 7aa76835…. The rework's changes were located by a diff of the round-1 and round-2 charter copies (both conductor views).
- contamination_disclosure (revision 2): the auditor read the round-1 GT of both tasks during revision 1 (expected values, factor_sensitivity, closures). That knowledge concerns the superseded worlds and charter; the round-2 GT (tasks/*.json as reworked) is unread at this freeze. The reworker's claim list (item ids only) was supplied by the conductor and carries no figure.

### changes found (charter diff, round 1 → round 2)

- A (accident_deductible): repeat_claim_surcharge removed; new loyalty_deductible_reduction (tenure 120/60 months → −100/−50); DriveSense now drivesense_deductible_reduction, effect method (top: −20 % of the figure; middle: −50 flat; else none); uninsured_driver_waiver relabelled parameter, partial share 50 → 75 %, fault_rows guard added; "(half up)" dropped from the combination sentence.
- S: package_custom_equipment_limit now option limit + 2,000 (Premier) / + 1,000 (Preferred); deductible_rewards_weighting relabelled parameter; tl_waiver_partial_share_pct 75 → 80.
- L: option_seasoning and tenure_credit removed; payoff_to_loss_date rewritten (grace 10 days; lessor: rent charge by whole months, payoff × rate/12 × months; lender: simple interest by days, payoff × rate × days/365); new assumed_contract_rate (new ≤ 24 months 5.9 %, new older 6.9 %, used 9.4 %); new lien_release_charge (OH/IN 15, KY/WV 10, else 0) added outside the cap; benefit share removed.
- C: Preferred credit cap now preferred_cap_share_pct 75 % of the option's collision_deductible (was max credit + 100).
- K: new overwrite naming the base new-car-replacement sentence (owner-retained vehicle valued at ACV, with the stated reason); retitling allowance now "is added to the kept-vehicle settlement"; tax basis rewritten (replacement bought → tax on full kept value; no replacement and fewer than 30 days loss→acceptance → no tax with the settlement; otherwise tax on kept value less salvage deduction); baseline tax now on kept value less salvage deduction.

### policy_conflict_scan (revision 2)

Structure unchanged (A→S→L, C→K; S/K exclusive by option). Overlaps re-checked: A's tenure loyalty and S's total-loss waiver both read the inception date (sequential, compatible). O-7 (L excludes the decided, not the charged, deductible) persists. New observation O-13: L's lien-release charge is added "to the loan payoff benefit" even when the shortfall is 0.00, so a covered lender with no gap receives a 15.00 "loan payoff benefit". Scopes still {A,S,L} / {C,K} by inference.

### rule_compute_equivalence (revision 2)

- A: every new binding has a verbatim basis. The compute clamps after_loyalty at zero (MX(0, capped − loyalty)) while the rule places "never going below zero" after the DriveSense step; for every input the two give the same result (a negative figure stays non-positive under −20 %, −50 or no reduction and is clamped to 0 at the DriveSense step). Equivalent.
- L: compute matches the rule for both conventions and the rate ladder; vehicle_added falls back to the coverage effective date where no auto_vehicle_add row exists (rule silent on that case; observation O-14). Day counting for the lender convention is "the days from the loss date to the acceptance date" with no explicit inclusion rule (S states "the report date not counted"); the plain difference is the natural reading (observation O-14).
- K: tax_base implements the three new tiers; acv basis now quotes the NCR exclusion sentence.
- S, C: changed bindings grounded.
- No invented basis, no empty promise.

### action_binding_and_uuids (revision 2)

Carried forward from revision 1 by reference: task_tools.py hash unchanged (7aa76835…); (target_tool, computes) pairs unchanged in the charter. PASS.

### prerequisite_graph / prerequisite_sentences (revision 2)

The three prerequisite blocks and their policy_source sentences are textually unchanged (diff shows no change in any prerequisite field or in the sentences inside the rules); depended-on rules (A, C) still do not restate them. Revision-1 conclusions stand. PASS.

### override_declarations (revision 2)

- A: the removed repeat-claim surcharge leaves nothing to declare; the loyalty and DriveSense reductions modify the combined figure governed by the named "fixed in this order" sentence (overwrite 1, updated). PASS.
- K: the base new-car-replacement sentence is now named (overwrite 2) with a single merged meaning (kept vehicle valued at ACV). P-1 closed. Realism of the reason given (new car replacement exchanges the damaged vehicle for a new one) is sound.
- S, L, C: overwrites updated consistently. PASS.

### factor_ladders (revision 2)

- A: package_deductible_cap (parameter), loyalty_deductible_reduction (parameter; cross auto; a tenure deductible reduction is a recognised loyalty perk), drivesense_deductible_reduction (method — a percentage cut versus a flat cut versus none: different algorithms; honest), uninsured_driver_waiver (parameter, now honestly labelled; multi-source). 3 parameter + 1 method. F-1 closed, F-2 closed.
- S: package_custom_equipment_limit now raises the option limit on every option (Premier +2,000, Preferred +1,000; all tiers distinct) — F-4 closed. deductible_rewards_weighting honestly labelled parameter — F-3 closed. Counts: 1 method (replacement_cost_value), 5 parameter.
- L: payoff_to_loss_date (method — whole-month rent-charge convention versus daily actual/365 simple interest versus none; these are the conventions lease and simple-interest auto loans actually use; honest) — F-5 closed. option_seasoning / tenure_credit removed — F-6 closed. package_deductible_coverage (parameter). lien_release_charge (parameter; realism acceptable — lien-release/title fees are real state-varying charges; O-13 on the zero-gap case). assumed_contract_rate (parameter) — NEW DEFECT N-1 below.
- C: package_credit_cap Preferred tier = 75 % of the option's collision_deductible — NEW DEFECT N-2 below. Other C factors unchanged.
- K: kept_vehicle_tax_basis — tier conditions are now a replacement purchase and the time elapsed since the loss (the conditions states that tie tax reimbursement to replacement actually use); drivability is gone. F-7 closed. Remaining K factors unchanged.

### findings (revision 2)

Closed (verified on the charter text): P-1, F-1, F-2, F-3, F-4, F-5, F-6, F-7. O-9 resolved (option-date proxy removed with option_seasoning). O-10: the rule no longer states half up in A's combination sentence; RND remains Python round(); no tie in either world — observation stands in reduced form. O-1, O-3, O-4, O-5, O-6 (now only the "Leasing"-in-name proxy), O-7, O-8, O-11, O-12 unchanged as observations; O-2 blueprint-level.

N-1 SOURCE-FACTOR RED — assumed_contract_rate (L) has no baseline in baseline.rule; its fall-through is not the baseline. Bears on task 0.
- L's baseline.rule removes no finance charge ("The measured payoff is the payoff stated on the accepted surrender settlement ..."), so no contract rate exists in the standard method. The factor's declared baseline contract_rate = K('used_vehicle_rate_pct') (9.4 %) is the fall-through tier of a ladder whose input only exists once payoff_to_loss_date leaves its own fall-through. The skill's test — "the factor's baseline is what the policy's baseline.rule states for that input" and "every factor's fall-through tier is that baseline" — fails: baseline.rule states nothing for this input, and 9.4 % appears nowhere in it. A reader who has the computation document and the payoff-as-of-loss-date document but not the contract-rate document meets "the assumed contract rate" with no value and computes no number, not a definite wrong one.

N-2 SOURCE-FACTOR RED — unreal tier introduced in package_credit_cap (C). Bears on task 1 (charter-level; task 1's $1,000 option takes the tier where it raises the cap).
- Preferred cap = 75 % × collision_deductible: on the $500 option 375.00 and on the $250 option 187.50, below the deductible_rewards_max_credit (500 / 250) that every lower package receives on the same option. A premium package lowering a Deductible Rewards cap the customer would hold on a basic package is not a treatment any carrier publishes (same shape as revision-1 F-4). Regression introduced by the rework (revision 1's Preferred tier, max + 100, always raised the cap).

Observations O-13 (lien-release charge paid as a "benefit" with no shortfall) and O-14 (L day-count wording; vehicle_added fallback).

### closing_checklist (revision 2)

Written 2026-10-05T12:22Z after both revision-2 comparisons. The revision-2 charter section above was on disk before any revision-2 reveal.

- Round-1 REDs, verified on the reworked artifacts: P-1 closed; F-1, F-2, F-3, F-4, F-5, F-6, F-7 closed; T-1 closed (task 1); C-1 closed (both tasks); K-NM closed (task 1). O-9 resolved; O-10 reduced (half-up wording dropped, Python round() kept, no tie in either world).
- No regression in: base copy (byte-identical), tool module (hash unchanged), prerequisite graph and sentences (unchanged), scopes ({A,S,L} / {C,K}, disjoint, complete), problem trees (unmet at opening, load-bearing, user write present, tools gate nothing), unique solutions (blind derivation = revision-2 GT on every write, argument and owner; every computations figure re-derived).
- New defects introduced by the rework: N-1 (assumed_contract_rate has no baseline in L's baseline.rule; task 0), N-2 (Preferred credit-cap tier falls below the basic cap on the $500/$250 options; task 1), N-3 (no near-miss left in the loan payoff computation; task 0). New observations O-13, O-14.
- Revision-2 verdicts: task 0 SOURCE-FACTOR RED (N-1, N-3), other three relationships PASS; task 1 SOURCE-FACTOR RED (N-2), other three relationships PASS.
- The difficulty does not yet pass; close-out (gate re-run on the final form) not reached.

## revision_3

### charter_global_frozen (revision 3)

- Inputs: /tmp/erl35_views/physical_damage_claims_and_total_loss.r3/ — hashes re-verified against MANIFEST.sha256 and the live files: physdmg.extended.yaml 1692aaa2be6ff498b67b1e16092e0e89b4fbe3b5244cdb4f5d58f15b464b7ced (CHANGED), task_tools.py 7aa76835… (UNCHANGED), task_0.view.json b214695f…a7ed9 (CHANGED), task_1.view.json 6ed30f05…db81c0 (UNCHANGED from revision 2). Base section byte-identical to the blueprint. GATES.txt: all eight green, traceability deferred. Entry conditions met.
- Freeze time 2026-10-05T12:57Z, before any revision-3 task JSON was opened.
- contamination_disclosure: the revision-1 and revision-2 GT of both tasks were read in earlier revisions; the revision-3 GT is unread at this freeze.
- Re-derivation scope: charter diff r2 → r3 touches only physdmg_ext_loan_payoff_benefit (L) and physdmg_ext_claim_free_credit (C). § action_binding_and_uuids carried forward on the unchanged task_tools.py hash; § prerequisite_graph / prerequisite_sentences carried forward (no prerequisite field or sentence changed; L's prerequisite sentence is still verbatim in its rule); A, S, K sections of revision 2 carried forward (text unchanged).

### changes found (r2 → r3)

- L: the finance-charge removal moves into the standard method: baseline.rule now states the daily actual/365 removal ("the loss date not counted") at "The assumed contract rate is used_vehicle_rate_pct percent a year" (9.4 %). payoff_to_loss_date now decides finance_charge with tiers lessor & > 10 days → whole-month rent charge / ≤ 10 days → none / otherwise → daily (the baseline). assumed_contract_rate's fall-through (9.4 %) is now the baseline.rule's rate; its rule states the vehicle-add fallback. Lien-release charge paid only where a shortfall exists.
- C: Preferred credit cap = deductible_rewards_max_credit + preferred_cap_uplift 250.

### rule_compute_equivalence / override_declarations (revision 3)

- L: finance_charge and measured_payoff bindings match the rule (monthly branch, grace branch, daily branch, rounding of the charge, measured = stated − charge); result adds the lien fee only when shortfall > 0, as the rule now says. The base override (loan/lease payoff sentence) remains declared. PASS.
- C: credit_cap matches the revised sentence. PASS.

### factor_ladders (revision 3)

- L: payoff_to_loss_date — method, three distinct algorithms (whole-month rent charge / none / daily simple interest), fall-through = baseline (daily). assumed_contract_rate — parameter, fall-through 9.4 % = baseline.rule's stated rate. package_deductible_coverage, lien_release_charge — parameters. 4 factors, 1 method, 3 parameter; multi-source assumed_contract_rate (coverage + auto add transaction); cross auto. Realism: lease rent charge by whole months and loan simple interest by days are the conventions those contracts use; a fixed assumed rate stands in for the contract rate (observation, as O-6).
- C: Preferred tier now raises the cap above the basic cap on every option where Deductible Rewards is available ($1,000: 750; $750: 750; $500: 750; $250: 500). Observation (extends O-8): on the $500 and $250 options the Premier tier (collision_deductible 500 / 250) now sits below the Preferred tier; the excess Preferred cap there exceeds the largest deductible of those options and can never be used, so the inversion costs no customer anything — not raised as RED (same shape as revision 1, where Preferred max + 100 also exceeded Premier on those options).

### findings (revision 3)

- N-1 CLOSED: assumed_contract_rate's baseline (9.4 %) is now the rate baseline.rule states, and payoff_to_loss_date's fall-through is the baseline's daily removal.
- N-2 CLOSED: the Preferred credit-cap tier no longer falls below the basic cap on any option.
- N-3: per task (0.md revision_3).
- O-13 CLOSED (lien-release charge only with a shortfall). O-14 CLOSED (loss date not counted; vehicle-add fallback stated).
- New observation O-15 (seed, task 0): the leased Outback's auto_lienholder_change row keeps reason_code new_loan and its add transaction reason vehicle_purchased; the auto charter offers no lease reason code. No rule reads either field.
- No new RED at charter level.

### closing_checklist (revision 3)

Written 2026-10-05T12:59Z after both revision-3 comparisons.
- Per-task files 0.md / 1.md correspond one-to-one with tasks 0-1, `_difficulty.md` alongside; revisions 1, 2, 3 preserved in order; every revision-3 comparison carries PASS on all four relationships for both tasks.
- Coverage and scope: 5 extended policies fully covered; task 0 {accident_deductible, surrender_settlement, loan_payoff_benefit}, task 1 {claim_free_credit, kept_vehicle_settlement}; pairwise disjoint over whole trees; task tools closed; five independently generated, frozen uuid8s (ec9cfb06, c07cd979, 8a830e94, c23d8d33, b04c3b51).
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, user write accept_total_loss_settlement_c07cd979; task 1 — 1 prerequisite problem, 1 value_input edge, user write keep_total_loss_vehicle_b04c3b51; difficulty graph A→S→L, C→K acyclic; no cross-task edge.
- Factors: A 4 (3 parameter, 1 method), S 6 (5/1), L 4 (3/1), C 6 (5/1), K 5 (3/2); each task has multi-source and cross-difficulty factors (task 0: auto, telematics; task 1: auto, telematics, billing) whose rows are seeded; every ladder ≥ 3 distinct tiers stated in its rule; every factor bears weight against an honest baseline on its task's world; all-baseline numbers 750.00 / 29,648.33 / 4,734.16 / 0.00 / 11,982.50 each differ from gold; a near-miss in every computation.
- Round-by-round RED history: revision 1 — P-1, F-1…F-7, T-1, C-1 ×2, K-NM; revision 2 — all closed, new N-1, N-2, N-3; revision 3 — N-1, N-2, N-3 closed, no new RED.
- Gates on the final form: the conductor's revision-3 snapshot (GATES.txt in the .r3 view directory: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; traceability deferred until the KB is published) was run on the files whose hashes the auditor verified as the live artifacts (charter 1692aaa2…, tools 7aa76835…, tasks/0.json b49ef38a…, tasks/1.json 396181ad…).
- Result: the difficulty passes the source-layer policy-task audit at revision 3. Remaining items are observations only (O-1, O-3, O-4, O-5, O-6, O-7, O-8, O-10, O-11, O-12, O-15; O-2 blueprint-level).
