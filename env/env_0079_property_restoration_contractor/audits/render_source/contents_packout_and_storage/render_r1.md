# Renderer findings (verbatim final reply of agent a7c1452bc96d791b6, saved by the coordinator)

I stopped at the scan and wrote nothing. The source has defects I can't render without misdescribing what the documents cover or publishing a false tool claim. No staging directory was created, nothing under `env/` or `/tmp/erl0079_coord/` was modified, and check_docs.py was not run, so there is no DOCS OK line or document count.

Everything else in the scan was clean: every `compute_basis` quote, `baseline.rule`, prerequisite sentence and `replaced_by` is verbatim in its rule, and every superseded clause is verbatim in its base rule. No factor reads another factor, no factor id is a substring of a tool name, and the rule and compute agree on every other edge I checked.

**STOP findings**

**S1 — `contents_ext_customer_share_payment`: two plain bindings carry a sentence that belongs to one factor (XF A2/A3)**
- Compute line `declined_share: MX(0, denied_writeoffs - contested_amount)` comes from the sentence "the share carries the carrier_denied_line write-offs recorded on the contents coverage less the contested amount, never below zero". It names a factor's quantity, "the contested amount", which only factor `declined_lines_contest` uses.
- Compute line `uncovered_share: insurer_storage_lines * uncovered_days / period_days` comes from the sentence "the share carries the job's most recent vault, climate vault and oversized item storage lines billed to insurance_claim, taken together, times the uncovered days, divided by the tier's period length". It names "the uncovered days", which only factor `uncovered_storage_days` uses.
- `denied_writeoffs`, `declined_share`, `insurer_storage_lines` and `uncovered_share` belong to no factor. check_docs therefore requires the computation document to list them as covered.
- That leaves two bad options:
  - **Put the sentences in the computation document.** It would name quantities defined only in a factor document, so a reader of that document alone can't compute and is told something else applies.
  - **Put them in the factor documents.** The computation document would then claim bindings it doesn't render.
- Suggested fix, with no change to rule text or gold:
  - Add `denied_writeoffs` and `declined_share` to the bindings of `declined_lines_contest`, with baseline `declined_share: '0'`.
  - Add `insurer_storage_lines` and `uncovered_share` to the bindings of `uncovered_storage_days`, with baseline `uncovered_share: '0'`.

**S2 — `contents_ext_closing_payment`: same defect as S1**
- `declined_share: MX(0, denied_writeoffs - disputed_amount)` comes from the sentence "...the closing payment carries the carrier_denied_line write-offs ... less the disputed amount, never below zero". "The disputed amount" belongs to factor `declined_lines_dispute`.
- `uncovered_share: insurer_storage_lines * unpaid_storage_days / period_days` comes from the sentence "...times the unpaid storage days, divided by the tier's period length". "The unpaid storage days" belongs to factor `unpaid_storage_tail`.
- Same fix: move `denied_writeoffs` and `declined_share` into `declined_lines_dispute`, and `insurer_storage_lines` and `uncovered_share` into `unpaid_storage_tail`, each with a baseline of '0'.

**S3 — `task_tools.py`: the docstrings of five charge tools promise something the code doesn't do (XF D2)**
- The tools are `charge_customer_vault_storage_2f9c3128`, `charge_declared_value_coverage_b3c8ef16`, `charge_pack_back_boxes_26b5c86b`, `charge_furniture_reset_9904d302` and `charge_return_truck_loads_2b0047ce`.
- Each docstring says: "A second call for the same job, period [date] and amount books nothing new."
- The code makes the second row insert a no-op (the row id repeats). It then still runs `balance = half_up(job.balance_due + amount)` and `ctx.update(...)`, so a repeat call raises the job's balance a second time.
- Publishing the sentence as written would be false, and leaving it out would drop part of the tool's contract. Fix either the code (skip the balance update when the insert is a no-op) or the docstring.
- Related, with no docstring claim involved: in `pay_contents_customer_share_24e82212` and `pay_contents_closing_balance_f918d993` the payment id is built from job, method and amount. A second real payment of the same amount and method would post no new payment row but still lower the balance. That contradicts "the payment is posted in full".

**Secondary (renderable as-is, but XF C1 treats it as RED, so worth fixing in the same round)**
- **C1 — `contents_ext_return_truck_loads`:** two of its overwrites retire whole base sentences of `contents_evt_packout_and_cleaning`, including parts that don't conflict. `replaced_by` restates those parts, so nothing is lost, but the base document would show them as "no longer in force":
  - "Truck trips are billed per load and the inventory report once per job." — the inventory-report half doesn't conflict.
  - "The job must be in authorized, in_custody or return_scheduled status when a packout, cleaning or disposal line is charged." — this is the base state-gate condition (`pk_state`).
- **Rounding tolerance:** all seven policies declare `rounding_epsilon: 1.0e-09` as their own constant. check_docs requires the literal "1e-09" in a document of each policy. When I render, I'll state it in each computation document as part of how half-up rounding is applied.
- **Base text (frozen):** "At custody start the vault count is the boxes packed divided by the tier's vault capacity, rounded up". The two tiers without storage, On-Site Contents Manipulation and In-Plant Contents Cleaning, have a vault capacity of 0, so this sentence divides by zero there. It has no effect because neither tier carries storage.
