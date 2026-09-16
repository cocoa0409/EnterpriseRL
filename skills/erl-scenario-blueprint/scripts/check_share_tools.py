"""Blueprint gate: verify share_tools expose a UNIFORM, COMPLETE id-lookup layer.

DESIGN (why this shape). A live agent knows no internal row id a priori — it must
LOOK UP every id it uses, starting from what the caller can state. The simplest
design that makes this complete by construction is: for EVERY table in the schema,
ship one share READ tool that finds that table's records, taking ALL of the table's
`_id`-postfix fields as OPTIONAL arguments (each defaulting to "" / None). Then any
record is retrievable by any id it carries — its own primary id OR any foreign key —
so from the located customer row you reach every customer-owned entity in one or a
few hops (find_systems(customer_id=…) → a system_id → find_components(system_id=…) →
a component_id → find_warranty_claims(component_id=…), and so on), with no ad-hoc
per-entity lookups and no reachability guesswork.

WHAT THIS CATCHES. The bug it prevents is the "god's-eye view": a gold trajectory
that operates on a row by an id no agent could have obtained, because share_tools
offered no way to look that table up. The classic instance is `get_system(system_id)`
existing while nothing yields a `system_id`. Under the uniform design that is
impossible — every table, including `systems`, has an all-ids finder.

THE CHECK (per table). For every table T in db_schema:
  - there is a share READ tool that does ctx.find(T, …), and
  - its parameters INCLUDE every `_id`-postfix field of T, and
  - each of those id parameters is OPTIONAL (has a default).
A table with no such finder — or one whose finder misses an id field or makes it
required — is a HARD failure.

IDENTITY ENTRY (also checked). A live agent starts knowing only what the caller can
state — never an internal id. So the customers finder is ALSO the entry point: beyond
customer_id it must expose at least one NON-id customers field (phone / email / name / …)
as an optional param, so the id can be bootstrapped from what the caller says. There is
no separate `locate_customer`; this same finder both enters by attribute and traverses by
id. A customers finder that takes ONLY customer_id is unenterable — a HARD failure.

Usage (from the repo root):
  .venv/bin/python skills/erl-scenario-blueprint/scripts/check_share_tools.py env/<scenario>

Pure stdlib. Reads db_schema.json + share_tools.py (AST, never executed).
Exit 0 = SHARE TOOLS OK; exit 1 = a table is missing its all-ids finder.
"""
import ast
import json
import os
import sys


def _id_fields(fields):
    return [f for f in fields if f.endswith("_id")]


def parse_read_tools(path):
    """AST-parse every @tool(rw="read") function -> its params, which params are
    OPTIONAL (defaulted), and the tables it ctx.find's (string-literal first arg)."""
    tools = []
    tree = ast.parse(open(path).read())
    for fn in tree.body:
        if not isinstance(fn, ast.FunctionDef):
            continue
        owner = rw = None
        for dec in fn.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, "id", None) == "tool":
                for kw in dec.keywords:
                    if kw.arg == "owner" and isinstance(kw.value, ast.Constant):
                        owner = kw.value.value
                    if kw.arg == "rw" and isinstance(kw.value, ast.Constant):
                        rw = kw.value.value
        if owner is None or rw != "read":
            continue
        # positional params (skip ctx) + which are optional (defaults align to the tail)
        pos = [a.arg for a in fn.args.args if a.arg != "ctx"]
        opt = set(pos[len(pos) - len(fn.args.defaults):]) if fn.args.defaults else set()
        # keyword-only params too
        for a, d in zip(fn.args.kwonlyargs, fn.args.kw_defaults):
            pos.append(a.arg)
            if d is not None:
                opt.add(a.arg)
        finds = []
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name) and node.func.value.id == "ctx"
                    and node.func.attr in ("find", "fuzzy_find") and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                finds.append(node.args[0].value)
        tools.append({"name": fn.name, "params": set(pos), "optional": opt, "finds": set(finds)})
    return tools


