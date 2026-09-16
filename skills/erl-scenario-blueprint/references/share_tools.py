"""Shared tools for <scenario>. Output of the erl-scenario-blueprint skill.
Path: env/<scenario>/blueprint/share_tools.py

Living in share_tools.py makes every tool here a SHARE tool: always present in its owner's tool list, directly callable in every task.
Put here ONCE the three utilities every difficulty reuses: the complete record-lookup layer (one finder per table — and the customers finder DOUBLES AS THE IDENTITY ENTRY by additionally taking the caller-stateable attributes), the identity-verification write, and the transfer-to-human handoff — so per-difficulty instantiation never re-introduces duplicates.
Customer-originated WRITES do NOT live here. An action only the customer themself can take (consent, disposing of their own assets, signing) is difficulty-specific and is authored as a HIDDEN task tool (owner="user", reached via unlock_user/call_user) in that difficulty's task_tools.py — never as an always-on share tool.
The identity-verification write must itself COMPARE the caller-supplied attribute values against the record and DERIVE the match count to decide the boolean outcome, but it STORES ONLY that `verified` boolean — never the match count, which is not reproducible across correct agents. Both it and the transfer-to-human write take the INTERNAL `customer_id` (read from the customers finder's return) as their locator; a locator is how the record is fetched, not a credential the caller proved, so it NEVER counts toward the match. The transfer-to-human write has EXACTLY TWO reason values (POLICY_NOT_COVERED, CUSTOMER_REQUESTED).

Rules for every tool:
  - Docstring PROSE is written in English (the agent reads it as the tool schema); the
    structural tokens are fixed — the `Args:` section header (docstring introspection matches it
    literally), parameter names, table/field names, and controlled enum values.
  - Docstrings address the tool's USER. Introduce THIS tool on its own terms, in full, courteous
    product language: what business effect it accomplishes and, per argument, its meaning and
    exact format. Engineering vocabulary — table, row, schema, primary/foreign key — never
    appears in docstring prose: speak of records, profiles and reference numbers in business
    terms. Do not describe
    the tool's workflow position or its upstream/downstream tools, and do not squeeze every
    docstring into one rigid boilerplate. (Code comments below the docstring MAY use engineering
    terms — they are not part of the introspected schema.)
  - The first parameter is always `ctx: ToolContext`.
  - Declare @tool(owner=..., rw=...) with real type hints and a Google-style docstring (the OpenAI schema is derived from them); owner is "agent"|"user", rw is "read"|"write".
  - The ctx interface is closed and validator-enforced:
      id   : ctx.make_id(prefix, *identifying_args) — deterministic content hash; same prefix and args give the same id. Build it from the arguments that identify the row, and store it in the row's id field yourself.
      read : ctx.find(table, **match) -> list   (no kwargs = whole table)
             ctx.fuzzy_find(table, **match) -> list — the same, but values are compared after normalisation on both sides (casefold, letters and digits only). Use it for criteria the caller states in speech (names, phone numbers, emails), and plain find for ids read from records.
      write: ctx.create(table, row_key, **fields) / ctx.update(table, row_key, **fields) / ctx.delete(table, row_key) — inserts are idempotent on row_key; table and field names are checked against db_schema.json ({table: [field, ...]}).
      time : ctx.now()   (slice ctx.now()[:10] for the date part)
    Anything else on ctx is rejected.
  - A "write" tool must actually call ctx.create/update/delete; a "read" tool must never write (statically verified AND runtime-enforced).
  - Logical soundness and robustness are mandatory. Ordinary lookup and CRUD helpers must not encode
    product-policy qualification, state, ownership, timing, deduplication, or workflow guards; those
    decisions remain with the agent using the KB and DB. The frozen ctx layer still checks table/field
    names and read/write permissions, and malformed calls surface as informative runtime Errors. Each
    read and write must otherwise be schema-valid and behave correctly on empty or missing data.
  - Scoring is a DB-hash comparison, so every argument a tool STORES in a row or feeds into ctx.make_id must be reproducible by any correct agent: a controlled enumeration value, a number/amount fixed by the KB or a record, a value deterministically computed from KB rules and record fields, a date from ctx.now(), an id located in the DB, or an exact verbatim string the customer supplies (pinned in the persona as a fixed value the agent copies unchanged) — NEVER prose the agent composes or paraphrases (a written reason, a note, a loosely reworded value). A genuinely free-text parameter may be accepted only when it is neither stored nor part of any id.
  - Document every parameter EXHAUSTIVELY in the Google-style docstring — its meaning, type, exact allowed values or enumeration, and where the agent obtains it — because the docstring IS the introspected runtime schema the agent reads.
"""

from erlbench import ToolContext, tool


