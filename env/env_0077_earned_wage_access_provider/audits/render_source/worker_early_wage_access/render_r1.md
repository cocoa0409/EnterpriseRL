# Renderer findings, access render round 1 (renderer agent afc7c2c35153d61f8; saved verbatim by the coordinator — the harness blocked the renderer from writing its findings file). Renderer STOPPED before writing any document. Everything else in its scan passed (rule-vs-compute edges, rounding, factor independence, assembly order, overwrite tails, factor-id-vs-tool-name, compute_basis verbatim).

## F1: `record_missed_recovery_review_*` docstring is wrong for a plan on Paystride Access Starter
- Docstring (task_tools.py line 210, parameter `new_variant_name`): `"Paystride Access Premier Plus" in no situation, since this review always lands at least one tier below the tier held.`
- Rule (`access_ext_missed_recovery_review.rule`, access.extended.yaml line 2316): `a tier named below as one or two below the current tier never goes below Paystride Access Starter` and `the plan lands on the lowest of those tiers and never higher than one tier below its current tier`.
- Compute (line 2332): `pd_one: MX(1, pd_cur - 1)`.
- Mismatch: a plan already on Paystride Access Starter lands on Paystride Access Starter, which is the tier it holds, not "at least one tier below the tier held". The tool document would have to publish a claim the rule contradicts.
- Suggested fix: drop or reword the `since …` clause, for example "since this review never lands higher than one tier below the tier held".

## F2: `book_bank_transfer_fee_*` docstring names a next-business-day bank transfer, but the body accepts any transfer
- Docstring (line 84): `Book the fee owed on one next-business-day transfer to a bank account on a worker's Earned Wage Access Plan.` Line 86 adds: `… carries the transfer's payday, delivery speed and destination, is typed as a next-business-day fee …`
- Body (line 108): `src = ctx.find("access_ledger", access_entry_id=related_entry_id, access_plan_id=access_plan_id, event_type="access_transfer")`. It does not check `delivery_speed == "next_business_day"` or `destination_type == "bank_account"`. Line 119 always writes `fee_type="next_business_day_fee"`.
- Mismatch: called on an instant transfer to an external debit card or the Paystride card, the tool books an entry typed as a next-business-day fee that carries `delivery_speed` instant. The body does not enforce the transfer type the docstring names (the "a deposit on this booking" class).
- Suggested fix: either reject a `related_entry_id` whose transfer is not next-business-day to a bank account, with an explicit error, or reword the docstring to match what the body actually enforces.
