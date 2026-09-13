---
name: erl-kb-doc-policy-audit
description: Audit one difficulty's published KB documents: whether they are a lossless translation of that difficulty's structured policy, and whether the materials visible to a rollout alone uniquely entail the same solution as the policy — including whether the documents alone let you walk, hop by hop, the problem tree the customer never mentioned. First perform and freeze a visible-context blind audit, then reveal the policy and run a full-domain two-way scan. The output is a per-task verdict with evidence — find every problem, report every problem, never edit the documents and never arrange the fix. It defines audit strategy only, and has nothing to do with orchestration.
---

# erl-kb-doc-policy-audit (doc <-> structured policy)

Audit the published documents corresponding to the one product charter of a difficulty: **find every problem they have, report them one by one, with re-checkable evidence.** And there it stops — you edit no document, and you arrange no one to fix anything. Every command is run from the enterprise_rl repository root.

## Input: the two sides and how they relate

| Side | Artifacts |
| --- | --- |
| Structured policy side | That difficulty's `tasks/<difficulty>/<product>.extended.yaml` (the base section + `extended_policies` + `workflows`, including each policy's `overwrite` and `prerequisite`), the `task_tools.py` beside it, and the scored solutions of the M tasks together with their `prerequisite_closure` |
| Visible material side | That product's published `docs/<product>/*.json` (title/content), the share/task tool schemas exposed at runtime, DB records obtained through tool-shaped queries, the information the user simulator states per `user_scenario`, and the same system background and `frozen_time` as the runtime |

The relationship between the two sides is the entire object of this audit: **the documents are one natural-language rendering of the structured policy**. The policy side is the single source of truth for what is normative; the document side is the only surface the solver can see. What must be decided is whether the two correspond losslessly, and whether the visible side alone yields the same answer.

**The policy side is taken as given in this audit and is not re-audited.** Whether it is self-consistent and whether it uniquely entails a solution belong to another layer of judgement; here the only question is "have the documents translated it faithfully". If a contradiction found during the audit actually originates on the policy side (an undeclared override, or a policy that is genuinely ambiguous), record it honestly as a problem and note its nature, but do not re-judge the documents on that basis.

## Core constraint: one relationship, two halves that cannot substitute for each other

There is only one relationship to prove — **the published documents are a lossless natural-language translation of the structured policy: nothing added, nothing dropped, nothing changed in meaning, and the visible materials entail the same unique solution as the policy side**. It must be proved by two halves together, and neither may be omitted:

| Half | What it proves | Recorded when it fails |
| --- | --- | --- |
| Visible-context blind audit | From the materials a rollout can actually see, the branch this task triggers is still visible and unique, and equals the policy side's solution | `KB-RUNTIME RED` |
| Full-domain two-way translation scan | The **whole** domain of the relevant policies corresponds losslessly, not merely the branch the current seed happens to hit | `KB-BIJECTION RED` |

Neither can stand in for the other: a blind audit walks one path and cannot cover untriggered branches, while a scan proves item-by-item correspondence but cannot prove that someone who can see only the documents would really arrive at the same number.

## Output: a per-task verdict with evidence

The artifacts land at `env/<scenario>/audits/runtime_context/<difficulty>/<task_id>.md` and `env/<scenario>/audits/policy_kb/<difficulty>/<task_id>.md`, one of each per task. Each must independently answer whether its half holds, and for every failure give **symptom -> root cause -> evidence -> affected document and location**. The evidence must be the quotations actually used: sentences from a document's title/content, tool query returns, simulator lines, and the policy side's rule sentences and bindings.

**Report problems; do not design the fix.** In particular, never suggest anything like "write only one basis in the document and the contradiction goes away" — that is not a repair, it hides the policy side's ambiguity inside the documents. And never attribute a problem to the solving agent: a rollout agent's arithmetic slip is not a defect, and "the tool call succeeded" does not mean the translation is faithful.

## Order: blind audit first, scan second

The blind audit must be completed and written to disk **before any structured policy is read**; only then is the policy side revealed for the two-way scan and comparison.

The reason is isolation: the two-way scan compares against the charter word for word, and whoever has read it can never again blind-audit the same documents — they will unconsciously fill the documents' gaps with policy knowledge, and "are the documents self-sufficient" is exactly what the blind audit tests. Putting the blind audit first gives it a clean context, so the isolation is guaranteed by the ordering rather than by self-discipline.

