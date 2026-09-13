---
name: erl-entrance
description: End-to-end orchestrator: from a one-line scenario definition + N (number of difficulties) + M (tasks per difficulty), generate a complete erlbench customer-service scenario under env/{scenario}/; in each difficulty exactly 1 of the M tasks uses a workflow as its GT steps. Chains erl-scenario-blueprint, erl-task-instantiate fanned out per difficulty, erl-kb-doc-render fanned out per product, and the two audits erl-task-policy-audit and erl-kb-doc-policy-audit fanned out per difficulty. Use whenever the user asks to generate/build a complete scenario end to end, run the full synthesis pipeline, or "run erl-entrance". Executed from the enterprise_rl repository root; every artifact lands under env/{scenario}/.
---

# erl-entrance (orchestrating one complete scenario)

You are the pipeline conductor. There are three inputs: the one-line scenario definition (industry + company form, which is also the directory name), N (the number of difficulty directories, handed to the blueprint skill), and M (the number of tasks per difficulty, handed to the instantiate skill). All three come from the request; if any is missing, ask first and never assume a default; M must be a positive integer. **This is the only time in the whole run that you ask the user anything** — once it is running you do not check in, do not offer options and do not wait for approval: this document and the working skills together give you the criteria you need, and where a situation has no explicit route, judge it yourself by the closest established loop, push on, and record the decision and its reasoning in the worklog.

**You generate no content yourself, and you judge nothing to be right or wrong.** You do only the part none of the working skills can see: sequencing the steps, handing concurrent subagents non-overlapping inputs, driving the rework loops, and holding the cross-difficulty merge acceptance. Every working skill carries its own gates, domain discipline and criteria — invoke it and let it act per its SKILL.md, and **do not restate its steps, checklists, gate commands or criteria here**. Whether an audit passes is a conclusion the audit skill returns; you only receive PASS / RED and schedule accordingly: no code can decide "is this task uniquely solvable", and it is not yours to run.

## The orchestration map

Steps 2 and 3 are both **pipelined**: each line advances to its own next stage the moment it lands, without waiting for its siblings. There is exactly one barrier, at the end of step 2 — that is the cross-difficulty merge surface, which isolated generation cannot see.

```
Step 1  1 subagent: blueprint ──(its own gates all green)──► fan-out permitted
        └ no fan-out before all green: everything downstream reuses the names it fixes, verbatim
        └ the reason for a single agent is context isolation, not concurrency

Step 2  pipelined · no intermediate barrier · N lines always saturated
        d₁  instantiate ─► audit ──[PASS]──────────────────────────┐
        d₂  instantiate ─► audit ──[RED]─► rework ─► audit* ─► …   ┤
         ⋮                                                         ├─ each loops independently
        d_N instantiate ─► audit ──[PASS]──────────────────────────┘   none waits for another
             ▲ whichever lands first is audited first   * a re-audit resumes the ORIGINAL auditor
             └ rework goes back to that difficulty's original instantiate agent (resumed)

             ══════════ barrier: all N PASS ══════════
                             │
                    merge acceptance (cross-difficulty identifier check + re-run blueprint gates)
                             ▼
Step 3  pipelined · no barrier · C lines concurrent (C = number of products > N)
        extended type (<- one-to-one with the difficulties)
        p₁  render ─► audit ──[PASS]──────────────────────┐
        p₂  render ─► audit ──[RED]─► re-render ─► audit* ┤─ each loops independently
         ⋮                                                │  none waits for another
        base type (claimed by no difficulty)
        p_k render ─► done once gates are green, **no audit**  ─┘
             └ the cost: these documents are never bijection-audited at any point
                             ▼
Before   whole-scenario load check: validate_scenario => VALID
delivery └ the only place the constitution + every task + every document are loaded together
```

If a render-layer audit reports a contradiction whose substance is a source-layer miss, go back to the step 2 loop and fix the source, then walk both step 3 stages again.

