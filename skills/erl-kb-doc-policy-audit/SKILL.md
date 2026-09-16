---
name: erl-kb-doc-policy-audit
description: Audit one difficulty's published KB documents: whether they are a lossless translation of that difficulty's structured policy, whether the materials visible to a rollout alone uniquely entail the same solution as the policy — including whether a careful reader can derive, hop by hop, the problem tree the customer never mentioned — and whether they state each dependency exactly as the source states it and no further: each prerequisite's prerequisite sentence carried verbatim on the blocked side in its declared form — a state-form sentence never restated as an action, no other problem's tool name or route stated beyond it, no chain aggregated, and no title that mirrors a task; and, for every computation, whether its computation document, with the product figures it names, yields a definite wrong number while every declared factor's ladder is carried in full in its own document, findable from the customer's records and referenced by nothing. First perform and freeze a visible-context blind audit, then reveal the policy and run a full-domain two-way scan and a dependency-form scan. The output is a per-task verdict with evidence — find every problem, report every problem, never edit the documents and never arrange the fix. It defines audit strategy only, and has nothing to do with orchestration.
---

# erl-kb-doc-policy-audit (doc <-> structured policy)

Audit the published documents corresponding to the one product charter of a difficulty: **find every problem they have, report them one by one, with re-checkable evidence.** And there it stops — you edit no document, and you arrange no one to fix anything. Every command is run from the enterprise_rl repository root.

## Input: the two sides and how they relate

| Side | Artifacts |
| --- | --- |
| Structured policy side | That difficulty's `tasks/<difficulty>/<product>.extended.yaml` (the base section + `extended_policies`, including each policy's `overwrite` and `prerequisite` with its prerequisite sentence and its form), the `task_tools.py` beside it, and the scored solutions of the M tasks together with their `prerequisite_closure` |
| Visible material side | That product's published `docs/<product>/*.json` (title/content), the share/task tool schemas exposed at runtime, DB records obtained through tool-shaped queries, the information the user simulator states per `user_scenario`, and the same system background and `frozen_time` as the runtime |

The relationship between the two sides is the entire object of this audit: **the documents are one natural-language rendering of the structured policy**. The policy side is the single source of truth for what is normative; the document side is the only surface the solver can see. What must be decided is whether the two correspond losslessly, and whether the visible side alone yields the same answer.

**The policy side is taken as given in this audit and is not re-audited.** Whether it is self-consistent and whether it uniquely entails a solution belong to another layer of judgement; here the only question is "have the documents translated it faithfully". If a contradiction found during the audit actually originates on the policy side (an undeclared override, or a policy that is genuinely ambiguous), record it honestly as a problem and note its nature, but do not re-judge the documents on that basis.

## Core constraint: one relationship, three parts that cannot substitute for each other

There is only one relationship to prove — **the published documents are a lossless natural-language translation of the structured policy: nothing added, nothing dropped, nothing changed in meaning, and the visible materials entail the same unique solution as the policy side — while stating each dependency exactly as the source states it and nothing beyond**. The documents are the context the solver reasons from, never the route it follows: each prerequisite sentence stands verbatim on the blocked side, and which write brings a waited-on state about, how the hops chain and in what order the writes land are what the solver works out from the depended-on rules and the records, never readable off a route, another problem's tool name or an aggregated chain. It must be proved by three parts together, and none may be omitted:

| Part | What it proves | Recorded when it fails |
| --- | --- | --- |
| Runtime blind audit | From the materials a rollout can actually see, the branch this task triggers — including every hop of the problem tree — can be derived and is unique, and equals the policy side's solution | `KB-RUNTIME RED` |
| Full-domain two-way translation scan | The **whole** domain of the relevant policies corresponds losslessly at the level of entailment, not merely the branch the current seed happens to hit | `KB-BIJECTION RED` |
| Dependency-form scan | Each prerequisite's prerequisite sentence stands verbatim on the blocked side in its declared form, and no sentence, heading, table or example goes beyond it: no state-form sentence restated as an action, no other problem's tool named, no route, no chain aggregated; titles and openings are general rather than mirrors of a task | `KB-EXPLICIT RED` |

None can stand in for another: a blind audit walks one path and cannot cover untriggered branches; a scan proves item-by-item correspondence but cannot prove that someone who can see only the documents would really arrive at the same number; and a corpus can be faithful and solvable yet hand the solver the route, which only the dependency-form scan measures.

