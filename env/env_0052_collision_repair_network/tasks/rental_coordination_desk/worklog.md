# rental_coordination_desk instantiate worklog (round 1)
- draw: task0 prerequisite_problems=3 factor_counts=[5,5,4,4]; task1 prerequisite_problems=2 factor_counts=[5,6,4]
- tool names frozen (uuid8 each generated separately):
  credit_rental_billing_error_4d32ac17, credit_repair_customer_discount_d339b3bd, charge_young_renter_fee_a6a6d206,
  accept_rental_goodwill_credit_52804ea3 (user), authorize_network_courtesy_days_8334cede,
  authorize_insurer_extension_days_b8e4d7d7, authorize_self_pay_days_charge_125d1a79 (user)
- task0 tree (customer-pay rental tied to a network customer-pay repair): root goodwill credit (user accepts) <- repair-customer discount <- billing-error credit; root <- young-renter fee
- task1 tree (rental returned while the claim repair is still open): root self-pay days charge (user authorizes) <- network courtesy days; root <- insurer extension days
- task0 persisted (round 1): 4 policies + 4 tools + tasks/0.json; gold 227.82 / 144.53 / 264.00 (days_count 17, superseded in round 2 by 11) / 78.29; per-task gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK
  (replay first flagged 10 unread seed rows: dropped retail/adas ledgers + insurer profile, added find_vehicles read)
- task1 design: claim repair (third-party liability, Major) still in_repair; parts-delay extension posted; supplement-delay extension approved by insurer but never posted;
  camera calibration failed in-house 3x (one DTC) -> dealer sublet; renter returned the rental early. Root: self-pay days charge (user authorizes)
  <- network courtesy days (calibration window) ; <- insurer extension days (supported days of the approved request)
- task1 persisted (round 1): 3 policies + 3 tools + tasks/1.json; gold courtesy 4 days (ordinal 3), extension 2 days (ordinal 4), self-pay 7 days 193.68 (extension and self-pay superseded in round 2)
  round-1 fixes: extension history not load-bearing (late-request days measured against the insurer-authorized reach via SUM); added find_vehicles read
  (the round-1 binding move that gave the self-pay pricing factor an unread DAYS binding was undone in round 2)
- final suite gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max 8, branches_max 89), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK
- check_traceability: deferred until the KB is rendered (currently NOT OK only because no published document carries the tool names)
- validate_scenario: INVALID only on "required document ... not found" (no KB yet, all difficulties); forbidden tokens absent from task_tools.py

## round 2 (policy-task audit rework: audits/policy_task/rental_coordination_desk/)
- CG-1/T1-1: extension late-request days now follow the base rental_evt_extension sentence (a request reaching the insurer less than
  extension_request_lead_hours before the insurer coverage end covers only days from its approval); the unbased "less one" tier is gone.
  New 4th factor extension_supplement_choice (method: latest approved in full / latest partly approved / latest submitted); task-1 world
  gains a later denied supplement 2 (near-miss) and supplement 1 moves to 2026-09-12/16. Extension 2 -> 1 day.
- CG-2/CG-3/T1-2: overwrite declared for "Every authorization moves the coverage end date by the days authorized." (both authorization
  policies), coverage_end "Every rental day starting after the coverage end date is the customer's at the partner rate." and the
  rental_days covered-days sentence (self-pay policy).
- CG-4: extra-day loyalty test is now EXISTS(claim closed) (exact), lookback param removed.
- CG-5: rental_days return-grace sentence declared superseded in all five day-counting policies.
- CG-6: T0-1 priced_day_count removed (plain day count) + new remainder_pricing method factor (its round-2 empty-remainder fall-through fixed in round 3); T0-2 age ladder tier 2 = reachable
  short-span surcharge; T0-3 goodwill time basis falls through to final charge / posted days (re-cut again in round 3); T1-3 self-pay day count
  plain, day rate split into repair_status_discount + network_delay_discount.
- CG-7/T1-4: window_closing_date relabelled parameter.
- T0-4: young-renter rule states the charge is booked for its charged fee days -> days_count 11.
- latent: None-guarded cross reads, hold-days wording, goodwill customer-pay scope + date-difference wording, courtesy review days read the
  reviewed supplement's own decision, docstring ordinal "one more than the highest authorization number", persona "looked high" line removed.
- gold after round 2: task0 227.82 / 144.53 / 264.00 (11 days) / 78.29 (goodwill superseded in round 3); task1 courtesy 4 (#3), extension 1 (#4), self-pay 8 days 227.51.
- gates (final run): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK;
  traceability deferred (no KB); validate_scenario INVALID only on missing KB documents.

## round 3 (policy-task audit revision_2: R2-1, R2-2, stale "4 real factors" claim)
- R2-1: remainder_pricing tiers = remainder >= weekly_rate_threshold_days (one more block) / 2..threshold-1 (extra-day rate, capped)
  / a single remaining day or none (partner rate per day) - the fall-through now prices a real day; billing error stays 227.82.
- R2-2: lost_day_time_basis re-cut on states reachable after the discount prerequisite: billing-error credit stands (net / rental days)
  / corrected time charge stands (net corrected / its days) / otherwise (net final / posted days = baseline, baseline paragraph updated).
- coordinator reachability note (audit O-6): lost_day_fee_basis removed as a factor (its middle tier existed only with the young-renter
  prerequisite skipped); fee value is the young-renter charge / rental days (zero when none); new program_uplift parameter factor
  (military / returning_customer / none, retail tier params) keeps goodwill at 5 factors.
- task0 goodwill 78.29 -> 82.21 (all-baseline 18.92); skip discount -> 100.06, skip young fee -> 49.59; task 1 untouched.
- design_rationale: stale "4 real factors" round-2 sentence rewritten; round-3 section added; factor card / skip values / tracing regenerated.
- gates (final run): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK;
  traceability deferred (no KB); validate_scenario INVALID only on missing KB documents.
