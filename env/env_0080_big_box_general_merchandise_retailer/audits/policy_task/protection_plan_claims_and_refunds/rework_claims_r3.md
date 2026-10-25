# Rework claims — protection_plan_claims_and_refunds, round 3

| item | status | location changed |
| --- | --- | --- |
| R2-C3 | closed | plan_ext_limit_of_liability_registration factor replacement_price_basis (tier 2 = lowered Northgate price) and new factor competitor_match_reduction; plan_ext_accident_cancellation_refund factor coverage_count_start (delivery-wait threshold); plan_ext_accident_claim_service_fee param tv_visit_charge_usd; tasks/0.json order adjustment row |
| R2-C11 | closed | plan_ext_limit_of_liability_registration rule/compute (covered device lines; accessories only for non-general-merchandise lines; allowance and delivery shared among device lines) |
| N1 | closed | plan_ext_food_loss_payment rule/compute/factor spoilage_cause_allowance (approved failure claim first, then manufacturer-warranty denial; both claim types read) |
| N2 | closed | plan_ext_accident_claim_service_fee prerequisite sentence and condition; plan_ext_accident_cancellation_refund settlement edge ("carries a settlement") |
| N3 | closed | plan_ext_repair_authorization_value rule/compute (base no-lemon clause applied); task_tools.py settlement rows carry the claim type; tasks/1.json seeded settlement row |
| T0-R2-1 | closed | plan_ext_repair_authorization_value (no authorization on the day of approval); plan_ext_accident_cancellation_refund (claim approved on the cancellation date: fee taken from the refund, repair after cancellation); tasks/0.json user_scenario passive line and tracing |
| O18, O19, O20 | closed | registration price bases; service-fee visit charge; task 0 persona |
| O16, O17, O1 | noted / disputed | O16 placement wording, O17 company schedule kept; O1 base definitional text (base frozen) |