**Equivalence is judged at the level of entailment.** A paraphrase, or a carriage in which the prerequisite sentence states what a result waits on and the depended-on rule and the records supply which write brings it about, is a faithful translation whenever it yields exactly the same permitted actions, parameters, order and results at the same strength. The absence of a restated source sentence is never by itself an omission; what is an omission is a semantics the visible materials no longer entail.

## Output: a per-task verdict with evidence

The artifacts land at `env/<scenario>/audits/runtime_context/<difficulty>/<task_id>.md` and `env/<scenario>/audits/policy_kb/<difficulty>/<task_id>.md`, one of each per task; the dependency-form scan is recorded in the `policy_kb` file. Each must independently answer whether its part holds, and for every failure give **symptom -> root cause -> evidence -> affected document and location**. The evidence must be the quotations actually used: sentences from a document's title/content, tool query returns, simulator lines, and the policy side's rule sentences and bindings.

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

The following must be supplied along with the input, and the auditor only checks and cites them: that this difficulty's policy-side verdict has passed, that `check_docs.py` on its product and `check_traceability.py` on the published corpus for this difficulty are both green (their output lines come with the brief; the auditor runs neither), that the runtime-visible view and the DB access path have been provided, and that the gate snapshot (the commands and their actual output lines) came with the brief. If any is missing, report "incomplete input" as a problem.

**A machine green light is only a qualification.** `check_docs.py` can prove structure, coverage, explicit leakage, the verbatim carriage of every prerequisite sentence on its blocked side and the coarsest surface of routed wording; `check_traceability.py` proves only that every non-computed gold argument is copyable verbatim from context the agent can reach. Neither can tell whether the prose has changed the meaning of the event a clock starts from, an authority boundary or a discount base, and neither can prove that an equivalent restatement preserved the boundary. That is precisely why this skill exists.

The retriever's ranking, whether a preset query hits, and top-k position are **not** criteria: it is enough that the corpus is self-sufficient as a whole, and no document is required to rank first. What is a criterion is findability by reasoning: the documents a hop depends on must be reachable through the plain business words the records use for the relevant items, not only through phrasing borrowed from the dependent document.

### Step 1: perform and freeze the runtime blind audit, task by task

Before seeing any source-layer material, write the following into the `blind_answer` section of `runtime_context/<difficulty>/<task_id>.md`:

1. whether the user has clearly expressed the target object, the timing, the boundary of the action and the mode of authorisation; whether the simulator only conveys needs, responds passively under if/else, or executes a user tool at the agent's direction;
2. whether, at the frozen moment, the answer is act now, wait for a future condition, or refuse, and every visible eligibility ground;
3. the narrowest business object, the correlation keys, and the similar ledger rows to include or exclude;
4. each scored parameter's formula in words, its input rows, intermediates, grouping/base/cap/rounding, and its final value — and, for every rule the visible documents state that decides one of its inputs by tiers, the tier this customer is on and the query returns that put them there (including returns from another product's records where the tier rests on them);
5. the tool sequence executable on the spot, the owners, the forward and backward dependencies, and the terminal state;
6. **the problem tree derived from the visible materials alone**: for the thing the customer asked about, read from the visible KB what its governed result waits on — the prerequisite sentences the blocked policy's documents state; use tool queries to see which of those states do not hold right now; for a state-form sentence, search, with the words the records and the sentence use for that state, for the policy whose documents describe the write that brings it about; for an action-form sentence, find the policy that performs the named action; from them work out what must be resolved and in what order; repeat the same reasoning for each such problem until nothing remains. Write down the resulting list of problems, the direction of the dependencies, the handling order, and — for every hop — the chain of reasoning behind it: which visible sentences, which query returns, and how they combine. Mark each hop **state-derived** (the sentence named a state, and you found the write that brings it about from the depended-on documents and the records), **action-named** (the sentence named the action, and you found the policy that performs it), or **pre-solved** (another problem's tool name, a policy id, an aggregated chain, a route or an operational pointer handed the hop over without any reasoning). **This is the heaviest item of the blind audit**: the core difficulty of the task is that the customer never said it, so the agent must read the prerequisite sentences, check the records, find the writes and do several more things; if the tree cannot be derived, the task is unsolvable for the solver, no matter how rigorously the policy side is written; if a hop is pre-solved, the corpus has routed it.