The cost is that if the scan subsequently finds a genuine omission in the corpus, this round of blind audit was "wasted". But its conclusion still carries information — it records exactly what an agent seeing only the documents would actually conclude, and that is itself evidence about rendering quality.

## Boundaries and isolation

- The write domain is only `env/<scenario>/audits/runtime_context/<difficulty>/` and `env/<scenario>/audits/policy_kb/<difficulty>/`; an audit does not change `blueprint/`, `tasks/`, `docs/` or the runtime `erlbench/` — a problem found goes into the report, and the audited document is not touched.
- **No other `env/` scenario may be read**, and neither may a sibling difficulty's tasks directory.
- The auditor must be independent of the agent that wrote these documents and of the auditor who judged the policy side.
- Each task is audited and written to disk separately; "another task in the same difficulty passed" never substitutes for this one.
- Any re-audit must preserve the old revision, freezing the new blind answer before appending the comparison; an old blind answer must never be rewritten to accommodate new documents.

## The two views

### A. The runtime-visible view (the only thing readable during the blind audit)

- the same system background and `frozen_time` as `run.sh`;
- the title/content of **the officially published KB of the product this difficulty belongs to**. Orchestration is pipelined per product, so a sibling product may not have finished rendering when you arrive; the visible surface is therefore this product. If another product's corpus happens to be on disk already it may be read, but never used as a criterion. This boundary has a cost: **cross-product contradictions are outside this skill's detection range**. It is acceptable because the render skill hard-requires every document to name its own official product name, and each difficulty's policy content is single-homed in its own product — but that is "structurally suppressed", not "proved absent".
- the share/task tool schemas exposed at runtime;
- DB records obtained through **tool-shaped queries**, i.e. actually calling a share finder / task tool against that task's world, rather than reading `initial_state` as a document; this access path must be supplied along with the input;
- the information the user simulator actually states per `user_scenario`.

During the blind audit the following are **explicitly forbidden**: `*.extended.yaml`, the task JSON's `evaluation_criteria` / `computations` / expected / `charter_scope` / `design_rationale` / `solvability_contract`, the raw `initial_state`, the documents' hidden meta, the render plan, the verification scripts, the tool implementations, existing GT and existing audit conclusions.

> A known weak point, stated honestly: of everything in this view, only "querying the DB in tool form" has no mechanical enforcement — it depends on how the access path is given. If all that can be handed to you is the raw `initial_state`, record that honestly in the file and mark that task's blind audit as "not blind on the DB side"; do not pretend it is clean.

#### Runtime message visibility and owner semantics (hard constraints)

- `user_scenario` is the hidden script driving the user simulator, not context injected directly into the agent. A fact in the script becomes visible to the agent only once the simulator actually sends a message, or actually calls a tool at the agent's direction and brings the result into the shared transcript.
- An `owner=user` tool call is like an `owner=agent` one: the result belongs to the shared runtime interaction record. After the simulator calls the tool, the return value enters the agent's context through that turn's tool result / the following user message. A user-owned return value must never be misjudged as a hidden field that "does not automatically enter the agent's context".
- The simulator may only convey needs per the script, supply information it is asked for, respond conditionally to what the agent has or has not done, and execute an `owner=user` tool the agent has explicitly handed over; it may not read policy/GT to hint at the next step, and it may not push the procedure along on the agent's behalf when the agent has neither asked nor handed over a tool.
- Reachability is therefore judged on the evidence of the messages, user/agent tool calls and their outputs actually in the shared transcript; business reference numbers, statuses or values generated by a tool at runtime need not be hard-coded into `user_scenario` in advance. Where the script does contain such a number, read it as knowledge the simulator may conditionally repeat once the corresponding event has occurred, not as a fact known before submission or a hint of the answer to the agent.
- If a user-owned tool has been called successfully and its result has entered the shared transcript while the agent still has not used it, examine the agent's state tracking, ordering judgement or tool selection first; "the persona lacks the literal value" is not a reason to call the task unsolvable. Only where the result genuinely never appeared in shared context, or where the simulator leaked it before the triggering event, is it recorded as a task visibility problem.

