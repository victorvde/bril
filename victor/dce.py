import json
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

def local_reassignment_dce(bb):
    unused_dests = {}
    killed = []
    for j, i in enumerate(bb):
        for a in i.get("args", []):
            if a in unused_dests:
                del unused_dests[a]
        if not "dest" in i:
            continue
        d = i["dest"]
        if d in unused_dests:
            killed.append(unused_dests[d])
        unused_dests[d] = j

    new_bb = []
    for j, i in enumerate(bb):
        if j in killed:
            continue
        new_bb.append(i)

    return new_bb

def bb_dce(f):
    bbs = basic_blocks(f)
    instrs = []
    for bb in bbs:
        instrs += local_reassignment_dce(bb)
    return {
        **f,
        "instrs": instrs,
    }

def process_function(f):
    prev_f = f
    while True:
        new_f = prev_f
        new_f = prune_unused_results(new_f)
        new_f = bb_dce(new_f)
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