The evidence must be **actually used** KB title/content quotations, tool query returns, user/agent tool outputs and simulator lines; writing "the document ought to say so" is not evidence. The file must first record the freeze declaration, the audit scope and the hash **and be written to disk**, and only then may the source layer and GT be read.

A two-way counter-proof is also required: the visible materials fully support the conclusion reached; and the closest alternative starting point in time, authoritative fact, object set, discount combination, business action or ordering must be excluded by some visible sentence or system record wherever the source itself closes that boundary; where the source leaves it open, the documents may not close it either (render Value 0), so record the openness as a policy-side note, never as a document defect. Do one further counter-proof for the problem tree: **the most natural wrong answer — "the customer asked for only this one thing, so do only this one thing" — must be excludable by reasoning from visible definitions, principles and records**: doing only that one thing must leave the governed result in a state the visible principles do not allow. If it cannot be excluded, the prerequisite does not exist on the visible surface (an omission); if it is excluded only by a pre-solved statement — another problem's tool name, a route, an aggregated chain — mark that hop pre-solved; a prerequisite sentence on the blocked side is the source's own form and is never a pre-solving.

And one for the calculation: **the fall-back answer — the number the computation document gives with no factor applied, reading only that document plus the product figures it names, wherever the corpus renders them — must be computable, definite, and different from the answer you reach.** Write it down. Then record, for every factor whose document you found, which words of the customer's records led you to it (the kind of record, its date or status, the product it belongs to, in the words the records themselves use); a factor document you could reach only by guessing that a variation exists, or only through the computation document's wording, is a findability omission; and a computation document that told you a variation exists, or that certain customers qualify for something else, has pre-solved the search.

Any early contact with the source layer or GT — including reading a scored value out of the brief, out of a recursive grep, or out of a side file — must be honestly recorded as `contamination_disclosure`, with that task's blind audit treated as void. Recursive grep is a measured leak path: think through the path scope before running any search.

### Step 2: reveal the source layer and compare the blind answer item by item

Once the blind answer is on disk, reveal the source layer and GT and append `gt_comparison`; **the blind_answer must never be modified to accommodate them**. Any of the following is recorded as **`KB-RUNTIME RED`**:

- the visible KB supports waiting/refusing while the source-layer solution writes directly (or vice versa);
- the visible KB offers two equally reasonable formulas, objects, actions or terminal states;
- the conclusion can only be explained by hidden compute/GT/the raw `initial_state`;
- the official DB and the customer's statement conflict with no visible policy to adjudicate;
- the KB adds a calculation, confirmation, review, step or procedure the structured source does not have, or drops or rewrites semantics the source does have;
- a tool schema, parameter, owner or executable effect disagrees with the source-layer solution;
- **a prerequisite declared in the source-layer `prerequisite` is not carried by the visible materials**: the prerequisite sentence on the blocked side is missing, its ordering connective, strength or form has changed, the depended-on policy's own rule is missing, or — for a state-form edge — the depended-on documents do not describe, in the words the sentence uses for that state, the write that brings it about, so the solver could read every document and still never work out which problem must be resolved before the root problem. This is the most consequential kind of omission — it does not make one number wrong, it makes the whole design intent of the task collapse;
- **the visible materials entail a prerequisite at a different strength**: the source makes it a hard gate while the visible principles leave it optional, advisable or combinable, or conversely a sufficient condition has become a necessary one, or a hint has been turned into a hard gate;
- **the visible KB writes in concrete world state**: the opening balance, status or missing record of some task written into a document as a policy fact (e.g. "this customer currently has arrears"), which both leaks the task and adds policy;
- **a factor declared in the source is not entailed by the visible materials**: its document is missing, a tier of its ladder is missing or softened, or the document cannot be reached from the words the customer's records use for its evidence, so a solver who has read the computation document and looked at the records still computes the fall-back number; or the computation document does not yield a definite number at all — a product figure it depends on being neither stated in it nor named in words that let the reader find it.

A hop that is correct but was marked **pre-solved** in the blind answer is not a `KB-RUNTIME RED` — the solution is still right — and is carried into the dependency-form scan (Step 3b) as a `KB-EXPLICIT RED`. The same holds for a document that aggregates several problems' prerequisites into one place: while the solution is still right it is a Step 3b matter, recorded once, under `dependency_form`, and nowhere else.

### Step 3: the full-domain two-way translation scan

