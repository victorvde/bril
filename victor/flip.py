import json
import sys

def process_instruction(i):
    if i["op"] in ["add", "mul"]:
        assert len(i["args"]) == 2, i
        return {
            **i,
            "args": list(reversed(i["args"])),
        }
    else:
        return i

def process_function(f):
    return {
        **f,
        "instrs": [process_instruction(x) for x in f["instrs"]]
    }

data = json.load(sys.stdin)
r = {
    **data,
    "functions": [process_function(x) for x in data["functions"]],
}
json.dump(r, sys.stdout, indent=4)
