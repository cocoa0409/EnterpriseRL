# worklog — contents_packout_and_storage (env_0079), M=2

## Step 0 (difficulty pre-check)
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/contents.yaml (+ claims, account,
  water/rebuild schema fields), db_schema.json, share_tools.py, audits/render_source/XF_recipe.md, identifier_bands.md.
- Draws: task 0 -> prerequisite_problems 2, factor_counts [4, 6, 6]; task 1 -> 3, [6, 6, 6, 6].
- Base automatic clauses checked: storage periods billed on their first day (state_due), late fees only on invoiced jobs,
  job closes at zero balance after invoicing, custody needs a deposit on self-pay jobs, return waits on company rebuild
  contracts at the address. Worlds are laid so none of these ignites an unhandled obligation (see task dossiers).
- XF D7 events written by my tools and their base triggers: contents_storage_charge (triggers []), contents_customer_payment
  (triggers []), contents_pack_back_charge (triggers []), contents_packout_charge (triggers []). None lands in another category.
- XF E9: the account charter binds no contents pricing (service-call waiver / SLA credit are water and fire only); nothing to stack.
- owner=user route (XF F1 b): the only computable customer write in the frozen contents charter is the customer's own payment
  through the secure channel (authorization / disposal signing carry no computable number). Stated in each payment rule and persona.
- DSL limits honoured (XF B7): exact-match filters only, no date arithmetic producing dates, no range sums; period membership is
  computed from DAYS() offsets on recorded dates.

## Task 0 — storage after the carrier's approved end date (see tasks/0.json design_rationale for the full dossier)
Tree: root contents_ext_customer_share_payment (user, 4 factors) <- contents_ext_customer_vault_period (6, value_input)
      <- contents_ext_customer_valuation_period (6, value_input). Tools: charge_customer_vault_storage_2f9c3128,
      charge_declared_value_coverage_b3c8ef16, pay_contents_customer_share_24e82212 (uuid8 generated one per tool).

### Capability contract cards
- charge_customer_vault_storage_2f9c3128 — agent/write; object: one contents job; action: add one vault_storage line
  (bill_to customer, storage_period_start, amount) and raise balance_due by the amount; event contents_storage_charge
  (triggers []); receipt: status, contents_charge_id, contents_job_id, claim_file_id, storage_period_start, bill_to, amount, balance_due.
- charge_declared_value_coverage_b3c8ef16 — agent/write; adds one valuation_coverage line (bill_to customer, quantity = the job's
  declared value, amount), raises balance_due; receipt adds declared_value.
- pay_contents_customer_share_24e82212 — user/write (round 2: also takes surcharge_amount and books the card surcharge line for a
  credit_card tender); posts one contents_customer_payment (tender enum, confirmation number generated
  by the channel = return value, posted today), lowers balance_due; receipt: status, contents_payment_id, payment_reference,
  contents_job_id, payment_method, posted_date, amount, balance_due.
- claim_file_id is an argument of both storage tools because base gate sg_bill_to binds contents_jobs.claim_file_id -> claim_file_id.

### XF tables (task 0) — round-1 version, superseded by REWORK round 2 (current factor-reads, method pairs and probes are in
### the 0.json / 1.json dossiers and the REWORK section below)
Factor-reads (A1): every factor reads only its own bindings and plain reads.
| policy | factor | bindings read (transitively) | owners |
|---|---|---|---|
| vault | vaults_billed_count | haul_lines, signed_listed, capacity_vaults, boxes_packed, capacity, recorded_vaults | factor / plain |
| vault | contaminated_lining | water_category | factor |
| vault | facility_schedule | policy_state | factor |
| vault | secured_section | declared_shown | factor |
| vault | crate_racking | crates_packed | factor |
| vault | return_period_share | return_date, today_index, return_offset, return_in_period, days_into_period, period_days | factor / plain |
| coverage | covered_value_basis | haul_lines, signed_listed, pending_listed, declared_value, boxes_packed | factor / plain |
| coverage | contaminated_coverage_loading | water_category | factor |
| coverage | crated_items_rider / electronics_items_rider | crates_packed / electronics_packed | factor |
| coverage | coverage_facility_schedule | policy_state | factor |
| coverage | coverage_return_share | return bindings, period_days | factor / plain |
| share | counted_payments_basis | refunds_posted, surcharge_lines, payments_posted | factor / plain |
| share | insured_proceeds_pass_on | claim_arrangement, all_charge_lines, insurer_excluded_lines, insurance_postings, insurer_side_balance, insured_only_paid | factor |
| share | declined_lines_share | denied_billable, denied_writeoffs, supplement_requested | factor |
| share | uncovered_storage_days | approved_end ... last_insurer_vault_line, period_days | factor / plain |
Defining-sentence table (A3): baseline sentence of each policy = its "standard ..." sentence; each factor's ladder sentence owned
by that factor; scope/period sentences are plain (period_days/today_index); assembly sentences are plain (per_vault_rate,
full_period_amount, coverage_rate, result); prerequisite sentences live only in the share rule.
All-pairs method table (A7): see 0.json dossier (each pair differs by an input or an operation).
Decoy/absent-record probes (B2), run on scratch copies: absent water job / category_1 -> 0 lining; self-pay (no claim) ->
facility 1, uncovered 0, proceeds 0; no coverage line -> secured 0; signed authorization without haul -> recorded/capacity tier;
pending authorization -> pending-subtracted coverage; extension request with later end inside the straddled period -> days after
requested end; request in a later period -> 0; supplement request -> write-off less request (floor 0).
T1/T2 (A6): single-factor substitution on the task world moves every result (figures in 0.json factor_sensitivity); each factor
acts alone on a baseline-defined quantity, so T2 holds by construction.
Half-cent guard (B5): raw scored, baseline and sensitivity figures checked > 1e-6 away from a half cent (sens.raw_check).