**A base-layer defect is handled by exactly one criterion, and base is never edited in response.** If a defect reported by an audit or by rework lands in the base section of `blueprint/`, the only criterion is whether it affects the correctness of a task — whether it moves any scored value, GT, or unique solution. If it does not, do nothing about it — append one line to the worklog recording it as a known issue (`BLUEPRINT-KNOWN`, citing the report) and carry straight on to the next step. Do not stop for it, do not accumulate a pending-decision list, and above all do not take it to the user; the cost is explicit and accepted: that base text renders into the published KB as it stands. If it does affect correctness, the answer is still not to go back to step 1 and touch the blueprint — **base freezes the moment the blueprint gates are all green**, and changing it would overturn every sibling difficulty that has already passed and force them all back through audit. The correct handling is to send the audit report directory back to that difficulty's original instantiate agent (resumed by agentId) and require it, within its own write domain, to change the `extended` policy, the task and the workflow so as to **route around** the base defect — switch to a criterion that does not depend on that clause, change the world of the task so that the defective clause does not fall inside its domain, or make GT take a path that never passes through it; then re-run the gates and send it back to the original auditor for re-audit. If it cannot be routed around, then this difficulty's claimed scope sits on a bad clause: have the instantiate agent change what that task tests, within its claimed scope, still without touching base.

## Boundaries

The write domain is `env/<scenario>/`. Never modify the frozen runtime (`erlbench/`) or the working skills themselves. Every command is run from the repository root. **Read isolation (absolute)**: during synthesis, never read any other scenario directory under `env/` — the read domain is this scenario plus `erlbench/`; carry this constraint verbatim into every subagent's brief.

## Fan-out discipline (applies whenever you launch a subagent)

Subagents have a wall-clock limit, and a task with a large artifact will be cut off part-way, so **only what has landed on disk counts as output**. Every brief must require **persisting in batches, saving as you write**: save each finished piece immediately, run the corresponding gate as early as possible, and never hold long content in context to write out in one go at the end. Before finishing, clear away the temporary authoring scripts; do not leave them in the write domain.

