"""Check the Peanut Index forecast log: canonical form, sequence, hash chain, methodology hash.

Standard library only. Exit 0 when every check passes; otherwise print the first failure, exit 1.
Timestamps are checked separately with the OpenTimestamps client (`ots verify <file>.ots`).
"""

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def main():
    d = os.path.join(HERE, "entries")
    names = sorted(n for n in os.listdir(d) if n.endswith(".json"))
    prev, methodology = "0" * 64, None
    for i, n in enumerate(names):
        raw = open(os.path.join(d, n), "rb").read()
        e = json.loads(raw)
        checks = [
            (n == f"{i:06d}.json", "file name out of sequence"),
            (canonical(e) == raw, "not in canonical form"),
            (e.get("seq") == i, "seq does not match the file"),
            (e.get("prev_sha256") == prev, "prev_sha256 does not match the previous entry"),
            (i > 0 or e.get("kind") == "methodology", "entry 0 is not the methodology commitment"),
            (os.path.exists(os.path.join(d, n + ".ots")), "no OpenTimestamps proof"),
        ]
        for ok, why in checks:
            if not ok:
                print(f"FAIL {n}: {why}")
                return 1
        if e["kind"] == "methodology":
            path = os.path.join(HERE, e["methodology_file"])
            if not os.path.exists(path) or hashlib.sha256(open(path, "rb").read()).hexdigest() != e["methodology_sha256"]:
                print(f"FAIL {n}: {e['methodology_file']} is missing or does not match its hash")
                return 1
            methodology = e
        prev = hashlib.sha256(raw).hexdigest()
    if methodology is None:
        print("FAIL: no methodology entry")
        return 1
    print(f"OK: {len(names)} entries, chain head {prev}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