# ONE finder PER TABLE (check_share_tools.py enforces this): every table gets a read
# tool that ctx.find's it, taking ALL of the table's `_id`-postfix fields as OPTIONAL
# args (default ""). Any record is then retrievable by any id it carries, so the whole
# DB is reachable from the located customer id by construction. Repeat this block for
# every table in db_schema.json (customers, systems, components, invoices, …).
@tool(owner="agent", rw="read")
def find_<table>(ctx: ToolContext, <id_field_1>: str = "", <id_field_2>: str = "", ...) -> str:
    """<Introduce this lookup in business language: which business records it returns (e.g. "look
    up the warranty coverage records held by a customer"), which business dimensions the content
    covers, and which reference numbers already in hand can be used to retrieve it. Every criterion
    is optional — supply whichever are known; state what is returned on a hit and on a miss.>

    Args:
        <id_field_1>: <Id class — the reference number of the <business object> record itself>; leave "" if unknown.
        <id_field_2>: <Id class — the reference number of a <business object> this record is linked to (e.g. the owning customer)>; leave "" if unknown.
        ...: one optional arg per `_id`-postfix field in the <table> schema
             (docstring prose uses business terms — record / reference number — never table or field jargon).
    """
    match = {k: v for k, v in {"<id_field_1>": <id_field_1>,
                               "<id_field_2>": <id_field_2>, ...}.items() if v}
    rows = ctx.find("<table>", **match)
    return str(rows) if rows else f"No <table> records for {match}."


# The CUSTOMERS finder is the IDENTITY ENTRY (check_share_tools.py enforces this): a live
# agent starts knowing only what the caller can state — never an internal id — so the
# customers finder must ALSO accept the caller-stateable NON-id attributes on file (phone,
# email, full name, …), each OPTIONAL, so the agent can locate the customer row and read the
# internal customer_id from it. Finding is NOT verifying (verification is a separate write).
# Every attribute param must be a real field of the customers table (enforced), so the entry
# can never drift from the schema. There is no separate `locate_customer` — this one tool is
# both the by-id finder and the by-attribute entry. It matches through ctx.fuzzy_find, so what
# the caller states is compared to the profile after normalisation — a trailing full stop,
# spacing or case never blocks the lookup.
@tool(owner="agent", rw="read")
def find_customers(ctx: ToolContext, customer_id: str = "", <attr_1>: str = "", <attr_2>: str = "", <attr_3>: str = "") -> str:
    """<Introduce this in business language: look up the customer profile and establish whose
    account this call is about. It can be searched by the customer reference number, or by what the
    caller naturally states (mobile number, email, name); every criterion is optional — supply
    whichever are known. State which business content the returned profile carries (contact
    details, identity-document details, the date the profile was opened, and so on), and that
    looking a customer up is not the same as verifying their identity.>

    Args:
        customer_id: <Id class — the customer reference number>; leave "" if unknown.
        <attr_1>: <Verbatim/Fixed-format class — one piece of profile information the caller can naturally state (e.g. the registered mobile number, 10 digits)>; leave "" if not provided.
        <attr_2>: <another piece of profile information (e.g. the registered email)>; leave "" if not provided.
        <attr_3>: <another piece of profile information (e.g. the name)>; leave "" if not provided.
    """
    match = {k: v for k, v in {"customer_id": customer_id, "<field_1>": <attr_1>,
                               "<field_2>": <attr_2>, "<field_3>": <attr_3>}.items() if v}
    if not match:
        return "Error: provide at least one id or attribute to find the customer."
    rows = ctx.fuzzy_find("customers", **match)
    if not rows:
        return f"No customer matches {match}."
    if len(rows) > 1:
        return f"Error: {len(rows)} customers match {match}; ask for one more attribute to disambiguate."
    return str(rows[0])


