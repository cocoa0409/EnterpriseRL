# Rework round 12 claims (bounded: members 1-7 of revision_11)

Each member was probed on a scratch copy of a task world:
- CG-33.1: makeup made-good test enforced (mk_made_good). Probe: task 1 world after the gold makeup posts. mk_made_good is True and no makeup is figured.
- CG-33.2: the respread, first-invoice and fee overwrites, the draft notice siblings and the credit/application overwrites now name a move "at the named insured's request". The billing_plan_switch restatement names the plans the returned-draft or certified-funds rules move. Probe: a plan moved by the returned-draft rule (Six-Pay, revoked, no switch down payment row). The switch scope is False, and its next invoice keeps the unchanged scheduled premium (mv_k 0, base).
- CG-34.3: the draft notice fallback on a requested move uses the respread schedule the move fixed (mv_k / mv_down / mv_respread). Probe: task 1 post-gold world, installment 5. The fallback premium equals the switch's respread.
- CG-34.4: the makeup advance is scoped to plans still billing by automatic draft (adv_auth, words and ladder). Probe: a return on the moved plan gives advance 0.
- CG-34.5: every schedule's down payment premium is the plan's own down_payment_amount less the fully earned fees it took, in the draft notice, deposit, switch down payment and switch (and the makeup advance). A plan switched onto EFT/card keeps the schedule it was enrolled on. Probe: card plan enrolled at a Six-Pay 20% down. The notice and deposit schedule installment equals the kept Six-Pay amount.
- CG-34.6: the draft notice fallback no longer reads a term number. A non-owner plan's down payment premium comes from its own non-owner policy fee. Probe: non-owner plan; the down payment premium is the down payment less the non-owner fee.
- CG-35.7: makeup fees owed are net of waivers tied to each fee by reversed_fee_txn_id. Probe: task 1 world with the late fee waived (company_error). The late fee owed is 0.

Scored values unchanged. Carried, not regressed: every item closed in rounds 1-11.
