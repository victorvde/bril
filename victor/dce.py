import json
import sys

def prune_unused_results(f):
    used_results = set()
    for i in f["instrs"]:
        used_results |= set(i.get("args", []))

    return {
        **f,
        "instrs": [i for i in f["instrs"] if "dest" not in i or i["dest"] in used_results],
    }

def process_function(f):
    prev_f = f
    while True:
        new_f = prev_f
        new_f = prune_unused_results(new_f)
        # bbs = basic_blocks(new_f)
        # new_f = local_reassignment_dce(new_f, bbs)
        if prev_f == new_f:
            break
        prev_f = new_f
    return new_f

data = json.load(sys.stdin)
r = {
    "functions": [process_function(x) for x in data["functions"]],
    **data
}
json.dump(r, sys.stdout, indent=4)

