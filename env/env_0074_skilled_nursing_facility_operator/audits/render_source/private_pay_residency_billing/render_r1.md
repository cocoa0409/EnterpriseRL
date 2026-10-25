# Renderer scan-first findings — private (render round 1, renderer agent a6001a4905504ed13, 2026-10-23)

Saved verbatim by the coordinator from the renderer's final report. The renderer wrote no documents.

BLOCKED: I stopped at the source scan, so no documents were written. Gate 0 passed (`VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`), but the scan of `private.extended.yaml` and its `task_tools.py` against XF_recipe.md found real mismatches between rule text and compute. I created nothing under `docs/private/` or `.doc_render_staging/private/`, and I did not add a RENDER.log line.

The mechanical checks were clean: every compute_basis quote, overwrite `replaced_by` and prerequisite sentence appears verbatim in its rule, every retired base clause exists, and tool docstrings match their bodies. All rounding uses RND(x + 1e-9), which your ruling covers.

## Mismatches (each changes the number in a world that can actually occur)

**1. `private_ext_late_notice_credit`: the request branch of the exclusion needs a recorded move date (XF B11, absent record)**
- Rule: "a span posted for a room the resident asked to move into, one whose tier is the agreement's own and whose first day is the move date recorded on the agreement or the date named by the resident's latest room-change request, carries the schedule the new-room rule sets and is owed no late-notice credit"
- `excl: True if (chg_tier == agr_tier and moved_on and (chg_from == moved_on or (req_on and chg_from == req_on))) else False`
- Where no move date is recorded but the latest room-change request names the span's first day (for example an own-tier span starting on the 1st that the request names), the rule excludes the span and the compute credits it.
- Fix: drop `moved_on and` from the request branch, or add "where a move date is recorded" before "the date named by…".

**2. `private_ext_room_change_credit`: "the move date" in the conversion carve-out has two readings**
- Rule (and the overwrite's `replaced_by`): "on an agreement that records a conversion to another payer source whose recorded conversion date falls on or after the first day of the advance's span and after the move date, no room-change credit is posted"
- The same rule redefines "the move date" through its factor: "where the move reprices from the date named by the resident's latest room-change request … the move date is that requested date; where it does not and the agreement records the move before the first day of the charge's span, the move date is the first day of the span".
- Compute uses the recorded date: `in_conv: True if (conv_rec and conv_on and moved_on and conv_on > moved_on and conv_on >= chg_from) else False`
- Divergent worlds: the move is recorded before the span and conversion falls on the span's first day; or conversion falls after the recorded move but on or before the requested date. The compute posts 0; the factor reading posts a full credit.
- Fix: write "after the move date recorded on the agreement" in both the rule and the `replaced_by`.

**3. `private_ext_conversion_credit`: the netted-days window drops the last converted day**
- Rule: "The netted days are the days of the late-notice credit on the charge, running consecutively from its first credited day, that fall on or after the first credited day and before the day the converted days stop; the netted amount of the other credits is, for each room-change or billing-error credit on the charge, its days running consecutively from its first credited day that fall in that same stretch"
- Earlier in the same rule, "the day they stop" means the last converted day ("are none where the first converted day falls after the day they stop"). So "before the day the converted days stop" leaves that day out.
- Compute (`stop_on: moved_on if mv_after else '9999-12-31'`, then `nd` and `oth`) nets every day through the last converted day, the span's last day included.
- Divergent world: no rate notice recorded, so the late-notice credit covers the whole span (say the 1st to the 31st), and conversion starts on the 15th. The compute nets 17 days; the rule nets 16, a difference of one day times the netted per-day amount.
- Fix: "on or before the last converted day" (and "that same stretch" follows).

**4. `private_ext_resumed_recharge`: the re-charge schedule's second tier contradicts the compute and the in-force base pricing clause**
- Rule (and the `recharge_schedule_rule` ladder): "where the notice had not run the rate change notice days by the first day of the advance's span but had run them by the conversion date recorded on the agreement, that date falling on or after the current schedule's effective date, it is the current private pay schedule; where a rate notice delivery date is recorded and that is not so, it is the preceding schedule; otherwise the re-charge schedule follows the standard method."
- `s_cur: True if (s_ran_conv and not s_ran_start and conv_on >= '2026-07-01') else (False if (notice and not s_ran_conv) else (s_ran_start and adv_from >= '2026-07-01'))`
- When a notice is recorded and had already run by the advance's first day, which is on or after 2026-07-01, the rule says preceding schedule and the compute says current. This is a common world (a notice delivered well ahead, an advance from August).
- The rule reading would also contradict the in-force base clause in `private_rate_schedule`: "Each charged day is priced at the tier's scheduled daily rate in effect for that day."
- Fix: "where a rate notice delivery date is recorded and the notice had not run the rate change notice days by the conversion date, it is the preceding schedule".

## Lesser findings (wording has a second reading or a figure isn't pinned)

**5. `private_ext_late_notice_credit`, `private_ext_new_room_span`, `private_ext_resumed_recharge`: "leave" or "booking"**
- Rule wording in all three: "the resident-private bed-hold days booked for the resident's leave that began latest (the booking posted first where two began on the same day)"
- Compute (`lv_*`, `bh_*`) is `XLATEST(... event_type='bedhold_day_booked', day_payer='resident_private')`, which picks one booking row. Bedhold books one row per reservation, service month and day payer, so a leave that crosses a month boundary has two bookings.
- Divergent world: a leave runs from 28 June to 4 July. The compute takes the July booking (from 1 July, inside a July span). The "leave" reading takes the leave starting 28 June, which is not inside the span, and gives 0.
- Fix: "the latest booking of resident-private bed-hold days (the one whose first booked day is latest, the one posted first where two share that day)".

**6. `private_ext_new_room_span`, `private_ext_resumed_recharge`: where the remaining leave days fall**
- Both rules overlap the leave days with the span days ("those booked days less the days reversed against that booking", then "that fall on or after the first … and on or before the last …"). Neither says where the unreversed days sit.
- The compute (`leave_in`, with `lv_start` set to the booking's first day) assumes they run in a row from the first booked day. `private_ext_late_notice_credit` says so ("counted from the first booked day"); these two don't.
- If a reversal comes off the front of a booking, for example `payer_days_available`, the overlap a reader takes from the records differs from the compute.

**7. `private_ext_room_change_credit`: the standard come-off schedule's explanation is incomplete**
- Rule: "the private pay schedule that governed the agreement's own rate on the move date recorded on the agreement: the current schedule once the agreement's rate notice had run its notice days by that date, and the preceding schedule while it had not"
- The explanation after the colon leaves out the condition that the move date is on or after the current schedule's effective date. The compute has it (`co_notice_in … and moved_on >= '2026-07-01'`), and so do the matching sentences in `private_ext_conversion_credit` and `private_ext_new_room_span`.
- Divergent world: a notice that had run by a move before 1 July 2026. The explanation says current schedule; the compute says preceding.

Findings 1–4 have to be fixed in the yaml before a render can pass. Findings 5–7 should go in the same rework brief so they don't come back as KB-audit reds after rendering.
