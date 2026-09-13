"""The task-tool skeleton for one difficulty. One of the artifacts of erl-task-instantiate.
Path: env/<scenario>/tasks/<difficulty>/task_tools.py

These are this difficulty's hidden task tools (they take the key parameters the agent has computed
and perform one atomic write). No domain examples are given; take the Python functions in this file
directly as the code skeleton and replace the placeholders according to the current blueprint /
policy / workflow / DB schema. Never wrap this file into a string constant, and never copy business
names, parameter sets, enum values or receipt fields from another scenario.

Tool contract (carried over from the blueprint):
  - Named <verb>_<object>_<uuid8>: uuid8 is an 8-hex suffix frozen at authoring time so names never
    collide across difficulties (the placeholders below show it as _<uuid8>).
  - HIDDEN: absent from every tool list; the name is registered only in <category>.extended.yaml
    (a workflow step / extended_policies.target_tool), and gold reaches it through unlock_* -> call_*.
    A share tool, by contrast, is always directly callable by name — the two are different.
  - @tool(owner="agent"|"user", rw="read"|"write"); owner follows the permission doctrine (the
    customer disposing of their own affairs -> user, a service action -> agent).

[Define the capability first, then write the function.]
  Before coding each tool, write down in the current task worklog: who uses it, the target business
  object, the atomic action one call completes, the exact account/status/business-record change, the
  observable result on success, and the shape of the receipt with all of its returned fields. For a
  lookup tool, write down the search boundary, the filter criteria, what a hit returns and what a
  miss means. If any of these cannot be stated, the tool's boundary is not yet closed; you may not
  lean on the function name, the implementation code, hidden GT, a later KB document or the author's
  common sense to supply the meaning.

[Docstring discipline: the docstring IS the complete runtime schema the agent reads.]
  - Every function docstring must contain, in order: a sufficient capability description, Args:, and
    Returns:. Sufficient does not mean piling on words or following a fixed sentence pattern; it
    means an agent that sees only the schema can tell, without guessing, what the tool does, how to
    construct each argument, and what it gets on success. The capability description must cover the
    target object, the atomic business effect, the exact status/account/business-record change, the
    observable result and what counts as success; a lookup must also cover the search scope, the
    filtering, what a hit contains and what a miss means.
  - Args: is in item-by-item bijection with the function signature: apart from ctx, every parameter
    appears exactly once — none missing, none extra, none merged. Each entry states the business
    meaning first, then declares exactly one of the following classes; the class, the type
    annotation, the target DB field, the implementation's conversion and the GT argument must all
    agree:
      Id class — state which kind of business object/record the reference number identifies, and the
        exact source from which it is reachable before the call;
      Fixed-format class — fully disclose every applicable dimension jointly fixed by the DB schema
        and the tool's actual format handling: unit, representation format, precision, rounding mode
        and rounding point, time zone, and the convention for an empty value; never leak the policy
        calculation;
      Enum class — list the closed set item by item, in exactly the literals and casing used in the
        schema, and state the unique business meaning that applies to each value; never list bare
        values only, a subset only, or write "for example";
      Verbatim class — point to the reachable source of the original text, and require it to be
        copied character for character, preserving wording, digits and punctuation, with no
        translation, normalisation, summarisation, addition or deletion; the whole parameter
        description must end exactly with ` (verbatim).`.
    There is no fifth free-text class, and no mixed class such as Enum/Fixed-format. If a parameter
    cannot be classified uniquely, split it, delete it or redefine it; fixed constants belong in the
    implementation and are not offered to the agent as a choice.
  - Returns: states the real shape of the return value, covering the business meaning, type and
    format of every field actually returned, and states what indicates the call completed and what
    business result is observable afterwards. Never write merely "returns the result" or
    "operation succeeded".
  - The docstring addresses the tool's user and introduces only this tool. Do not use implementation
    terms such as table, row, primary key, foreign key or schema; do not state the workflow position,
    the upstream/downstream tools or policy preconditions; do not write the policy formula for a
    numeric/date parameter. How a parameter should be represented belongs to the tool contract; why
    it takes that value belongs to the policy/KB, and the two are never mixed.

[The implementation and the public contract must agree.]
  - Row id = ctx.make_id(prefix, *all arguments); money is round(float(x), 2); time comes only from
    ctx.now(); writes go only through ctx.create/update/delete. Every other fixed-format parameter is
    handled at exactly the precision and format it publishes.
  - An ordinary task tool performs no business guard and no mechanical eligibility check; it simply
    executes one atomic CRUD with the arguments as declared. The underlying ctx checks on table
    names, field names and read/write permission are runtime infrastructure, not policy judgements
    the tool should encode.
  - When it is written, check parameter by parameter: signature, type annotation, target DB field,
    unique class, business meaning, reachable source or complete format/enum contract,
    implementation conversion, GT argument; then check each returned field of the implementation
    against Returns:. Any gap or contradiction must be fixed in the tool first.

[Iron rule: tools are basic and atomic, and never build in aggregation.]
  One tool makes one atomic state change. Never provide an aggregation tool that "folds a stretch of
  history into one derived value" — that would pre-bake exactly the multi-factor calculation and
  ledger reconciliation this task is meant to test, and hand the difficulty away. Wherever a value
  must be synthesised from history / another category / the tier, it is the AGENT that reads the
  history, looks up the cross-category holding, looks up the tier parameters, and works out
  compute.result itself, layer by layer, following the policy; it then passes that value into the
  write tool below as one fixed-format parameter. The tool simply lands that one write; it does not
  compute on the agent's behalf, and it does not judge same-row or cross-row policy preconditions.
  Cross-row, aggregate and time-window preconditions are policy, and the agent verifies them; a task
  tool never returns a policy-based refusal.
"""

