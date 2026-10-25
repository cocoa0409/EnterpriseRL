# Renderer source-scan findings — product nfipcom, render round 1 (renderer agent a2cbfd9a7840d95aa)
Saved verbatim by the coordinator from the renderer's final message (the renderer STOPPED with 0 docs written). All findings are in tasks/nfip_commercial_rcbap_claims/nfipcom.extended.yaml.

**Blocking mismatches**

1. **A factor reads another factor** (`nfipcom_ext_building_payment`). `pb_other`, owned by factor `bpay_other_cover`, reads `pb_n_sched`, which belongs to `bpay_alone_layer`: `pb_other: "pb_chg_lim if (pb_bz_primary and pb_n_sched > 0 and (pb_inc_ok or pb_dec_ok)) else (pb_sov_value if (pb_bz_primary and pb_n_sched > 0) else 0)"`. The contents twin avoids this, so it is fixable inside the building policy.

2. **Claim bar contradicts the endorsement return** (`nfipcom_ext_cancellation_credit`).
   - The rule says "under the reasons in claim_bar_reasons nothing is returned for the current term when a loss dated on or after the current term_start carries claim payments…". For the held case it says "nothing of the current term is returned by this credit and its other parts are returned as worked out".
   - The compute zeroes only `xc_cur_ret`, which excludes the endorsement. A current-term endorsement is still returned under the bar: `result: MX(0, RND(xc_cur_ret + xc_prev_ret + xc_endo_ret - xc_rr_back …))`, with `xc_endo_ret` unchanged when barred.
   - The refund side zeroes the same endorsement's Reserve Fund Assessment under the bar (`xr_rfa: … (0 if xr_barred else …)`). So one cancellation returns the endorsement's risk premium but not its Reserve Fund Assessment.

3. **Rule says "in full", compute subtracts re-rate credits** (`nfipcom_ext_cancellation_refund`, `rfd_rfa_return`). The rule says "…and the Reserve Fund Assessment charges of a term that began after the cancellation took effect are returned in full". The compute nets them: `(0 if xr_in_cur else RND(xr_r_cur - xr_rc_cur, 2))`. This is reachable within scope: one endorsement in the prior term, one re-rate in the current term, and a cancellation effective in the prior term.

4. **Tie between value endorsements is undefined.** The rule says "the one that took effect later among those that took effect on or before the date of loss" and does not say which wins when an increase and a decrease take effect the same day. The compute silently picks the increase (`DAYS(…_dec_eff, …_inc_eff) >= 0`). This appears in `pb_chg_lim` (building payment), `cp_chg_cont` (contents proof amount) and `cy_chg_cont` (contents payment).

5. **Definitions used by only one factor sit outside it.** These bindings are bound as non-factor, so the computation document would have to cover them and name BizFlood. The baselines of the two proof-amount policies never mention BizFlood, so this would expose the factor there.
   - **Building proof amount:** `bp_bz_pid` and `bp_bz_loc` ("The building's location on that BizFlood policy is the location number…") feed only `bpol_value_basis`. The scope guard `bp_one` ("…only where the named insured's BizFlood statements of values schedule the building's address at most once…") is also non-factor.
   - **Contents proof amount:** `cp_bz_in` and `cp_bz_eff`/`cp_bz_cxl`/`cp_bz_end` (the in-force definition) feed only `cpol_value_ceiling`. The scope guard `cp_one` has the same problem as `bp_one`.
   - **Building payment:** `pb_bz_bldg` feeds only `bpay_alone_layer`, and duplicates `pb_sov_value`.
   - **Contents payment:** `cy_bz_cont` feeds only `cpay_alone_layer`, and duplicates `cy_sov_cont`.

**Non-blocking (rule and compute agree, but the results look wrong)** — all in `nfipcom_ext_cancellation_refund` unless noted:
- **Endorsement or re-rate effective after the cancellation date:** the RFA formula multiplies the endorsement charge or re-rate credit by more than 100%. The credit side handles this case as "in full" or "the whole re-rate credit".
- **Cancellation effective before the current term_start with no endorsement or re-rate:** the "otherwise" RFA branch uses a ratio above 1 on the current term and ignores the prior term's RFA. ICC and HFIAA handle this case explicitly.
- **Zero risk premium credit:** "The signed request a cancellation refund means is the one the risk premium CANCELLATION credit booked at processing references" is undefined, because no credit row exists. The amount is unaffected.