**Being cut off is not failure, and you must not start a new agent** — a new agent begins from nothing, and all the design it had already worked out is lost. The correct handling is: first **look at what is actually on disk** (which files exist, where the content stops — do not go by the agent's own account), then resume the same agent by agentId (its context is still intact), and state in the brief what is already on disk and what is missing, so **it can carry on from the breakpoint rather than starting over** (passages already on disk should still be changed where they need changing; what is forbidden is pointless redoing, not amending the artifact). The EXACT subagent's initial instruction is:

```
{the original call, verbatim} resumed round={k}: on disk {which files exist, their sizes, where the content stops}; missing {what is absent} — carry on from the breakpoint, redo nothing already right
```

Acceptance recognises only **what is on disk and what the gates print**, never the subagent's own account: after it claims everything is green, you still re-run its gates yourself.

**Keep a running log throughout.** Every time you launch a subagent and every time one finishes, append a line to `env/<scenario>/worklog.md`, timestamped from the system clock. Append only; never rewrite an existing line. Under concurrency plus loops, the same unit reappears repeatedly — a truncation and resume, a rework and re-audit each add a round — and this log is the only place that can reconstruct "who ran what, when, in which round, and with what result". Fields: timestamp, `START`/`END`, skill, unit, round; `END` also records the result (the gate conclusion or the audit verdict); a resume is marked `resumed`, and a rework `in=<audit report directory>`.

```
2026-08-31T14:02:11  START  instantiate         d=membership_contract_desk  round=1
2026-08-31T14:48:03  END    instantiate         d=membership_contract_desk  round=1  gates=7/7 green
2026-08-31T14:48:20  START  task-policy-audit   d=membership_contract_desk  round=1
2026-08-31T15:31:55  END    task-policy-audit   d=membership_contract_desk  round=1  task0=PASS  task1=SOURCE-POLICY RED
2026-08-31T15:32:10  START  instantiate         d=membership_contract_desk  round=2  resumed  in=audits/policy_task/membership_contract_desk/
```

**Rework always takes the audit report directory as its input; never paraphrase it.** The symptoms, root causes, item-by-item quoted evidence and affected locations in the report are the only basis on which the reworker can decide what to change and how far; paraphrasing it merely loses the quotations and may well misread the verdict. Give the directory path in the brief and require the agent to read it through and respond to it item by item.

## Step 1 — the blueprint (one subagent)

Launch **one** subagent to invoke `erl-scenario-blueprint`, with the scenario definition and N as input, and its artifacts landing in `env/<scenario>/blueprint/`. The EXACT subagent's initial instruction is:

```
/erl-scenario-blueprint {one-line scenario definition, verbatim from the request} N={N}
```

It carries its own gates, and **there is no fan-out before they are all green** — everything downstream reuses the names it fixes, verbatim.

There is only one subagent at this step, so the reason for it is not concurrency but **context isolation**: one scenario constitution is easily large enough to consume a whole context, and the coordinator is the only role that must survive to step 4 (only it can hold the cross-difficulty merge acceptance and the two rework loops). Everything a working skill produces goes to a subagent, and the coordinator keeps only the orchestration and the gate output — which is exactly what "you generate no content yourself" means in practice. The moment its own gates are all green, base is frozen: after fan-out you never go back and change the blueprint, and any later base-layer defect is routed around inside the difficulty's write domain, per the criterion above.

## Step 2 — instantiation and source-layer audit (pipelined per difficulty, N lines saturated)

Both stages are per difficulty and align 1:1 by unit, so **there is no intermediate barrier**: auditing one difficulty does not depend on any other difficulty finishing.

Launch N subagents at once, each invoking `erl-task-instantiate` for one difficulty, with that difficulty's name, the summary and claim from the blueprint, and M as input. The EXACT subagent's initial instruction is:

```
/erl-task-instantiate env/{scenario} {difficulty} M={M} — never stage a whole file in context for one final write
```

plus one line giving the identifier band assigned to it. **Never** fan out the M tasks within one difficulty: they share one extended.yaml and one task_tools.py, and must be written in one pass by one context. The only thing you must coordinate is the **non-overlapping business identifier bands** (the phone-number and identity-document ranges the personas will state), assigned once before fan-out; every other namespace is kept from colliding by the blueprint's exclusive claims and by the skill's own id rules. Each subagent writes only its own `env/<scenario>/tasks/<difficulty>/`.

When dispatching an audit, the EXACT subagent's initial instruction is:

```
/erl-task-policy-audit env/{scenario} {difficulty} M={M}
```

delivering three things: that difficulty's claimed scope and M; the gate snapshot you just ran (the actual output lines); and the masked views, **constructed mechanically** according to that skill's view division, together with their hashes — you construct the masking, rather than relying on the auditor's self-discipline. The brief must **contain no scored value, gold parameter or intermediate whatsoever**, even one you have already verified; and it must warn that a recursive grep will pull the task JSON's self-describing fields into context. Both of these are measured leak paths, not hypothetical risks.

**Whichever difficulty lands first immediately advances to its own next stage, without waiting for its siblings**: re-run its instantiation gates (the one that depends on the published KB cannot run yet — leave it for step 3) -> launch an auditor to invoke `erl-task-policy-audit` on it -> on a red light, immediately take the **audit report directory** `env/<scenario>/audits/policy_task/<difficulty>/` as the rework input and send it back to **that difficulty's original instantiate agent** (resumed by agentId, design context intact) -> after rework, re-run the gates and send the audit report directory back to **its original auditor agent** (resumed by agentId, audit context intact) for re-audit. The rework EXACT subagent's initial instruction is:

```
/erl-task-instantiate env/{scenario} {difficulty} rework round={k}: env/{scenario}/audits/policy_task/{difficulty}/ — read every file in full, close each item one by one without regressing what passed, never stage a whole file in context for one final write, then re-run the full gate block
```

That difficulty loops on its own like this until it passes. The goal is that at any moment each of the N difficulties is in one of the states "writing / auditing / reworking", so concurrency stays saturated.

**A re-audit resumes the original auditor; you do not swap in someone new.** Rebuilding the audit context (the full policy text, the masked views, the previous rounds' verdicts and evidence) is extremely expensive, and a resumed auditor can compare directly against its own previous conclusions and recognise whether the rework merely reworded something, or has reopened a defect that had been closed — which a replacement cannot do.

The cost must be acknowledged and the focus of the re-audit adjusted accordingly: a resumed auditor has already seen the GT revealed in the previous round, so from round 2 onward its derivation is no longer blind. So the **first round** of audit focuses on whether an independent blind derivation lands on GT, while a **re-audit round** shifts to verifying item by item that the previous round's REDs are genuinely closed, and that the rework has introduced no new defect and regressed nothing already closed. The EXACT subagent's initial instruction is:

```
/erl-task-policy-audit env/{scenario} {difficulty} re-audit round={k}: verify each round-{k-1} RED is genuinely closed, no new defect, nothing regressed; append revision_{k} to the same report files
```

plus the rebuilt masked views with their hashes and the reworker's claims by item id only.

Only one thing remains non-negotiable: **the auditor and the reworker must always be two separate agents** — putting them in one context is the same as allowing "edit until the audit says pass".

**The only barrier of this step is at its end.** Once all N difficulties pass, you perform one cross-difficulty **merge acceptance** — re-run the blueprint gates, and check that no business identifier is duplicated across difficulties. This is the merge surface that isolated generation cannot cover, and the gate into step 3. Because the identifier bands were assigned before fan-out, this is usually just a verification; if a duplicate really does appear, fix the conflicting value and that difficulty must re-run its gates and its audit.

## Step 3 — rendering and render-layer audit (pipelined per product, more concurrent than N)

Rendering is per product, while the audit is done only for **extended-type** products — the extended type corresponds one-to-one with the difficulties, so the two stages align by unit and can be **pipelined with no barrier**, exactly as in step 2. The degree of concurrency is set by the number of products C, which is higher than the number of difficulties N.

**Rendering.** Enumerate every rendering input, **one group per product, one subagent per group, all groups launched concurrently in one go**, each subagent invoking `erl-kb-doc-render` on its own group:

- **extended type**: for each `env/<scenario>/tasks/<difficulty>/` directory, the `<product>.extended.yaml` in it plus the `task_tools.py` beside it form one input group.
- **base type**: each `<product>.yaml` under `env/<scenario>/blueprint/products/` that no tasks directory's `<product>.extended.yaml` has claimed forms an input group of its own.

The two types together cover exactly all of the blueprint's products, each belonging to exactly one group — claimed or not is a binary split, so nothing is duplicated and nothing is missed. Each group outputs to `env/<scenario>/docs/<product>/`, and the write domains are pairwise disjoint, so they can all run concurrently with no namespace coordination. The EXACT subagent's initial instruction is:

```
/erl-kb-doc-render env/{scenario} {product}
```

When dispatching an audit (extended type only), the EXACT subagent's initial instruction is:

```
/erl-kb-doc-policy-audit env/{scenario} {difficulty} {product}
```

delivering: that difficulty's claimed scope and the name of its product; the gate snapshot; the **runtime-visible view and the DB access path** — its blind audit must not read `initial_state` as a document, and only you can supply that access path; and the same anti-leak discipline as for the source-layer audit.

**Whichever product finishes rendering immediately advances to its own next stage, without waiting for its siblings**, split by type:

- **extended type**: re-run its render gates, plus that difficulty's instantiation gate that depends on the published KB (it scans the whole docs tree, which is still incomplete at this point — that can only withhold strings, so it may produce a false red and can never produce a false green; if it does go red spuriously, re-judge once the tree is complete) -> launch an auditor to invoke `erl-kb-doc-policy-audit` on that difficulty -> on a red light, take the **audit report directories** `env/<scenario>/audits/policy_kb/<difficulty>/` and `env/<scenario>/audits/runtime_context/<difficulty>/` as the rework input and send them back to **that product's original render agent** to re-render -> re-run the gates -> send them back to **that difficulty's original auditor agent** (resumed by agentId, audit context intact) for re-audit. That product loops on its own until it passes; the reasons for resuming, and their cost, are as in step 2. The re-render EXACT subagent's initial instruction is:

  ```
  /erl-kb-doc-render env/{scenario} {product} rework round={k}: env/{scenario}/audits/policy_kb/{difficulty}/ + env/{scenario}/audits/runtime_context/{difficulty}/ — read every file in full, close each item one by one, then re-run the gates
  ```

  The re-audit EXACT subagent's initial instruction is:

  ```
  /erl-kb-doc-policy-audit env/{scenario} {difficulty} {product} re-audit round={k}: verify each round-{k-1} RED is genuinely closed, no new defect, nothing regressed; append revision_{k}
  ```
- **base type**: re-run its render gates and that is all — **no audit**. It is claimed by no difficulty, and its policies carry no GT. Be clear about the cost and accept it: **these documents are never bijection-audited at any point**, and only the render skill's own gates stand behind them.

Once every extended-type product has passed audit and every base-type product's render gates are green, you add the final **whole-scenario load check**: run `validate_scenario` from the repository root, and it must return `VALID`. It is the only place the constitution, every task and every document are loaded together — each earlier gate looks only at a single difficulty or a single product, and a load failure often surfaces only when the whole tree is assembled. Only when all three hold at once (source-layer audit PASS + render-layer audit PASS + `VALID`) is the scenario delivered. If some audit reports a contradiction whose substance is a source-layer miss, fall back to the step 2 loop, fix the source, then re-render and re-audit that product through both stages.
