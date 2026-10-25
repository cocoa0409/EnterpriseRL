# Render-source findings — install (round 3)

Source: `install.extended.yaml` sha256 a5ed1fad039f5c9df725da0e9c39fe57c4924cd4999991388b3648addad82440; `task_tools.py` d8de31a5… (unchanged).

Upstream gate: policy_task `0.md` "revision_3 verdict: task 0 PASS" and `1.md` "revision_3 verdict: task 1 PASS".

Inputs read: `policy_kb/…/0.md` and `1.md` in full; `runtime_context/…/0.md` and `1.md`, the reading notes, counter-proofs and gt_comparison sections. No task value was used in any document.

## KB findings — closure

- **F0-1 (permit fee assembly missing from its computation document)**
  - `permit_administration_fee_amount_c1e5a01b.json` now names the method's fee as the filing base. It states the assembly in the computation document:
    1. amounts added to the fee join the filing base in one sum;
    2. a filing share multiplies that whole sum once;
    3. the fee is rounded to the nearest cent once, at the end.
  - It covers `result` only, because `own_signed` now sits with the filing-share factor.
- **F0-2 (capping volume document pointed at the oversize weighting)**
  - `capping_volume_pricing_e5fe614f.json` no longer says "as counted for capping" or "(from openings counted as one and a half)", and its half-opening example row is gone.
  - It now states the bands on "the priced openings of the job", which belong to the contract the job installs (the Window Replacement Contracts or Entry & Patio Door Contracts contract).
  - Its covers now follow the source bindings: `priced_openings`, `capping_price`.
- **F1-1 (casing volume document pointed at the leg weighting)**
  - `casing_volume_pricing_59115603.json` is fixed the same way. "As counted for casing", the 9.5 row and the half-opening line are removed.
  - Its covers are now `casing_openings`, `casing_price`.

## Source changes carried

- **Capping and casing standard paragraphs.** "…times the priced/casing openings, which are the openings on the contract the job installs" is carried in each computation document, which now covers `result` only. The weighting documents now say oversize openings "add to the priced/casing openings", counting as two, one and a half, or one priced/casing opening.
- **Crew-day standard.** "The units the crew plans for, which are the job's units, divided by the crew's daily pace…" is carried in `crew_days_planned_count_6218b618.json`, which now covers `daily_pace`, `plan_units` and `result`.
  - The inspection hold-back document says its openings "join the units the crew plans for".
  - The oversize crew-day document's tiers no longer name the hold-back. They now read "the units the crew plans for (other than the oversize openings / so weighted)".

## Runtime reading notes also closed

- **Lead-safe shaped-trim placement (the 915.00 alternative).** `lead_safe_fee_amount_3a6db6d9.json` now says the minimum per job is compared only with the method's lead-safe fee per opening times the openings on the job. Every other amount, including any amount stated per opening, joins after that comparison.
- **270.00 coincidence.** The hypothetical figures in `multi_day_containment_charge_0e8b7547.json` and `short_notice_company_move_multiplier_3a56771e.json` were changed so neither example produces 270.00.

## New source findings (round 3)

None. The S0-1 and S1-1 binding mismatches and the S0-2 hold-back coupling are fixed in the source and reflected above.