def covering_finder(T, id_fields, reads):
    """A share read tool that finds T and exposes every id field of T as an OPTIONAL
    parameter — return its name, or None."""
    for r in reads:
        if T in r["finds"] and set(id_fields) <= r["params"] and all(f in r["optional"] for f in id_fields):
            return r["name"]
    return None


def blueprint_dir(root):
    """The scenario constitution lives in env/<scenario>/blueprint/ (new layout);
    fall back to the env root for legacy scenarios. Same sentinel file as the
    runtime loader, so the check always reads what the runtime will read."""
    sub = os.path.join(root, "blueprint")
    return sub if os.path.exists(os.path.join(sub, "blueprint.yaml")) else root


def main():
    if len(sys.argv) < 2:
        print("usage: check_share_tools.py env/<scenario>")
        sys.exit(2)
    root = sys.argv[1]
    bdir = blueprint_dir(root)
    schema = json.load(open(os.path.join(bdir, "db_schema.json")))
    reads = parse_read_tools(os.path.join(bdir, "share_tools.py"))

    print(f"🔎 share_tools per-table id-lookup check  ({os.path.basename(root.rstrip('/'))})")
    print(f"   tables: {len(schema)}   share read tools: {len(reads)}")
    print(f"   {'table':28} {'id fields':40} finder")
    print("   " + "-" * 92)

    missing = []
    for T in sorted(schema):
        idf = _id_fields(schema[T])
        finder = covering_finder(T, idf, reads)
        status = finder if finder else "*** MISSING ***"
        print(f"   {T:28} {','.join(idf) or '(none)':40} {status}")
        if finder is None:
            # explain the closest failure
            targeting = [r for r in reads if T in r["finds"]]
            if not targeting:
                why = "no share read tool does ctx.find on this table"
            else:
                r = targeting[0]
                miss = [f for f in idf if f not in r["params"]]
                req = [f for f in idf if f in r["params"] and f not in r["optional"]]
                why = (f"{r['name']} finds it but " + "; ".join(filter(None, [
                    f"misses id params {miss}" if miss else "",
                    f"makes {req} required (must be optional)" if req else ""])))
            missing.append((T, why))

    # identity entry: any read tool that ctx.find's the customers table must query on
    # real customers fields — a drifted entry (params not on file) leaves the agent no
    # way to bootstrap the customer id from what the caller states.
    cust_fields = set(schema.get("customers", []))
    cust_id_fields = set(_id_fields(schema.get("customers", [])))
    cust_finders = [r for r in reads if "customers" in r["finds"]]
    for r in cust_finders:
        extra = sorted(r["params"] - cust_fields)
        if extra:
            missing.append(("customers", f"{r['name']} takes params {extra} that are not "
                                         "fields of the customers table"))
    # entry point: at least one customers finder must expose a NON-id stateable attribute
    # (optional), or the agent can never enter — it would need the internal id up front.
    if cust_finders and not any(
            (r["params"] - cust_id_fields) & r["optional"] for r in cust_finders):
        missing.append(("customers", "no customers finder exposes a non-id stateable attribute "
                                     "(e.g. phone_number/email/name) as an optional param — the "
                                     "customer id cannot be bootstrapped from what the caller states; "
                                     "add those attributes to the customers finder (it is the identity entry)"))

    ok = not missing
    if missing:
        print("\n  [FAIL] tables without a complete all-ids finder:")
        for T, why in missing:
            print(f"           - {T}: {why}")
        print("  Every table needs one share READ tool that ctx.find's it and takes ALL of its "
              "_id-postfix fields as OPTIONAL args (default \"\"), e.g. "
              "find_<table>(<id1>=\"\", <id2>=\"\", ...).")
    else:
        print("\n  [PASS] every table has a share read finder covering all its _id fields (optional)")

    print("SHARE TOOLS OK" if ok else "SHARE TOOLS NOT OK — add the missing all-ids finders and re-run")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