Write into `policy_kb/<difficulty>/<task_id>.md`, freezing `source_to_kb`, `kb_to_source`, the difference list and the conclusion separately:

- **YAML -> KB forward scan**: break this task's extended policies, every base policy governing their subjects, the variants/parameters actually read, and the task-tool contracts into normative semantic atoms; locate an equivalent home for each in a title/content. Eligibility, authoritative sources, object correlation, time anchors and boundaries, the complete calculation domain, untriggered branches, acting base/order/cap/rounding, and owner/terminal state must all be covered — **it is not enough to check the branch the current seed hits**. List each `prerequisite` separately: its prerequisite sentence (`policy_source`) must appear verbatim, ordering connective and form intact, in a document of **the problem it blocks** (its hub or one of its fragments) and in no document of any other policy; every edge must then be resolvable, at the same strength, from that sentence together with the depended-on problem's own rules and the facts — for a state-form edge the depended-on documents must describe, in the words the sentence uses for that state, the write that brings it about; record that basis (the sentences and the records it rests on). The depended-on problem's documents must not carry the blocked side's prerequisite sentence (the depended-on side never discloses who waits on it); `condition`, `resolved_by` and `fallback_reason` are authoring fields with no home in any document. List the policy's `baseline` first: its `rule` must be carried complete in its computation document (role `baseline`) — every input, default value, standard rounding, window, base, order and the assembly of the result — with the policy's own default constants rendered there, every product figure it reads named, and nothing added; a default dropped or softened, or an assembly step moved into a factor document, is `KB-BIJECTION RED`. Then list each declared factor (`factors[].id`) separately as well: its factor document must carry the **whole ladder** — every tier's condition (every part of a compound condition, its window and threshold) and what the tier does: the value it selects for a `parameter` factor, or, for a `method` factor, the computation rule it applies with the operation, base, rounding mode, precision and moment, window or day-count convention, order of steps, cap moment or multiplier exactly as the source pins them — and the sweep covers every tier, not the one this task's customer sits on; a tier dropped, merged, rounded or softened, a threshold named under a business term but never stated in figures in that factor document, a compound condition reduced to one of its parts, or a method tier compressed into "calculated accordingly" is `KB-BIJECTION RED` even where this task's numbers are unaffected. The factor's `baseline`, `evidence` and `cross_difficulty` fields are authoring fields and appear nowhere. Where a factor's tier rests on another product's holdings or entries, the document names that product by its official name and the kinds of records it reads, so that a reader who has looked at those records can find the rule — a factor reachable only through this product's vocabulary is an omission on the findability side.
- **KB -> YAML reverse scan**: check sentence by sentence every business obligation, eligibility, prohibition, calculation, question, confirmation, wait, review, notification, exception handling, step and ordering in the formal prose; every normative claim must have a structured source. On the prerequisite side, additionally look for two additions that can only appear at this layer: cross-problem operational guidance such as "if unsatisfied, please call <tool> first to handle Y" inside one problem's clause (`resolved_by` and `condition` are authoring fields, not renderable text); and writing some task's opening world state in as a policy fact. A document that aggregates several problems' prerequisites into a table, checklist or route is recorded under Step 3b, not here. Anything the source does not require — "please confirm the amount/date with the customer", "review again before handling", "notify/verify after completion", "if it fails, follow some procedure" — is added policy, however reasonable or complete it may look.
- **The retired surface**: a base clause retired by some extended policy's `overwrite` must still have a bearing document — an override never breaks the bijection — but that document must write it as retired and no longer applicable. All three of these are `KB-BIJECTION RED`: a retired clause still stated in the KB as a rule in force; a retired clause vanishing from the KB entirely (present in the source, absent from the KB); and the KB retiring a clause the source-layer `overwrite` never declared retired (the KB legislating on its own). Also check that the same policy's other, unnamed clauses are still carried as clauses in force.
- A document's hidden meta may only help locate a candidate source; it can never prove that the prose is equivalent. `carries` / `covers` / `superseded_clauses`, a policy id, or a green gate may not substitute for a sentence-by-sentence semantic judgement.

What is audited is the whole domain of the relevant policy: **even if the current task's final numbers happen to be unaffected by the omitted branch, it is still recorded as `KB-BIJECTION RED`.** The same holds on the prerequisite side: even if some prerequisite happens not to affect the final numbers in this task, omitting its prerequisite sentence, changing its strength, its connective or its form, or carrying it in another policy's document is still a red light.

