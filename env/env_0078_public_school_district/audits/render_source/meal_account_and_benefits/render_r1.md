# Renderer scan-first findings — product meals, render round 1 (renderer findings filed verbatim by the coordinator)

# env_0078 meals (meal_account_and_benefits): source findings, render STOPPED (no docs written)

Source: env/env_0078_public_school_district/tasks/meal_account_and_benefits/meals.extended.yaml (+ task_tools.py)
Gate line checked: "VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN".
Checks that came back clean: compute_basis quotes verbatim (all 8 policies); every policy_source verbatim in its rule; every baseline.rule verbatim in its rule; MONTHS/DAYS behaviour at month-end and for negative indices (June 2026 gives -1, so falls outside the window); next-month serving-day constants re-derived from the calendar (14/21/21/16/14/19/19/17/22/19 all agree); schema fields leaver_reason / withdrawn / completed / date_of_birth all exist.

## F1 (RED): meals_ext_departure_rollover, the lunch charge is a plain binding that contradicts baseline.rule
- `w_lunch_charge` is in no factor's `bindings` (the factors are departure_serving_days, departure_breakfast, departure_milk, departure_second_meal, departure_snacks). It is therefore a non-factor binding, and the computation document has to cover it.
- compute (extended.yaml ~l.2981): `w_lunch_charge: P('lunch_charge_secondary') if (F('campus') == 'Ridgecrest Middle School' or F('campus') == 'Calloway Creek High School' or F('campus') == 'Mesquite Ridge High School') else P('lunch_charge_elementary')`
- rule / compute_basis: "The lunch charge the departure rollover counts is the student's charge under the district's meal pricing at the account's campus: the secondary lunch charge of the student's meal status at Ridgecrest Middle School, Calloway Creek High School or Mesquite Ridge High School, and the elementary lunch charge of the status at any other campus not listed in cep_campuses."
- baseline.rule (~l.3245): "The standard departure rollover amount funds twenty serving days (days_standard), a full school month, of one reimbursable lunch at the elementary lunch charge of the student's meal status, with nothing else added, less the account's balance ..."
- The computation document would have to say both "the elementary lunch charge" (baseline.rule) and "the secondary lunch charge at R/C/M" (the binding it covers), and the two conflict. Witness (hypothetical): receiving account at a high school, Paid Meal Status, balance 0.00, every factor at baseline. baseline.rule gives twenty times 3.10 = 62.00, but compute gives twenty times 3.45 = 69.00.
- Possible fixes (pick one): make the lunch a declared factor (e.g. departure_lunch with baseline P('lunch_charge_elementary'), as the cover, quote and graduate rollover do), or reword baseline.rule to the campus-dependent lunch charge.

## F2 (RED, XF A2/A10): meals_ext_cep_balance_refund, a rule sentence names the factor quantities
- rule (~l.2288): "The CEP refund leaves on the account a keep for the student's milk, second meals and snacks over the serving days left in the current month, as the schedules below count it, together with every deposit not yet cleared; the keep is defined only by those schedules."
- The sentence lists the quantities of cep_refund_keep_milk, cep_refund_keep_second_meal and cep_refund_keep_snacks, and also the held deposits (cep_refund_check_hold, cep_refund_card_hold). It has no legal home:
  - in the hub it is a component inventory;
  - in the computation document it is a factor hint, and it contradicts baseline.rule "with nothing kept and no deposit held back";
  - in any one factor document it names the other factors.
- Fix: drop the sentence, or reduce it to the generic assembly sentence that already exists ("The adjustments described in the schedules are applied to the standard CEP refund in this order: ...").

## F3 (RED, placement / baseline silence): meals_ext_cep_balance_refund, the serving-day count is a plain binding that only factor quantities use
- Plain (non-factor) bindings: e_left_month_index, e_left_start, e_left_end, e_left_span, e_left_weekday, e_left_weekdays, e_left_closed, e_days_left. They come with the rule sentences on the 2026-27 calendar and "The serving days the keep counts left in the month of the refund date are the weekdays after the refund date ...".
- `e_day_charge: e_milk_rate + e_second_rate`. Both terms are factor quantities, so at baseline the day charge is 0 and e_days_left moves nothing ("The standard CEP refund amount is the account's whole balance, with nothing kept").
- The computation document would have to carry the whole serving-day calendar and a per-day multiplication whose only per-day inputs live in factor documents. That signals undeclared modifiers, so the fall-back test fails its "no sentence suggesting anything is missing" leg. Every other policy in this charter declares its serving-day count as a factor (quote_serving_days, cover_serving_days, netting_keep_days, departure_serving_days, rollover_serving_days).
- Possible fix: make the CEP keep's serving days a declared factor with a baseline (one family factor, as the other policies do), so the computation document stays the plain "whole balance" calculation.

## F4 (AMBER, B6): transfer_idle_sibling_balance_b810dc58 docstring adds a condition the rule and the body lack
- docstring: "School Nutrition moves the idle part of an active student's meal account balance to a sibling's active meal account in the same household that carries unpaid meal charges."
- The netting rule's receiving account is the cover's receiving account ("the part of another active account's balance ... is moved by sibling transfer to that student's account"). The cover rule does not require that account to carry unpaid meal charges ("to clear the account's unpaid meal charges and pay for the student's meals ..."), and the tool body checks nothing of the kind.
- A tool document rendered from this docstring would publish an applicability condition that the source policy lacks.
- Fix: drop "that carries unpaid meal charges" from the docstring.
