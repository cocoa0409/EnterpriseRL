# Render pre-scan findings — product vision (difficulty vision_member_services), render round 1
Source: renderer agent a809460d215f9f785, 2026-10-20; saved verbatim by the coordinator. The renderer STOPPED before writing any document.
Gate line read: `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`. Source: tasks/vision_member_services/vision.extended.yaml and task_tools.py.

Findings by policy, worst first (references are to the extended yaml):

1. **Base-rule assembly sentence names quantities that only factors define (XF#2)**
   - `vision_ext_contacts_order`: `baseline.rule` and the `result` basis say *"then the fitting allowances (the tied fitting allowance and the new-wearer fitting allowance) are added into one combined fitting allowance and the fitting line's share is taken under its cost rule"*.
     - This names the `tied_fitting_allowance` and `new_wearer_allowance` factors. The new-wearer allowance is 0.0 in the baseline, so only its factor defines it. "its cost rule" points at the `fit_cost_rule` factor.
     - The same sentence also says *"(every in-lieu discount part that applies being added into one rate and taken once off the retail charge)"*. The baseline has no in-lieu rate: `k_basis` is `'allowance'` there.
   - `vision_ext_refit_member_share`: `baseline.rule` and the `result` basis say *"The allowances of a stand-alone fitting (the tied fitting allowance and the new-wearer allowance) are added into one combined fitting allowance before the cost rule for its kind and location is applied"*. This is the same problem.
   - Rendering these sentences would put factor hints into the computation document.

2. **One factor reads or is gated through another (XF#1), in `vision_ext_contacts_order`**
   - The rule says *"The in-lieu discount rate starts at materials_discount_pct percent, and the additional-pair part below is added to it when it applies."* This links `in_lieu_basis` to `additional_pair_part`. The sentence has no `compute_basis` attribution.
   - `k_ppct` only takes effect inside `in_lieu_basis`'s `'outside'` tier: `result: … k_cr * (1 - (P('materials_discount_pct') + k_ppct) / 100) if k_basis == 'outside'`.
   - Its own basis says *"An additional-pair part is added to the in-lieu discount rate…"*, but that rate exists only in the other factor.

3. **A fitting is zeroed when the contact lenses are blocked by frequency, but no rule sentence says so (`vision_ext_oon_glasses_claim` and `vision_ext_oon_contacts_claim`)**
   - The compute reimburses the fitting only when the contact-lens amount is above 0 or there is no contact-lens line:
     - `oon_glasses_claim`: `((MN(g_kr, (g_fit if g_cv else 0.0)) if g_kid != '' else 0.0) if ((MN(g_cr, g_camt) if g_cok else 0.0) > 0 or g_cid == '') else 0.0)`
     - `oon_contacts_claim`: the equivalent condition on `c_cok` and `c_camt`.
   - The rules say only *"the fitting is not limited separately"* and *"…oon_exam_reimbursement for a routine exam and for a fitting"*. The only stated exception is the in-lieu case. So a fitting whose contact lenses are denied for frequency is paid by the rule and paid nothing by the compute.

4. **Out-of-network fitting in `vision_ext_exam_visit_payment`: the rule and compute disagree**
   - `result` contains `(MN(a_kr, P('oon_exam_reimbursement')) if a_ch == 'out_of_network' else MN(a_kr, a_ffee))`. But the result sentence says only *"then the fitting line's lesser of its billed charge and its scheduled fitting fee is added"*.
   - `baseline.rule` schedules every fitting at `exam_fee_private`. So for an out-of-network visit with a fitting, the base rule gives min(charge, 110) while the compute gives min(charge, `oon_exam_reimbursement`).
   - The out-of-network sentence is attributed to the `a_ffee` (`fitting_type_fee`) factor, but that factor's ladder has no out-of-network tier.

5. **Claim-scope exclusions in the rules have no compute, and two policies conflict**
   - These exclusions are not applied in the claim-selection compute:
     - `exam_visit_payment`: *"…a routine eye exam line and no contact-lens line"* is not applied in `a_c1`/`a_c2`/`a_c3`.
     - `eyeglasses_order`: *"…and no contact-lens line"* is not applied in `b_c0`–`b_c5`.
     - `refit_member_share`: *"…neither a routine eye exam line nor a contact-lens line"* is not applied in `x_snsp`–`x_sdta`.
   - `contacts_order` says *"(a routine exam line of such a claim is settled as an exam visit)"*. But the exam-visit rule excludes any claim with a contact-lens line, so by the text that exam line belongs to no policy.

6. **Scope of an out-of-network sentence in `vision_ext_refit_member_share`**
   - The sentence is *"On a plan whose contacts_benefit_included is false a stand-alone fitting … is denied DENIED_NOT_COVERED and bought at materials_discount_pct percent off its charge at a participating location; out of network the member pays the receipt less the lesser of the receipt and oon_exam_reimbursement"*.
   - The compute applies the out-of-network branch before the benefit check. So a non-covered plan's out-of-network fitting is still reimbursed, and the covered-plan out-of-network case is stated only inside this not-covered sentence.

7. **Binder read: the rule says "any" payment, the compute reads only the latest (XF#6/#7, all six policies; minor)**
   - The rule says *"received a binder payment, not returned, … on or before the binder deadline"*, which is satisfied by any such payment.
   - The compute reads only the latest binder (`XLATEST(... payment_purpose='binder')` and its return count). An earlier unreturned, in-time binder followed by a later returned or late one gives a different answer.