### Step 3b: the dependency-form scan

Write into the `dependency_form` section of `policy_kb/<difficulty>/<task_id>.md`. Using the blind answer's hop marks and a read of the whole product corpus, record as **`KB-EXPLICIT RED`** every place where the visible materials go beyond the form in which the source states a dependency:

- a restatement of a state-form prerequisite sentence that names the action, the performer or the other problem that brings the state about — the state form is what the source chose, and the corpus may not downgrade it to the action form; a restatement of either form that names a tool, a policy or another document;
- a sentence, heading, table or example that states a dependency or an order between problems that no prerequisite sentence of the source states, or that states one of the source's dependencies in a second document;
- a document that aggregates several problems' prerequisites into a dependency table, checklist, roadmap or complete route, or that strings several problems into a procedure or an ordered step list;
- cross-problem operational guidance such as "if unmet, first call <tool>", the tool of any other problem named inside the blocked problem's documents (whether or not an edge points at that problem), or the resolving action or problem named beside a state-form sentence; the blocked policy's own tool, named in its own invocation block, is none of these;
- a contrast between a wrong and a correct reading, a named mistake, or an example or FAQ that walks across problems or demonstrates the chain;
- a title or opening that restates a customer request, labels a procedure for a specific situation, or mirrors a task's situation rather than naming a general subject (the request type an `on_request` policy is defined by is that policy's general subject, and a title that names it is not a mirror);
- a depended-on document reachable only through phrasing borrowed from the dependent document, rather than through the words the records and the prerequisite sentence use for the state;
- a factor document that says which tier a customer, or most customers, fall on, that describes the reading a person without the rule would take as the mistake to avoid, or that writes a task's evidence rows in as a fact — the ladder is stated as a rule and the tier is what the reader derives from the records;
- a computation document (the baseline) that hints that anything modifies it — "unless otherwise provided", "adjustments may apply", "certain customers qualify for", "set out elsewhere", an exception list, a pointer — or a factor document that names, overrides or points at the computation document or another factor: the corpus is a discrete topology, and the existence of a factor is discovered only from the customer's records.

These are recorded even when the semantics are correct and the solution is unique: a faithful corpus that routes the solver through the chain fails its purpose. A prerequisite sentence carried verbatim on the blocked side, and its same-form restatements in the same document, are never RED: they are the source's own form. A sentence of a **base** rule that itself states an order or a dependency is rendered as the source has it — the KB may neither drop nor soften base law — so it is recorded as a policy-side note under Step 4, never as a KB verdict; what is judged here is what the rendering added beyond its source. Judge by meaning, not by keywords — a route in unusual wording is still a route, and a prerequisite sentence, which carries an ordering connective by construction, is not. Copied or repeated wording is not a finding of this scan: what matters is what a sentence states, never whether its words also occur elsewhere. As everywhere, report with quotations and locations; never rewrite.

### Step 4: settle the problems one by one

The auditor produces only verdicts and evidence, **edits no document**, and arranges no fix. Three disciplines may not be crossed:

- **Never accommodate in reverse.** Never suggest changing the policy side to fit the documents: when the visible text and the policy conflict, the faithful side is always the policy, and the problem is in the document.
- **Never dissolve a contradiction by hiding one side.** "base and extended were found to contradict each other, so the document states only one basis" is the classic case of using the documents to cover up a source-layer ambiguity. The correct handling is the next item.
- **Report policy-side problems, but do not let them change this skill's verdict.** If the substance of a contradiction is an undeclared override on the policy side, or a genuinely ambiguous policy, write that judgement into the report and note its nature; this skill's own verdict still lies only among `KB-BIJECTION RED` / `KB-RUNTIME RED` / `KB-EXPLICIT RED` / `PASS`.
- **Never recommend more than the source states.** When reporting an omission, name the semantics the visible materials fail to carry — never suggest naming the tool, the resolving problem or the route; when reporting a pre-solved statement, name the statement and the semantics it carries — never suggest simply deleting it, since the source's own prerequisite sentence must still stand.

Also, never attribute to the solving agent: a rollout agent's arithmetic slip is not a defect, and "the tool call succeeded" does not mean the translation is faithful.

### Step 5: closing out the difficulty