### Runs
- ROUND scratch: /tmp/contents_packout_and_storage_0079/{ext_t0.yaml, assemble.py, sens.py, t0/*}.
- [round 1, superseded by REWORK round 2] vault 244.68, coverage 145.67, payment 3535.21. Current (round 2): vault 259.07
  (baseline 435.00), coverage 160.73 (baseline 177.70), payment 3869.69 (baseline 1152.19); skip vault -> 3610.62, skip coverage
  -> 3708.96; both orders of the two prerequisites give identical results.
- Fix log: replay flagged '' foreign keys on claims_approvals (claim_request_id / source_approval_id) -> empty id fields dropped.
  carrier_receivable aligned with the seeded claim rows (round 2: 8400 approved - 1850 paid - 245 written off = 6305.00).
- Per-task gates (task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Revision after task 1 design (propagated to task 0)
- contents_ext_customer_share_payment scoped to jobs in in_custody or return_scheduled status (the closing payment of task 1
  governs returned/invoiced jobs; each scope sentence names the other); its declined-lines supplement filter narrowed to
  price_variance supplements so the closing payment's contents_added-supplement excess and the declined-lines factor never
  subtract the same request. Task 0 figures unchanged (no supplement recorded); dossier text, tracing and gates re-run.

## Task 1 — return close-out (see tasks/1.json design_rationale for the full dossier)
Tree: root contents_ext_closing_payment (user, 6) <- contents_ext_pack_back_box_line (6), contents_ext_furniture_reset_line (6),
      contents_ext_return_truck_loads (6); all three edges value_input on excess_share (state form; two negated 'not ... until'
      sentences, one 'only after'). Tools: charge_pack_back_boxes_26b5c86b, charge_furniture_reset_9904d302,
      charge_return_truck_loads_2b0047ce (agent; one move-back line each, event contents_pack_back_charge, triggers []),
      pay_contents_closing_balance_f918d993 (user; one customer payment, confirmation number = return value).
- Return truck loads are booked as a move-back line (code truck_trip); contents_return carries no gate for move-back lines
  (policy_scope). Round 2: the truck rule now declares its overrides of the base truck-trip and quantity-times-rate sentences.
- [round 1, superseded] boxes 4212.40, reset 1502.02, loads 805.84, closing 9277.41. [round 2, superseded] closing 8823.89;
  skip boxes -> 5212.77, skip reset -> 7388.96, skip loads -> 8018.05. [round 3, superseded] closing 8265.69;
  skips 4654.57 / 6830.76 / 7459.85. [round 4, superseded] boxes 4280.80, closing 8912.89.
  Current (round 6): pack-back boxes 4298.80 (baseline 3088.80), furniture reset 1434.93 (880.40), truck loads 805.84 (645.00),
  closing payment 8930.89 (2413.10); skip boxes -> 5301.77, skip reset -> 7495.96, skip loads -> 8125.05; lines commute.
- XF tables for task 1 (factor reads, method pairs, probes, near-misses) are in 1.json's dossier; raw half-cent check clean.
- XF sweeps (both tasks): every compute_basis quote, baseline sentence and prerequisite sentence is verbatim in its rule;
  no factor id is a substring of a tool name; task_tools.py has none of the forbidden tokens; frozen_time format
  'YYYY-MM-DD HH:MM:SS CDT'; identifier bands: phones 2255550441 / 8505550463, surnames Nordquist / Ostrander, organizations
  Pelican Ridge Mutual Insurance, Red Stick Federal Credit Union, Osprey Coast Insurance Company, Navarre Coastal Credit Union,
  claim numbers ending 4417 / 4682.
- BLUEPRINT-KNOWN candidates: (1) the frozen charter's only computable owner=user write is the customer's payment, so both
  payments' factors are claim/contents record mechanics rather than pricing levers; (2) several storage and move-back levers
  (lining, facility schedule, secured section, racking, carry, floor protection, odor bags, crew/truck add-ons) are company
  schedules with policy params, keyed on water, fire, rebuild, claim and packout records, because the base parameters alone
  cannot supply 6 independent ladders per line.

## Final gate block (difficulty level, no --task)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite branches mean 70.00, steps 18.50,
history_rows_max 69, branches_max 84); GROUNDING OK; SCOPE OK. check_traceability deferred until docs are published.
ROUND 1: gates 7/7 green

## REWORK round 2 (audit: audits/policy_task/contents_packout_and_storage/{_difficulty,0,1}.md)
Scratch: /tmp/contents_packout_and_storage_0079/ (r1_* = round-1 copies; probes.py / probes_r2.json = probe table; rb_*.txt =
live-rebuild read expressions). Each class closed across all 7 policies, both worlds and all proof text.
- CG-A7 CLOSED: VP/VC fraction factors relabelled parameter (they select a fraction value); VC covered value made a plain rule;
  VC electronics rider rebuilt as a method (value-rated percentage vs per-item tariff); SP counted-payments dropped (surcharge
  lines in the standard share); PB boxes-brought-back made plain and the high-value check rebuilt as a method (technician-hour
  tariff vs per item); FR pieces made plain and the second crew rebuilt as a method (technician-hour tariff vs per piece); CP
  netting rebuilt (custody + goodwill vs goodwill capped at the tier's goodwill cap). All-pairs tables in each dossier.
- CG-LABEL CLOSED: insured proceeds (SP, CP) and scope overrun labelled method; declined lines and storage tail rewritten as fixed
  formulas whose tiers select a value (contested/disputed amount; uncovered days); CP charge-lines factor removed (surcharges and
  late fees in the standard closing payment).
- CG-COUNT CLOSED (parameter/method per computation): VP 5/1, VC 5/1, SP 2/2, PB 5/1, FR 5/1, TL 5/1, CP 3/3.
- CG-VC-REAL CLOSED: pending-signature tier removed; items on signed authorizations leave coverage (never compensated, base).
- CG-FR-REAL CLOSED: pieces are the furniture items; crates carry their own uncrating charge; no tier drops electronics.
- CG-SP-OVERLAP CLOSED: Homeowner Direct Pay excluded from SP/CP scope; denied/withdrawn tier replaces it; pass-on capped by approved
  scope less write-offs less postings; overrun counts non-storage work only.
- CG-CP-OVERLAP CLOSED: overrun on non-storage work (storage is approved by date), tail on storage after the approved end,
  suspension days on or before it — disjoint by construction.
- CG-C1-TL CLOSED: TL declares overrides of 'Truck trips are billed per load and the inventory report once per job.' and
  'Amounts are quantity times unit rate, rounded to the cent, half up.' (scoped replaced_by); the retire-nothing contents_return
  overwrite removed.
- CG-A9 CLOSED: every two-grouping sentence rewritten with an explicit order ('taking ... dividing that difference ...';
  'the lesser of two amounts, the first being ... the second being ...').
- CG-B4 CLOSED: VP/VC count the days from the period's first day through the return date, both counted (compute adds 1).
- CG-B2-REQ CLOSED: SP/CP read the request asking the latest end date (XLATEST on requested_storage_end_date): no tie rule needed,
  matches 'any request asking a later date'; probed with two requests.
- CG-B2-REBUILD CLOSED: every rebuild read takes the contract furthest along (closed, final_invoiced, substantially_complete,
  in_construction, permitted, signed, proposed) and never a cancelled one; stated in each rule; probed with a cancelled proposal
  listed first.
- CG-E7 CLOSED: SP prerequisite sentences narrowed to the storage period running today (the resolvers' own scope).
- CG-REF CLOSED: SP/CP scope 'while no storage line billed to customer has stayed unpaid longer than the tier's referral days counted
  from the first day of its period, customer payments settling the oldest customer lines first'; seeds reworked (task 0 debit
  payment 2026-09-02, task 1 ACH payment 2026-08-20) so no customer line is past 60 days.
- CG-C2 CLOSED: VP/VC replaced_by texts name the sibling's priced lines and keep the base text for every line the rule does not price.
- CG-A2 CLOSED: combination sentences rewritten generically (rate per unit after its adjustments, number of units, any per-item
  amounts, fraction of the period).
- CG-D8 CLOSED: both payment tools take surcharge_amount (0.00 unless credit_card) and book the surcharge line with the payment.
- T0-1, T0-2, T1-2 CLOSED (via CG-A9 / CG-B4). T0-3, T1-3 CLOSED (via CG-REF). T0-4, T1-6 CLOSED (via CG-COUNT). T1-1 CLOSED
  (CG-C1-TL). T1-4 CLOSED (CG-CP-OVERLAP). T1-5 CLOSED (CG-FR-REAL).
- T0-5, T1-7 DISPUTED (accepted residue): other-category ledgers (water/fire job lines, dwelling approvals and payments, deductible
  rows, rebuild draws) cannot be seeded: replay_tasks requires the gold read closure to equal the seed, so rows no gold read returns
  are rejected, and finder calls that feed no decision break evaluation_criteria leanness. Seeded holdings' own fields stay
  consistent with their charters; carrier_receivable equals the seeded contents approvals less payments and write-offs (task 0
  6305.00; task 1 693.00).
- Observations: O-1 closed (VC scope requires boxes above zero; compute guards the division); O-2 closed (a completion after the
  returned date carries no protection or runners, stated); O-4 closed ('declared value above zero'); O-7 reworded (punch list
  open / closing visits); O-8 closed (referral counted from the period's first day); O-3, O-5, O-6 noted, no change.
- Probe table re-run on scratch copies (probes_r2.json): no exception, outcomes match the rules. One unproducible probe (a denied
  file still carrying approvals and an approved storage end) double-counts; the claims lifecycle denies only before approval.
- Sweeps: compute_basis / baseline / replaced_by verbatim in their rules (0 misses); no factor id inside a tool name; forbidden
  tokens absent; every scored, baseline and sensitivity figure > 1e-6 from a half cent; stale-figure grep over both task files
  clean (4212.40 now appears only as task 1's heavy-box sensitivity figure).
- Gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 2: gates 7/7 green

## REWORK round 3 (audit revision_2: _difficulty.md VERDICT revision_2, 0.md / 1.md revision_2 findings)
- CG-A7 CLOSED: CP owed_compensation_netting rebuilt so the tiers take different inputs. T1, custody credits stand: every custody
  credit and every goodwill credit netted in full (the goodwill belongs to that damage settlement). T2, goodwill only: the lesser of
  the goodwill credits and the customer's own charges (lines billed to customer, surcharge and late fee lines). T3: nothing. T2 adds
  the contents_charges input and the lesser-of pick. The pick is not a no-op: a job whose storage is all billed to the carrier has own
  charges 0 while goodwill stays at or under the tier cap (probe: netted 0). The no-op goodwill-cap tier and the probe that broke the
  base cap are gone.
- CG-C1-TL CLOSED (T1-r2-1): TL adds a second overwrite. The base status sentence "The job must be in authorized, in_custody or
  return_scheduled status when a packout, cleaning or disposal line is charged." is replaced, for the move-back truck line only, by
  charging once the job is returned. Every packout, cleaning or disposal line keeps the base status gate, and the quantity-times-rate
  replaced_by now says "every packout, cleaning or disposal line amount is still ...".
- CG-A2 CLOSED: the five combination sentences (and their replaced_by and compute_basis copies) are now generic. VP: "any amount
  figured per item"; VC: "any amount figured per item or on the declared value"; PB: "every amount figured per item"; FR: "every amount
  figured per item or per crew"; TL: "any amount figured per item". A grep for the old phrases returns 0 hits.
- CG2-SUSP CLOSED (T1-r2-2): rebuild_suspension_storage is dropped, along with its sentences, bindings and the rebuild cross-category
  read on CP. The task 1 world's rebuild contract no longer records suspension or resumption dates, so no unjustified rebuild state
  remains. CP keeps its drawn 6 factors through the new prompt_payment_discount (parameter): a closing payment taken within 10 days
  of the returned date gets 2 percent off the customer's own unpaid charges (lines billed to customer less customer payments, floored at
  0); within 30 days, 1 percent; otherwise 0. On this world: 3 days, 2% of 2360.00 = 47.20. A kept-items factor was tried first and
  rejected: its charge and the overrun's exclusion of the same share cancel whenever the overrun is positive, so it would not bite.
- CG2-B1-FLOOR CLOSED: SP and CP add the carried amounts to the standard amount "before its rounding and before its floor at zero",
  matching the single final floor in compute. Probe (task 0 world plus a 2000.00 customer payment): rule and compute both give 1449.89
  on the opening world.
- CG2-B3 CLOSED: (a) SP and CP read the contents_added request with the highest supplement_number (an XMAX binding, then XLATEST
  filtered on that number), and the rule says so ("the most recent supplement request is the one carrying the highest supplement
  number on the file"). Probes with two same-date requests read the higher number (task 0: overrun floored to 0; task 1: 7365.69).
  (b) Every rebuild read in PB, FR and TL filters on the job's own claim file at the loss address. The rule states that the company
  keeps one rebuild contract per claim file and address, with added scope written as a change order, so no two contracts tie. Probe:
  a closed contract on another claim file at the same address is not read.
- T1-r2-3 CLOSED (via CG-A7). T0 revision_2 items: only CG-A2, CG2-B1-FLOOR and CG2-B3 wording bore on task 0; all closed, and task 0
  figures are unchanged (vault 259.07, coverage 160.73, share 3869.69).
- T0-5 / T1-7 ACCEPTED RESIDUE (coordinator ruling): every cross-category record a scored factor reads is a state its own charter
  produces and is seeded and read by gold: the claim file status, dates, approvals, write-off, payments and requests; the water job
  category; the fire job smoke severity; the rebuild contract status, property type and completion date. The one state needing
  justifying rows (the rebuild suspension) is dropped with its factor.
- Figures (round 3): task 1 boxes 4280.80, reset 1434.93, loads 805.84, closing 8265.69 (baseline 2413.10). Factor baselines: overrun
  4654.57, pass-on 6265.69, declined 7858.69, tail 8144.02, netting 8505.69, discount 8312.89. Deletion runs: 4654.57 / 6830.76 /
  7459.85. Task 0 unchanged. Raw half-cent check clean on every scored, baseline and sensitivity figure.
- Probe table re-run on scratch copies (probes_r3.json): no exception, and every outcome matches its rule (netting tiers, discount
  windows and zero base, supplement tie, rebuild claim-file filter, plus the round-2 probes).
- Sweeps: compute_basis and replaced_by verbatim in their rules (0 misses; the VP basis carried the old per-crate phrase and was
  fixed); no 'suspen', 'kept share' or goodwill-cap text in any rule. 0.json / 1.json proofs, factor traces and both design_rationale
  dossiers rewritten for the new figures. The stale-figure grep finds 8823.89 / 5212.77 / 7388.96 / 8018.05 / 511.00 nowhere.
  8312.89 now appears only as the discount's baseline figure.
- Gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 3: gates 7/7 green

## REWORK round 4 (audit revision_3: _difficulty.md VERDICT revision_3 = CG3-DISC; 1.md T1-r3-1)
- CG3-DISC CLOSED: prompt_payment_discount removed (rule sentence, bindings, params, factor). No write can record a discount, so it
  is not replaced by another unbooked reduction. The replacement is base-grounded: withheld_depreciation_carry (parameter, CROSS
  claims), from claims_evt_depreciation_release / claims_evt_writeoff ("Once the window has passed without a request, the withheld
  depreciation is written off as depreciation_forfeited and becomes the customer's own responsibility on tiers where denied amounts
  are billable"). T1: billable arrangement with a contents depreciation_forfeited write-off -> those write-offs. T2: contents
  depreciation releases issued insured_only -> those releases (the insured pays the company from them). T3: 0. The insured-proceeds
  pass-on now leaves depreciation releases out, so nothing is counted twice. A6/A7/A1: the values come from distinct record sets,
  bindings are its own, and the tiers are exclusive (a release implies a timely request, which excludes forfeiture). The window
  tier ("window passed, not yet written off") was not used because the DSL cannot take the earliest ACV date.
- T1-r3-1 CLOSED: task 1 world reseeded. The initial contents approval withholds 600.00. ACV contractor_direct is received
  2026-03-31 and posted 2026-04-01 (window closed 2026-09-27; the contents job was not complete before its 2026-10-20 return, so no
  request was possible). The depreciation_forfeited write-off of 600.00 is posted 2026-10-02 and the carrier receivable is 93.00.
  Ledger closure on the gold world: balance after the four writes = receivable 93.00 + insurance-billed storage 4380.00 less the
  121.67 tail; residue -0.0033 (half-up rounding only).
- Class sweep (CG3-DISC, payment different from the ledger share with nothing recording the difference), members found and closed:
  (1) SP and CP declined lines: a decided price_variance request still lowered the carried write-off while its approval also lowered
  the overrun. Now only the most recent price_variance request named by no approval is disputed (probes: T0 decided at 80 ->
  3369.89; T1 decided at 300 -> closure residue -0.0033). (2) SP and CP standard: refunds raise the balance, so customer payments are
  now counted net of the refunds returned from them. (3) CP standard: billing_error and duplicate_line credits are now netted.
  (4) PB boxes brought back are now never below zero (boxes packed 0 gave a negative line). Task 0 figures are unchanged
  (259.07 / 160.73 / 3869.69); its 0.json changed only in tier/trace wording for (1) and (2).
- Netting T2 (lesser of goodwill and the customer's own charges) checked, NOT a member: it never reduces below the ledger. Where it
  binds, the excess goodwill is a credit balance that the base customer-payment rule refunds or hands to a human, so no missing write.
  Kept as round 3 (auditor: CG-A7 closed, realism plausible).
- O-r3-1 CLOSED: "the most recent supplement request of a reason is the one of that reason carrying the highest supplement number on
  the file" (SP, CP). O-r3-2 / O-r3-3 noted, no change (not engaged).
- Probe table re-run on scratch copies (probes_r4.json) with a closure column. Covered: depreciation tiers (no write-off, AOB,
  insured_only release, contractor_direct release, dwelling decoy), price_variance awaiting/decided, refund, billing_error credit,
  goodwill, no claim file (None reads), box count 0, window open, denied file, plus the round-3 probes. No exception. Residues are
  -0.0033 except pending carrier decisions (an awaiting request), as designed.
- Sweeps: compute_basis / baseline / replaced_by verbatim in their rules (0 misses); no discount/prompt/suspension text in any rule.
  Stale-figure grep over both task files clean (8265.69, 47.20 and the round-3 sensitivities gone; the post1 seed check now says
  2026-03-31 / 2026-04-01). Both design_rationale dossiers, read objectives, argument tracing, factor traces and tier_taken were
  rewritten. Raw half-cent check clean.
- Gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 4: gates 7/7 green

## REWORK round 5 (renderer findings: audits/render_source/contents_packout_and_storage/render_r1.md; realism_bar.md applied)
- S1 CLOSED: in contents_ext_customer_share_payment, denied_writeoffs and declined_share now belong to declined_lines_contest, and
  insurer_storage_lines and uncovered_share to uncovered_storage_days. Each factor's baseline adds its share binding as '0' and
  keeps its decides key. No rule text changed; rule == compute holds; every scored, baseline and sensitivity value was recomputed
  and is identical. A1 holds: no factor reads another factor's binding. A2 holds: the factor-named sentences now live only with
  their factor; the computation document keeps only the standard and the generic assembly.
- S2 CLOSED: same move in contents_ext_closing_payment. denied_writeoffs and declined_share go to declined_lines_dispute;
  insurer_storage_lines and uncovered_share go to unpaid_storage_tail; baselines extended the same way, values unchanged.
- S1/S2 class sweep: every remaining plain binding in all seven policies is either a standard-method read or a generic assembly
  ("any percentage", "every amount figured per item", "the number of vaults/boxes/loads/pieces"). None names a factor-owned
  quantity. No other member found.
- S3 CLOSED (code fixed, docstrings kept): the five charge tools check whether the deterministic line id already exists. On a
  repeat call they return status already_booked with the line id and the unchanged balance. The docstrings now say so ("books
  nothing new: it returns status already_booked with that line's id and leaves the balance due unchanged"). Scratch test: a
  second identical pack-back call leaves the balance unchanged.
- S3 payment-id note CLOSED: both pay tools add the job's count of existing customer payments to the payment id and confirmation
  seed. A second real payment of the same method and amount posts its own row (and its own surcharge line); scratch test confirmed.
  Gold replay and closure regenerated (REPLAY OK, closure == seed).
- S3 class sweep: no other tool promises idempotence or a behaviour the code does not perform (check_task_tools OK).
- C1 CLOSED in part: two return-truck overwrites now retire only the conflicting clause. "Truck trips are billed per load" (the
  inventory-report clause stays in force) and "Amounts are quantity times unit rate" (the half-up rounding stays in force), each
  as a verbatim fragment, the same pattern the vault and coverage overwrites already use. replaced_by texts were narrowed to
  match, in the rule as well.
- C1 DISPUTED in part (status sentence kept): "The job must be in authorized, in_custody or return_scheduled status when a
  packout, cleaning or disposal line is charged." genuinely conflicts for the move-back truck line, which is charged once the job
  is returned. The revision_2 audit (CG-C1-TL residual) required this overwrite. The sentence is a single clause with no part
  that does not conflict, and replaced_by keeps the gate in force for every packout, cleaning and disposal line.
- C1 class sweep: the other seven overwrites (vault, coverage, pack-back, reset) already supersede fragments or the exact
  conflicting clause and restate the rest. No other member found.
- Rounding-tolerance note: no change. rounding_epsilon is each policy's own param; the renderer states it per computation
  document.
- Base vault-capacity-0 note: frozen base text. It has no effect because the two tiers with capacity 0 carry no storage.
  Observation only.
- realism_bar.md: no factor changed this round. All factors stay R1/R4/R5 shapes; none is X1-X4; no R6 waiver used.
- Proof/rationale sweep: task 1 design_rationale base-invariant card restated for the narrowed overwrites. No other proof text
  changed; the stale-text grep for the old replaced_by wording and the old docstring sentence is clean; verbatim sweep (compute_basis,
  baseline, replaced_by) shows 0 misses. Probe table re-run on scratch copies with no exception and no outcome change.
- Gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 (audit revision_5: _difficulty.md VERDICT revision_5 = CG5-X4; 1.md T1-r5-1; realism_bar.md applied)
- CG5-X4 CLOSED (pack-back heavy-box handling): the ladder is now graduated. As many large boxes as the heavy-box volume threshold
  carry the standard charge, and only boxes beyond it carry the volume charge, so the charge rises with every box and never drops at
  the threshold. The rule sentence, compute_basis and ladder were rewritten. The label changed parameter -> method, because the
  volume tier now has a different shape (two rates and the threshold as an input); A7 holds against the standard tier.
- CG5-X4 CLOSED (pack-back wardrobe hanging): the same graduated form and the same relabel. Not engaged in either task world.
- CG5-X4 CLOSED (coverage electronics schedule): the value-rated tier is now "never less than the per-item electronics rider times
  one item fewer than the electronics rated threshold" (a lesser-of-two floor equal to the largest per-item charge), so reaching the
  threshold never lowers the coverage. Task 0's world stays on the value-rated amount above the floor, so its scored figures do not
  move; its trace text names the floor.
- T1-r5-1 CLOSED: task 1's pack-back amount, the closing payment that carries it through the overrun, the deletion runs and every
  affected sensitivity were recomputed. All proof and rationale text in 1.json was rewritten to the graduated tier; raw half-cent
  check clean.
- Class sweep (every ladder in all seven policies, checked at each threshold): vault crate racking, uncrating, oversized set,
  oversized move, second reset crew, condition check, and the percentage/add riders all charge at least as much at and above their
  threshold as just below it. No other member found.
- Pack-back factor mix after the relabel: three parameter and three method factors. It still meets the floor of two parameter and
  one method, and the drawn count of six is unchanged.
- Renderer-closed fixes kept intact: S1/S2 binding ownership, S3 tool idempotence and payment ids, and the C1 narrowed overwrites.
- Stale-proof sweep: task 0's XF A1 line and task 1's plain-read list no longer call denied_writeoffs and insurer_storage_lines
  plain (stale since round 5). The stale-figure grep over both task files is clean; the verbatim sweep (compute_basis, baseline,
  replaced_by) shows 0 misses.
- Probes (scratch, probes_r6.json): each volume threshold checked one below, at and one above (large boxes, wardrobe boxes,
  electronics, plus a low declared value that makes the floor bind). Charges never decrease, and no exceptions in the full table.
- Gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 6: gates 7/7 green

## REWORK round 7 (KB audit revision_1: audits/policy_kb/contents_packout_and_storage/_difficulty.md KBVERDICT kb=K-1 src=S-1,S-2,S-3; runtime_context read)
- S-1 CLOSED (XF A3): every quantity only one factor reads now belongs to that factor and its sentence. Moved: vault capacity and
  boxes packed -> vaults_billed_count (customer vault period); vault capacity and boxes packed -> return_load_count (return truck
  loads); period length -> uncovered_storage_days (customer's share); period length -> unpaid_storage_tail (closing payment). The
  moved capacity / boxes-packed bindings quote the factor's own capacity sentence as compute_basis; the period-length bindings keep
  "divided by the tier's period length", which sits in the factor's sentence. No compute changed.
- S-1 class sweep (every plain binding in all seven policies, traced to its readers): the only other plain bindings read by a single
  factor are the period length of the vault and coverage period rules and the recorded vault count of the vault and return-load
  rules. They stay plain on purpose: the period length defines the period being billed in each rule's scope and baseline sentence,
  and the recorded vault count is the standard method's own input (the factor baselines read it). The KB audit's K-1 list confirms
  neither was flagged.
- K-1 (KB side): its source cause is S-1, closed above; the affected computation documents are for the renderer to re-render.
- S-2 CLOSED: the sibling exclusions now name only the sibling line, never its machinery. Vault return-period replaced_by: "a
  declared-value coverage line that the declared-value coverage rule prices remains under that rule". Coverage return-period
  replaced_by: "a vault storage line that the customer vault storage rule prices remains under that rule". Pack-back and furniture
  reset replaced_by: the sibling return lines "remain under their own rules". Rule text and replaced_by changed together. XF C2
  sibling naming is kept.
- S-2 class sweep: the other six replaced_by texts (vault storage, vault count, coverage amount, and the three truck-load clauses)
  name no sibling mechanism.
- S-3 CLOSED: the share-payment and closing-payment referral scopes now read "customer payments settling the oldest storage and
  declared-value coverage lines billed to customer first". This matches the scope's own "storage line billed to customer" test, the
  base measure contents_msr_customer_storage_unpaid, and the readings gold already uses. No compute reads this scope. Class sweep:
  "customer lines" appears nowhere else in any rule.
- No scored, baseline or sensitivity figure moved; both tasks were recomposed and compared field by field. The task 1 rationale also
  picked up the round 6 plain-read correction, which had been written to scratch but not yet composed.
- Proof/rationale sweep: both design_rationale dossiers now say where the moved quantities belong. Stale-text grep (old
  replaced_by / scope wording) is clean in both task files; verbatim sweep (compute_basis, baseline, replaced_by) shows 0 misses.
  Probe table re-run on scratch copies with no exception.
- realism_bar.md: no factor added or changed in shape; all factors remain R1/R4/R5; none X1-X4; no R6.
- Gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 7: gates 7/7 green

## REWORK round 8 (KB re-judge revision_3: audits/policy_kb/contents_packout_and_storage/_difficulty.md KBVERDICT kb=CLEAN src=S-4)
- S-4 CLOSED (verified): the return truck-load site-wait sentence carried two appositives ("with its punch list still open",
  "with closing visits still being made"). Ladder, compute and KB key on status alone, no record field shows punch-list or
  closing-visit state, and the published rebuild punch-list days could make the first appositive read false on task 1's dates.
  The status-only reading is the real rule, so the sentence now reads: "Delivering to a property whose rebuild the company has not
  yet closed out costs crew waiting time, and the wait charge is keyed on the contract's status alone: when ... substantially_complete
  status, each return load carries the open-site wait charge; when it is in final_invoiced status, each return load carries the
  invoiced-site wait charge; ...". The matching compute_basis was updated. Rule == compute == ladder; no scored figure moves.
- S-4 class sweep: every rule sentence of all seven policies was scanned for appositives and parentheticals (", with ...",
  "(...)", ", while ...", ", as ...", ", which ...", ", because ...", ", once/after/before/unless ..."). The only other members were
  the second site-wait appositive above, fixed with the first. The remaining hits are not conditions:
  - "because ..." clauses: reasons;
  - "as the line amount": the result's name;
  - "as many ... as that threshold": the graduated tier's own operative clause, matching compute;
  - "while no storage line billed to customer ... has stayed unpaid ...": the scope's stated, intended condition;
  - "which the insured pays the company from": a non-restrictive explanation.
  No rule contains a parenthesis.
- Probes (scratch): site wait across rebuild contract statuses (substantially_complete, final_invoiced, closed, in_construction,
  cancelled = not read) follows the status ladder; full probe table re-run with no exception.
- Proof/rationale sweep: no task text mentioned punch lists or closing visits. The task 1 design_rationale now notes the
  status-only key; the verbatim sweep (compute_basis, baseline, replaced_by) shows 0 misses. Both tasks were recomposed and compared
  field by field: only task 1's rationale text changed, and every scored, baseline and sensitivity value is identical.
- realism_bar.md (incl. RULE-6/7): no factor added or changed in shape; none X1-X4; no R6.
- Gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 8: gates 7/7 green
