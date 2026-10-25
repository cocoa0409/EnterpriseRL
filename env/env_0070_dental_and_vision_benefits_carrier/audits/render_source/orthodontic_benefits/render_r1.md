# Render pre-scan findings — product ortho (difficulty orthodontic_benefits), render round 1
Source: renderer agent af07bf5bc57f1d471, 2026-10-19; saved verbatim by the coordinator. The renderer STOPPED before writing any document.
Gate line read: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`.
All locations are in `env/env_0070_dental_and_vision_benefits_carrier/tasks/orthodontic_benefits/ortho.extended.yaml`. Problems 1 to 3 each block the render on their own; 4 to 6 are smaller gaps found in the same pass.

**1. `ortho_ext_waiting_takeover_fee`: the assembly sentence names a factor's quantity, and its wording does not match the compute** (rule, line 1303; `compute_basis.result`, line 1384)
- Quoted: "the covered months are counted and valued as stated, every share taken off the fee comes off the value of the covered months, divided by the planned treatment months, **the retention part is then added at its value**, every amount to be subtracted is then subtracted…"
- "The retention part" is the `retention_part` factor's quantity (`ret_pct`). The calculation document that carries `result` would have to name it, which breaks the rule that the calculation document says nothing about factors.
- The compute (`result`, line 1349) also takes the retention share off the covered-months value, using `(100 - start_pct - ret_pct)/100`, and then adds `fee * ret_pct/100`. The sentence only takes off "every share taken off the fee". The retention sentence calls that part "kept whole", not "taken off", so a reader would naturally not set it aside first.
- Hypothetical example (fee 4000, planned 24 months, 20 covered, braces start 15%, retention 10%): the compute gives 2900.00, while the natural reading of the text gives 3233.33.
- The transfer-fee policy (line 856) states this correctly: "every part taken off the allowed case fee and every part kept whole is first set aside".

**2. `ortho_ext_waiting_takeover_fee`: the `covered_payment_shape` factor describes another factor's quantity** (rule sentence and `compute_basis` for `shape_code`, `move_rate`, `moved`, `move_index`, line 1372; ladder, lines 1466–1472)
- Quoted: "for a case that has moved, … the covered months from that month on at the lesser of … , and **the retention part is valued at that lesser fee**; otherwise every covered month **and the retention part** are valued at the allowed case fee". The ladder repeats it: "the rest **and the retention part** at the lesser of the allowed fee and the latest practice's rate".
- This factor's document cannot be written without describing `retention_part`. In the compute the two only meet in `result`: `(move_rate if shape_code == 2 else ns_allowed) * ret_pct / 100`.

**3. `ortho_ext_carried_first_payment`: what `since_months` counts from when there is no installment payment** (rule line 1040; `compute_basis.since_months` line 1137 and `case_no` line 1103; compute line 1094)
- Rule: "on a monthly schedule with two or more such periods, the first carried payment covers the whole calendar months from the first day of the latest installment's service period to today … a case with no installment payment counts its periods from the banding month."
- Compute: `MONTHS(LATEST('ortho_cases','banding_date',…), NOW)`. This counts from the banding date, and `MONTHS` depends on the day of the month (confirmed in `check_compute.py`), not from the first day of the banding month.
- Example: monthly rider, banding on the 15th of month M, no installment yet, today the 10th of M+2. The rule gives 2 periods, so the payment covers 2. The compute gives `MONTHS` = 1, so it covers 1.

**4. `ortho_ext_member_overpayment_return`: a case the rule never addresses** (`start_index`, line 1592, and its rule sentence)
- Rule: "the first takeover installment covers the service period in which coverage of the case began". No sentence covers coverage that began before the original schedule's first service period (`cover_index` below the first-installment offset).
- This can happen on quarterly riders, where the offset is 3, when banding came 1–2 months before coverage began. The compute quietly uses the first scheduled period.

**5. `ortho_ext_member_overpayment_return`: possible division by zero** (`installment_count`, line 1606)
- On a quarterly schedule the count can be 0 when the months after the banding month before coverage are at least the installment cap. That leads to division by zero in `result`, and no rule sentence covers it (recipe point 6). It is only reachable with 31 or more planned months.

**6. `ortho_ext_waiting_takeover_fee`: "passed over" can be read two ways** (line 1374)
- Quoted: "a transfer entry with no months remaining is passed over". The compute treats the case as not moved; it does not fall back to an earlier transfer entry. "Passed over" can also be read as "use the previous transfer entry".