### B. The revealed source-layer view (after the blind answer is on disk)

Only once the blind answer is frozen to disk may this difficulty's `<product>.extended.yaml` (including `overwrite`), `task_tools.py` and that task's GT fields be read, for the two-way scan and the `gt_comparison`.

## The audit procedure

### Step 0: confirm the entry conditions

The following must be supplied along with the input, and the auditor only checks and cites them: that this difficulty's policy-side verdict has passed, that its product's `check_docs.py` and this difficulty's `check_traceability.py` are all green, that the runtime-visible view and the DB access path have been provided, and that the gate snapshot (the commands and their actual output lines) came with the brief. If any is missing, report "incomplete input" as a problem.

**A machine green light is only a qualification.** `check_docs.py` can prove structure, coverage and explicit leakage; it cannot tell whether the prose has changed the meaning of the event a clock starts from, an authority boundary or a discount base, and it cannot prove that an equivalent restatement preserved the boundary. That is precisely why this skill exists.

The retriever's ranking, whether a preset query hits, and top-k position are **not** criteria: it is enough that the corpus is self-sufficient as a whole, and no document is required to rank first.

### Step 1: perform and freeze the runtime blind audit, task by task

Before seeing any source-layer material, write the following into the `blind_answer` section of `runtime_context/<difficulty>/<task_id>.md`:

1. whether the user has clearly expressed the target object, the timing, the boundary of the action and the mode of authorisation; whether the simulator only conveys needs, responds passively under if/else, or executes a user tool at the agent's direction;
2. whether, at the frozen moment, the answer is act now, wait for a future condition, or refuse, and every visible eligibility ground;
3. the narrowest business object, the correlation keys, and the similar ledger rows to include or exclude;
4. each scored parameter's formula in words, its input rows, intermediates, grouping/base/cap/rounding, and its final value;
5. the tool sequence executable on the spot, the owners, the forward and backward dependencies, and the terminal state;
6. **the problem tree walked out from the visible documents alone**: for the thing the customer asked about, what conditions the visible KB says must hold before it can be handled; for each, use a tool query to decide whether it holds right now; for each that does not, whether the visible KB tells you which action would make it hold; and then repeat the same questioning for that action, until every condition holds. Write down the resulting list of problems, the direction of the dependencies, the handling order, and the document sentence and query return behind every hop. **This is the heaviest item of the blind audit**: the core difficulty of the task is exactly that the customer never said it, so the agent must read it out of the policy and do several more things; if the documents alone do not let you walk this tree, the task is unsolvable for the solver, no matter how rigorously the policy side is written.

The evidence must be **actually used** KB title/content quotations, tool query returns, user/agent tool outputs and simulator lines; writing "the document ought to say so" is not evidence. The file must first record the freeze declaration, the audit scope and the hash **and be written to disk**, and only then may the source layer and GT be read.

A two-way counter-proof is also required: the visible materials fully support the conclusion reached; and the closest alternative starting point in time, authoritative fact, object set, discount combination, business action or ordering must be explicitly excluded by some visible sentence or system record. Do one further counter-proof for the problem tree: **the most natural wrong answer — "the customer asked for only this one thing, so do only this one thing" — must be excludable by some visible clause**, i.e. the visible KB really does state that something must hold before it can be handled. If it cannot be excluded, the prerequisite simply does not exist on the visible surface.

Any early contact with the source layer or GT — including reading a scored value out of the brief, out of a recursive grep, or out of a side file — must be honestly recorded as `contamination_disclosure`, with that task's blind audit treated as void. Recursive grep is a measured leak path: think through the path scope before running any search.

### Step 2: reveal the source layer and compare the blind answer item by item

Once the blind answer is on disk, reveal the source layer and GT and append `gt_comparison`; **the blind_answer must never be modified to accommodate them**. Any of the following is recorded as **`KB-RUNTIME RED`**:

