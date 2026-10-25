# Renderer source-scan findings — product forceplaced, render round 1 (renderer agent a69f629b3390c47b0)
Saved verbatim by the coordinator from the renderer's final message (the renderer STOPPED with 0 docs written). Everything is in tasks/lender_placed_flood_programs/forceplaced.extended.yaml.

**F1 – An overwrite retires a clause that is still in force (forceplaced_ext_loan_event_credit, overwrite[1] → forceplaced_evidence_cancellation)**
- The retired clause is: "On acceptable evidence the certificate is cancelled for BORROWER_COVERAGE_CONFIRMED, and the cancellation and its credit are processed no later than overlap_refund_days calendar days after the evidence is received, counted by adding the days to the received date on the calendar with the last day qualifying."
- Its replaced_by keeps that clause fully in force: "...on acceptable borrower evidence a certificate is still cancelled for confirmed borrower coverage, with the cancellation and its credit processed no later than the overlap refund period after the evidence is received, counted on the calendar from the received date with the last day qualifying."
- So nothing is actually retired, and the loan-event rule never conflicted with the clause. The retired sentence is also the exact `condition` of the base eligibility `overlap_refund_deadline`. The base document would have to mark the sentence "no longer in force" in the rule while carrying it as an in-force eligibility. On top of that, the evidence deadline would end up housed in the loan-event schedule's documents.

**F2 – Three rules defer to a base clause that their own overwrite retires (placement, renewal and commercial overwrites → forceplaced_effective_date_premium)**
- All three retire "The annual premium is the building limit divided by 100 times building_rate_per_100 plus the contents limit divided by 100 times contents_rate_per_100, rounded to the cent, and never less than minimum_certificate_premium".
- Their replaced_by and rule then defer to that same sentence:
  - placement: "every other certificate premium remains under the base rule"
  - renewal: "a new placement under any tier is priced by its own placement schedule or the base rule, and every other certificate premium remains under the base rule"
  - commercial: "every other certificate premium, including any on the Commercial Building and Contents tier, remains under the base rule"
- The retired sentence is the base rule's only premium formula, and none of the three restates it. The overlap and loan-event replaced_by do restate their base treatment. As written, the premium for Gap, Replacement Cost, Manufactured and Commercial Building and Contents certificates would be marked "no longer in force".

**F3 – Record scope differs between rule and compute (forceplaced_ext_commercial_placement_premium, factor branch_credit)**
- The rule reads "premium payments the lender made in the last 12 months on its own NFIP General Property Form policies with Tidemark".
- The compute is `reo_paid: XSUM('nfipcom', 'nfipcom_billing', 'amount', within_months=12, date_field='posted_date', event_type='nfipcom_premium_payment')`. That has no form filter, so it also sums the NFIP RCBAP tiers. The product's display name is "NFIP General Property Form and RCBAP Flood Policies (Write Your Own)".

**F4 – Unstated same-day tie rules (latent)**
- The rules say "the" record with the latest date, but `LATEST` uses a strict `>` and keeps the first stored row when dates tie:
  - placement and commercial `fn_loan`: "the first notice with the latest notice date among the program's first notices"
  - overlap `ev_cert`: "the borrower evidence with the latest received date"
  - loan-event `c_cert`: "the issue entry with the latest processing date under the program"
  - renewal `rn_cert`/`is_cert`/`cert`: "The certificate renewed is the one whose current term ... expires today". Nothing says what happens when more than one certificate expires today; the compute prefers a renewal entry over an issue entry.
- Also in the renewal policy, `rn_req` reads "the required amount stated on its renewal notice". The compute takes the latest of possibly several renewal notices.

**F5 – Negative and absent-record branches (latent)**
- **a. Renewal loss_load:** the rule covers net amounts "25 percent or more", "above zero but below 25 percent" and "when the net amount is zero the load is zero". A negative net (voids inside the 12-month window of payments issued outside it) is undefined; `loss_add` gives 0.
- **b. Placement and commercial retro load:**
  - The rule's day count ("days between two dates are counted from the earlier date to the later date") makes the gap non-negative when the notice comes before the lapse date. `retro_mult` uses a signed `DAYS(retro_lapse, retro_notice)`, which gives 1.00 where the rule would give 1.04 or 1.10.
  - The tiers also mix "from the lapse date to the notice date" with "between them".
  - This is unreachable if the base rule's notice-after-lapse ordering holds.
- **c. Overlap credit:** the latest acceptable evidence can name no certificate (the field is "empty when none was issued yet"). The rule's "the certificate named on the acceptable borrower evidence most recently received" is then undefined, and `ev_cert` is empty.

**F6 – Prerequisite scope wider than what the resolving schedule prices (forceplaced_ext_credit_refund, latent and seed-dependent)**
- Prerequisite 2 covers every certificate "whose latest term has reached its expiration date" (on or before today). The renewal schedule only identifies "the one whose current term ... expires today".
- Prerequisite 3 covers "every loan whose latest first notice is more than the borrower notice period old". The residential placement schedule only prices "the loan named on the most recently mailed first notice".
- The renderer could not check whether a seed actually hits this (task files are outside its read domain).

Renderer's severity note: F1 and F2 need a rework before this product can be rendered. F3 is a real rule-vs-compute scope mismatch, though seed exposure is unlikely. F4–F6 are latent.