from erlbench import ToolContext, tool


@tool(owner="agent", rw="read")
def <find_history_tool>(ctx: ToolContext, <holding_id>: str = "", <fk_or_type>: str = "") -> str:
    """<In the business language of the current domain, fully introduce what is being looked up, the
    search boundary, the filters available, the business content returned on a hit, and the explicit
    meaning of a miss.>

    Args:
        <holding_id>: <Id class — state the exact business object it identifies, and where that
            reference number is reachable from before the call.>
        <fk_or_type>: <Choose exactly one of Id / Fixed-format / Enum / Verbatim according to the
            current schema, and write out in full the source, format or closed enum semantics that
            class requires; also state whether an empty value is allowed when not filtering.>

    Returns:
        <State the return type and shape, the meaning and format of every business field, and the
        observable semantics of a hit and of a miss.>
    """
    match = {k: v for k, v in {"<holding_fk>": <holding_id>, "<type_field>": <fk_or_type>}.items() if v}
    rows = ctx.find("<event_table>", **match)
    return str(rows) if rows else f"No <event_table> rows for {match}."


@tool(owner="agent", rw="write")
def <compute_write_tool>(ctx: ToolContext, <holding_id>: str, <computed_amount>: float) -> str:
    """<In the business language of the current domain, fully state which business object the user
    completes what atomic action on, exactly what account/status/business-record change it produces,
    what the user can observe afterwards, and which receipt indicates the call completed. Never
    write the policy calculation.>

    Args:
        <holding_id>: <Id class — state what the target business object's reference number means, and
            where it is reachable from before the call.>
        <computed_amount>: <Fixed-format class — state the parameter's business meaning, and write out
            in full every applicable dimension of unit, format, precision, rounding, time zone or
            empty-value convention; do not write the policy logic behind the value.>

    Returns:
        <State the real receipt shape, the business meaning and type/format of every returned field,
        and the observable semantics that indicate successful completion.>
    """
    rid = ctx.make_id("<pfx_>", <holding_id>, <computed_amount>)      # includes every argument
    ctx.create("<event_or_intake_table>", rid, <id_field>=rid, <holding_fk>=<holding_id>,
               <amount_field>=round(float(<computed_amount>), 2), status="<CONST>", <date_field>=ctx.now()[:10])
    return f"<confirmation text, including {rid} and the booked value>."


@tool(owner="user", rw="write")
def <customer_confirm_tool>(ctx: ToolContext, <holding_id>: str, <computed_amount>: float) -> str:
    """<In the business language of the current domain, fully state which business object the customer
    themselves disposes of and how, exactly what account/status/business-record change it produces,
    what the customer can observe afterwards, and which receipt indicates the call completed. Never
    state the workflow position.>

    Args:
        <holding_id>: <Id class — state the exact reference number of the business object the customer
            disposes of, and where it is reachable from before the call.>
        <computed_amount>: <Fixed-format class — state the business meaning of the confirmed value, and
            write out in full every applicable dimension of unit, format, precision, rounding, time
            zone or empty-value convention; do not write the policy logic behind the value.>

    Returns:
        <State the real receipt shape, the business meaning and type/format of every returned field,
        and the observable semantics that indicate successful completion.>
    """
    rid = ctx.make_id("<pfx_>", <holding_id>, <computed_amount>)
    ctx.create("<table>", rid, <id_field>=rid, <holding_fk>=<holding_id>,
               <amount_field>=round(float(<computed_amount>), 2), status="<CONST>", <date_field>=ctx.now()[:10])
    return f"<confirmation text, including {rid}>."