- the visible KB supports waiting/refusing while the source-layer solution writes directly (or vice versa);
- the visible KB offers two equally reasonable formulas, objects, actions or terminal states;
- the conclusion can only be explained by hidden compute/GT/the raw `initial_state`;
- the official DB and the customer's statement conflict with no visible policy to adjudicate;
- the KB adds a calculation, confirmation, review, step or procedure the structured source does not have, or drops or rewrites semantics the source does have;
- a tool schema, parameter, owner or executable effect disagrees with the source-layer solution;
- **a prerequisite declared in the source-layer `prerequisite` has no corresponding clause in the visible KB**: the solver could read every document and still never know that something else must be done before the root problem. This is the most consequential kind of omission — it does not make one number wrong, it makes the whole design intent of the task collapse;
- **the visible KB states a prerequisite at a different strength**: the source says "it may not be handled until satisfied" while the KB writes "we suggest handling it first" or "it may be handled together", or conversely a hint has been turned into a hard gate;
- **the visible KB aggregates the prerequisite chain**: some document lays several problems' prerequisites out as a dependency table, a checklist or a complete route, so the solver can follow it without discovering each hop. That is both an addition (each `prerequisite` in the source declares one hop only, and no field declares the whole chain) and a direct erasure of the task's core difficulty;
- **the visible KB writes in concrete world state**: the opening balance, status or missing record of some task written into a document as a policy fact (e.g. "this customer currently has arrears"), which both leaks the task and adds policy.

### Step 3: the full-domain two-way translation scan

Write into `policy_kb/<difficulty>/<task_id>.md`, freezing `source_to_kb`, `kb_to_source`, the difference list and the conclusion separately:

- **YAML -> KB forward scan**: break this task's extended policies, every base policy governing their subjects, the variants/parameters actually read, the workflow and the task-tool contracts into normative semantic atoms; locate each one at its unique equivalent home in a title/content. Eligibility, authoritative sources, object correlation, time anchors and boundaries, the complete calculation domain, untriggered branches, acting base/order/cap/rounding, and owner/dataflow/terminal state must all be covered — **it is not enough to check the branch the current seed hits**. List each `prerequisite` separately: every edge's `condition` must appear equivalently, and at the same strength, in the bearing document of **the problem it blocks**, and the rule sentence its `policy_source` cites must also have a home in the corpus; the depended-on problem's documents must not restate that condition (otherwise the same semantics acquires a second home).
- **KB -> YAML reverse scan**: check sentence by sentence every business obligation, eligibility, prohibition, calculation, question, confirmation, wait, review, notification, exception handling, step and ordering in the formal prose; every normative claim must have exactly one structured source. On the prerequisite side, additionally look for three additions that can only appear at this layer: aggregating several problems' prerequisites into a dependency table, checklist or roadmap (no field in the source declares the whole chain); adding cross-problem operational guidance such as "if unsatisfied, please call <tool> first to handle Y" inside one problem's clause (`resolved_by` is an authoring field used for checking, not renderable guidance); and writing some task's opening world state in as a policy fact. Anything the source does not require — "please confirm the amount/date with the customer", "review again before handling", "notify/verify after completion", "if it fails, follow some procedure" — is added policy, however reasonable or complete it may look.
- **The retired surface**: a base clause retired by some extended policy's `overwrite` must still have exactly one bearing document — an override never breaks the bijection — but that document must write it as retired and no longer applicable. All three of these are `KB-BIJECTION RED`: a retired clause still stated in the KB as a rule in force; a retired clause vanishing from the KB entirely (present in the source, absent from the KB); and the KB retiring a clause the source-layer `overwrite` never declared retired (the KB legislating on its own). Also check that the retiring document does not restate the new basis's numbers (which would give that quantitative key a second home), and that the same policy's other, unnamed clauses are still carried as clauses in force.
- A document's hidden meta may only help locate a candidate source; it can never prove that the prose is equivalent. `carries` / `covers` / `superseded_clauses`, a policy id, or a green gate may not substitute for a sentence-by-sentence semantic judgement.

What is audited is the whole domain of the relevant policy: **even if the current task's final numbers happen to be unaffected by the omitted branch, it is still recorded as `KB-BIJECTION RED`.** The same holds on the prerequisite side: even if some prerequisite happens not to affect the final numbers in this task, omitting it, changing its strength, or aggregating it into a chain is still a red light.

### Step 4: settle the problems one by one

The auditor produces only verdicts and evidence, **edits no document**, and arranges no fix. Three disciplines may not be crossed:

- **Never accommodate in reverse.** Never suggest changing the policy side to fit the documents: when the visible text and the policy conflict, the faithful side is always the policy, and the problem is in the document.
- **Never dissolve a contradiction by hiding one side.** "base and extended were found to contradict each other, so the document states only one basis" is the classic case of using the documents to cover up a source-layer ambiguity. The correct handling is the next item.
- **Report policy-side problems, but do not let them change this skill's verdict.** If the substance of a contradiction is an undeclared override on the policy side, or a genuinely ambiguous policy, write that judgement into the report and note its nature; this skill's own verdict still lies only among `KB-BIJECTION RED` / `KB-RUNTIME RED` / `PASS`.

Also, never attribute to the solving agent: a rollout agent's arithmetic slip is not a defect, and "the tool call succeeded" does not mean the translation is faithful.

### Step 5: closing out the difficulty

Once all M tasks have a frozen `blind_answer` / `gt_comparison` and `source_to_kb` / `kb_to_source`, and both halves PASS, close out the difficulty:

- the audit files correspond one-to-one with the tasks, old revisions are traceable, and every comparison section carries a PASS;
- every normative atom of this difficulty's structured source has exactly one home in its product's docs, with nothing unborne, nothing borne in several places with changed meaning, and no claim from outside the source;
- its product's `check_docs.py` and this difficulty's `check_traceability.py` are re-run once on the final form.

The closing output takes the form of **two half-verdicts per task + the difficulty's closing checklist**.

**Be clear about coverage**: this skill is organised per difficulty and audits only the product a difficulty has claimed. A base-type product claimed by no difficulty (pure distractor corpus) is **entirely outside this skill's audit scope** — its policies carry no GT, and its documents are guarded only by the render skill's own gates. That is an explicit coverage gap, not something covered elsewhere.

Only when "runtime blind audit PASS + full-domain two-way scan PASS" hold together does this difficulty's rendering pass the audit.

## Minimum format of an audit file

`env/<scenario>/audits/runtime_context/<difficulty>/<task_id>.md`

```markdown
# Runtime-context blind audit — <difficulty> / task <id>

## blind_answer
freeze hash, freeze time, auditor, the list of visible materials and the explicit forbidden list; the six blind-answer items and their visible evidence quotations (item 6 being the problem tree walked out from the visible documents alone: the list of problems, the direction of the dependencies, the handling order, and the document sentence and query return for every hop);
the two-way counter-proof: which visible sentence/system record excludes the closest candidate, and which visible clause excludes the wrong answer "do only the one thing the customer asked for". If there was contamination, add contamination_disclosure

## gt_comparison
the reveal time, item-by-item same/different, KB-RUNTIME RED or PASS
```

`blind_answer` must contain no hidden policy id, no GT parameter, no source-layer expected value and no conclusory self-justification.

`env/<scenario>/audits/policy_kb/<difficulty>/<task_id>.md`

```markdown
# Policy-KB bijection audit — <difficulty> / task <id>

## source_to_kb
the unique prose home of each source atom, the complete domain and the equivalence judgement (including untriggered branches and the retired surface); each `prerequisite` listed separately: the bearing document of its condition, whether the strength matches, and whether it appears only in the document of the problem it blocks

## kb_to_source
the unique source of each normative prose claim; the list of additions/rewrites/duplications/omissions; on the prerequisite side, the results of the three specific checks: aggregation into a dependency table/checklist/route across problems, cross-problem operational guidance, and a task's opening world state written in as a policy fact

## bijection_verdict
KB-BIJECTION RED or PASS; the affected documents and locations, and the relation to previous revisions
```

Across rounds, append under `## revision_N`, leaving the text of older revisions untouched.

## Definition of done

This skill is complete not when "some number of reports have been written", but when every task of this difficulty can be answered with evidence on record: from the officially published documents and the records obtainable interactively alone, one can walk hop by hop the problem tree the customer never mentioned and arrive at the same unique solution as the source layer; and the whole domain of the relevant policy (including every `prerequisite`) corresponds losslessly, item by item, in the documents, with no document aggregating the prerequisites into a chain. Any failure is reported honestly, is not blamed on the rollout agent, and is not papered over by the audit report adding business steps or calculations of its own. The policy side's own self-consistency and unique solution belong to another layer of judgement, which this skill neither re-audits nor overturns.