@tool(owner="agent", rw="write")
def <verify_customer_identity>(ctx: ToolContext, customer_id: str, <attr_1>: str = "", <attr_2>: str = "", <attr_3>: str = "", <attr_4>: str = "", ... , <attr_n>: str = "") -> str:
    """<Introduce this in business language: verify the caller's identity and record the outcome of
    this verification; before looking up or transacting any business on the customer's account, this
    verification must pass. The comparison is performed by this tool, not judged by the agent: the
    tool compares each piece of identity information the caller states against the customer profile,
    counts how many match, and passes only when at least <K> match. The customer reference number is
    used solely to retrieve the profile and never counts as a match. Callers can usually state only
    some of the information, so pass only the values actually given, verbatim, and leave the rest "".
    The outcome is recorded; where a first attempt fails and a later attempt passes with more
    information, the pass stands.>
    <Design constraints (do NOT carry into the final docstring): the parameter list admits only
    profile information good enough to serve as an identity credential (mobile number, identity
    document digits, email, the date the profile was opened, ...); a bare name, easily known by
    others, gets no parameter. The persona pins down which items the caller will state, so the match
    count is reproducible.>

    Args:
        customer_id: <Id class — the customer reference number, read from the customer profile lookup. Required and never blank; used only to retrieve that profile, and not counted toward the number of matches.>
        <attr_1>: <meaning and format of the first piece of identity information the caller states (e.g. "the registered mobile number, 10 digits")>; leave "" if not stated (verbatim).
        <attr_2>: <meaning and format of the second piece of identity information>; leave "" if not stated (verbatim).
        <attr_3>: <meaning and format of the third piece of identity information>; leave "" if not stated (verbatim).
        <attr_4>: <meaning and format of the fourth piece of identity information>; leave "" if not stated (verbatim).
        ...
        <attr_n>: <meaning and format of the nth piece of identity information>; leave "" if not stated (verbatim).
        ...
    """
    if not customer_id:
        return "Error: customer_id is required; locate the customer first and pass their id."
    rows = ctx.find("<customer_table>", customer_id=customer_id)
    if not rows:
        return f"Error: no customer {customer_id}; cannot verify."
    rec = rows[0]
    # The tool owns the comparison: match each SUPPLIED (non-blank) attribute against the record on file.
    # The locator customer_id is deliberately NOT in `supplied` — fetching a record is not proving identity.
    supplied = {"<field_1>": <attr_1>, "<field_2>": <attr_2>, "<field_3>": <attr_3>, "<field_4>": <attr_4>, ..., "<field_n>": <attr_n>}
    matched = sum(1 for field, value in supplied.items() if value and str(rec.get(field)) == str(value))
    verified = matched >= <K>
    rid = ctx.make_id("<pfx_>", customer_id)
    # Store ONLY the reproducible `verified` outcome — never `matched` (a conversation-dependent count
    # that differs when a correct agent supplies a different valid attribute subset).
    # UPSERT + MONOTONIC: the row id is keyed on the customer, so a caller who fails a first attempt and
    # then passes with more attributes MUST end up recorded as verified. A plain idempotent ctx.create
    # would keep only the first (failed) write and pin verified=False forever — failing every correct
    # agent that verified after one miss. So carry a prior True forward and UPDATE the existing row
    # (create it only on first touch); verification never downgrades True -> False.
    prior = ctx.find("<verification_table>", <id_field>=rid)
    verified = verified or bool(prior and prior[0].get("verified"))
    if prior:
        ctx.update("<verification_table>", rid, verified=verified, verified_at=ctx.now())
    else:
        ctx.create("<verification_table>", rid, <id_field>=rid, customer_id=customer_id,
                   verified=verified, verified_at=ctx.now())
    return (f"Identity verified for {customer_id} ({matched} attribute(s) matched)." if verified
            else f"Identity NOT verified for {customer_id} (only {matched} of the required <K> attributes matched). Ask the caller for another attribute on file and call this tool again.")


@tool(owner="agent", rw="write")
def <transfer_to_human_agent>(ctx: ToolContext, customer_id: str, reason: str) -> str:
    """<Introduce this in business language: hand the customer over to a human representative to
    carry on, and record the handoff and its reason. State the two applicable situations, one for
    each of the two controlled values of reason.>
    <Design constraints (do NOT carry into the final docstring): exactly one of these per scenario,
    and it is mandatory; the reason enum is closed at exactly two values — only these two are
    unambiguous enough to score against; <R> is the repeat-request threshold this scenario pinned
    down in step 1, written verbatim into the docstring.>

    Args:
        customer_id: <Id class — the customer reference number, read from the customer profile lookup (the profile must exist).>
        reason: <Enum class — the reason for the handoff; one of POLICY_NOT_COVERED / CUSTOMER_REQUESTED, never free text.
            POLICY_NOT_COVERED — current policy offers no way to resolve the request;
            CUSTOMER_REQUESTED — the customer has explicitly asked for a human representative at least <R> times.>
    """
    allowed = {"POLICY_NOT_COVERED", "CUSTOMER_REQUESTED"}
    if reason not in allowed:
        return f"Error: unknown handoff reason '{reason}'. Valid: {', '.join(sorted(allowed))}."
    if not ctx.find("<customer_table>", customer_id=customer_id):
        return f"Error: no customer {customer_id}; cannot record handoff."
    rid = ctx.make_id("<hof_>", customer_id, reason)
    ctx.create("<handoff_table>", rid, <handoff_id_field>=rid, customer_id=customer_id,
               reason=reason, created_at=ctx.now())
    return f"Handoff to a human representative recorded for {customer_id} ({reason})."