Once all M tasks have a frozen `blind_answer` / `gt_comparison`, `source_to_kb` / `kb_to_source` and `dependency_form`, and all three parts PASS, close out the difficulty:

- the audit files correspond one-to-one with the tasks, old revisions are traceable, and every comparison section carries a PASS;
- every normative atom of this difficulty's structured source is entailed by its product's docs, with nothing unborne, nothing borne with changed meaning, and no claim from outside the source; every prerequisite's prerequisite sentence stands verbatim, in its declared form, in a document of the policy it blocks and in no other policy's, and every hop is resolvable from it, the depended-on documents and the records; every declared factor's ladder is carried in full, every tier exact, in its factor document, findable from the records its tier rests on; and no other problem's tool name, route or aggregated chain is stated anywhere beyond those sentences and their same-form equivalents;
- its product's `check_docs.py` and this difficulty's `check_traceability.py` are re-run once on the final form, and their output lines are placed on record.

The closing output takes the form of **three part-verdicts per task + the difficulty's closing checklist**.

**Be clear about coverage**: this skill is organised per difficulty and audits only the product a difficulty has claimed. A base-type product claimed by no difficulty (pure distractor corpus) is **entirely outside this skill's audit scope** — its policies carry no GT, and its documents are guarded only by the render skill's own gates. That is an explicit coverage gap, not something covered elsewhere.

Only when "runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS" hold together does this difficulty's rendering pass the audit.

## Minimum format of an audit file

`env/<scenario>/audits/runtime_context/<difficulty>/<task_id>.md`

```markdown
# Runtime-context blind audit — <difficulty> / task <id>

## blind_answer
freeze hash, freeze time, auditor, the list of visible materials and the explicit forbidden list; the six blind-answer items and their visible evidence quotations (item 6 being the problem tree derived from the visible materials alone: the list of problems, the direction of the dependencies, the handling order, and for every hop the chain of reasoning — the sentences and query returns it combines — marked state-derived, action-named or pre-solved);
the two-way counter-proof: which visible sentence/system record excludes the closest candidate, and which visible definitions, principles and records exclude the wrong answer "do only the one thing the customer asked for". If there was contamination, add contamination_disclosure

## gt_comparison
the reveal time, item-by-item same/different, KB-RUNTIME RED or PASS
```

`blind_answer` must contain no hidden policy id, no GT parameter, no source-layer expected value and no conclusory self-justification.

`env/<scenario>/audits/policy_kb/<difficulty>/<task_id>.md`

```markdown
# Policy-KB bijection audit — <difficulty> / task <id>

## source_to_kb
the prose home of each source atom, the complete domain and the equivalence judgement at the level of entailment (including untriggered branches and the retired surface); each `prerequisite` listed separately: the document carrying its prerequisite sentence verbatim, its form, its resolution basis (the sentence, the depended-on rules, the records), whether the strength and the connective match, and confirmation that no other policy's document carries it

## kb_to_source
the source of each normative prose claim; the list of additions/rewrites/omissions; on the prerequisite side, the results of the two specific checks: cross-problem operational guidance, and a task's opening world state written in as a policy fact

## bijection_verdict
KB-BIJECTION RED or PASS; the affected documents and locations, and the relation to previous revisions

## dependency_form
every place the visible materials go beyond the verbatim prerequisite sentences and their same-form equivalents — a state-form sentence restated as an action, another problem's tool name, a route, the sentence carried in a second document, an aggregated chain; task-mirroring titles or openings — each with document, location and quotation; KB-EXPLICIT RED or PASS
```

Across rounds, append under `## revision_N`, leaving the text of older revisions untouched.

## Definition of done

This skill is complete not when "some number of reports have been written", but when every task of this difficulty can be answered with evidence on record: from the officially published documents and the records obtainable interactively alone, a careful reader can derive hop by hop the problem tree the customer never mentioned — reading each prerequisite sentence, checking the records and finding the write that brings the waited-on state about — and arrive at the same unique solution as the source layer, while no document states a tool, a route or an aggregated chain beyond those sentences; and the whole domain of the relevant policy (including every `prerequisite`, and every tier of every declared factor's ladder) corresponds losslessly, at the level of entailment, in the documents. Any failure is reported honestly, is not blamed on the rollout agent, and is not papered over by the audit report adding business steps or calculations of its own. The policy side's own self-consistency and unique solution belong to another layer of judgement, which this skill neither re-audits nor overturns.
