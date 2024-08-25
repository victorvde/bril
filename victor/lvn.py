import json
import random
import sys

def prune_unused_results(f):
    used_results = set()
    for i in f["instrs"]:
        used_results |= set(i.get("args", []))

    instrs = []
    for i in f["instrs"]:
        if "dest" in i and i["dest"] not in used_results:
            continue
        instrs.append(i)

    return {
        **f,
        "instrs": instrs,
    }

def basic_blocks(f):
    bbs = []
    current_bb = []

    def finalize():
        nonlocal current_bb
        if current_bb:
            bbs.append(current_bb)
        current_bb = []

    for i in f["instrs"]:
        if "label" in i:
            finalize()
            current_bb.append(i)
        else:
            current_bb.append(i)
            if i["op"] in  ["jmp", "br", "ret"]:
                finalize()
    finalize()
    return bbs

def gensym(s):
    return s + "_" + str(random.randint(0, 100000))

def local_ssa(bb):
    unused_dests = {}
    killed = []
    for j, i in enumerate(bb):
        if not "dest" in i:
            continue
        d = i["dest"]
        if d in unused_dests:
            killed.append(unused_dests[d])
        unused_dests[d] = j

    new_bb = []
    renames = {}
    for j, i in enumerate(bb):
        new_i = i
        new_args = [renames.get(x, x) for x in new_i.get("args", [])]
        if "dest" in new_i:
            if j in killed:
                d = i["dest"]
                new_dest = gensym(d)
                renames[d] = new_dest
                new_i = {
                    **new_i,
                    "dest": new_dest,
                }
            else:
                d = i["dest"]
                renames[d] = d
        new_i = {
            **new_i,
            "args": new_args,
        }
        new_bb.append(new_i)
    return new_bb

def local_value_numbering(bb):
    value2var = {}
    var2value = {}

    def normalize_arg(a):
        n = var2value.get(a)
        if n is None:
            return a
        na = value2var[n]
        return na

    def normalize(i):
        op = i["op"]
        args = i.get("args", [])
        if op == "id" and args[0] in var2value:
            return var2value[args[0]]
        nargs = tuple([var2value.get(a, a) for a in args])
        value = i.get("value")
        return (op, nargs, value)

    new_bb = []
    for i in bb:
        new_i = {
            **i,
            "args": [normalize_arg(a) for a in i.get("args", [])],
        }
        d = i.get("dest")
        # print(f"{d=}")
        if d and i["op"] in ["add", "sub", "mul", "div", "eq", "lt", "gt", "le", "ge", "not", "and", "or", "id"]:
            n = normalize(i)
            # print(f"{n=}")
            if n in value2var:
                new_i = {
                    **i,
                    "op": "id",
                    "args": [value2var[n]],
                }
            else:
                value2var[n] = d
            var2value[d] = n
            # print(f"{var2value=}")
            # print(f"{value2var=}")
        # print(f"{new_i=}")
        new_bb.append(new_i)

    return new_bb

def local_transforms(f):
    bbs = basic_blocks(f)
    instrs = []
    for bb in bbs:
        new_bb = bb
        new_bb = local_ssa(new_bb)
        new_bb = local_value_numbering(new_bb)
        instrs += new_bb
    return {
        **f,
        "instrs": instrs,
    }

def process_function(f):
    prev_f = f
    while True:
        new_f = prev_f
        new_f = prune_unused_results(new_f)
        new_f = local_transforms(new_f)
        if prev_f == new_f:
            break
        prev_f = new_f
    return new_f

data = json.load(sys.stdin)
r = {
    **data,
    "functions": [process_function(x) for x in data["functions"]],
}
json.dump(r, sys.stdout, indent=4)

