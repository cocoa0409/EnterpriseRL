# Remaining source items after funding render round 3 (renderer a42998df730df58cd) and funding KB re-audit round 3 (a0ff99cf4efd3fe3a) — copied verbatim by the coordinator

Rendered source: funding.extended.yaml 63ab5a0aa207262c6a808ff27e504257d7478e41afa5d719b2c18f49b0e5043b, task_tools.py b1cb4232… (unchanged). docs/funding/ republished (58 docs, DOCS OK). Policy revision_6 CLEAN; KB revision_3 task0=PASS task1=PASS.

## Renderer, remaining source mismatches
1. **Combination sentences are still tied to computation-document bindings.** The compute_basis of several non-factor bindings still quotes sentences that name factor quantities:
   - lf: `lf_refund_days` ("A late day that the treatment of funds that were out or the treatment of the days after a settlement-agent return takes out is not refunded…"), `lf_overlap`, `lf_interest` and `result`.
   - sf: `sf_after` ("Any record-error allowance comes off the per diem shortfall first…").
   - rw: `rw_ret_wd`/`rw_std_n` ("Larkspur's re-send standard is the re-send days plus the re-review days plus the relock days…").
   - dd: `dd_interest`.
   The gate requires the computation documents to cover those bindings, so their meta still lists them while the sentences now sit in the factor documents.
2. **fm and rd baselines name their components.** fm's baseline still names the setoff, the redraw fee refunds and the payment channel charge. rd's names the rush, rider and program addenda add-ons, the signer-set price and the repeat-redraw fee. I carried them because the source states them, so those two computation documents are not fully silent about factors.
3. **sf credit cover timing.** The rule says the credit was "cut back at closing", but `sf_cutback` sums every exceeds-eligible-costs reduction on that credit with no date condition. The credit product books reductions "before or at closing".

## KB auditor, source-side notes
- Still open: the set-off rule still points to a prepaid interest dispute.
- New: the days-after-return document says "A day the treatment of funds that were out already takes out is not taken out again". That names another factor, but it is the source's own sentence and without it task 0 would count 09-14 twice.
