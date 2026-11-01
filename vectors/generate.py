"""Generate the language-neutral test vectors for the Graviteron unit (v0.4).

Run from the repository root:  python vectors/generate.py
The file vectors/graviteron-unit-v0.4.json is the reference; CI checks it is reproduced exactly.
"""

import json
import math
import pathlib

from graviteron.evidence.unit import reading

DAY = 86400.0
A = {"sensitivity": 0.9, "specificity": 0.9}
C = {"sensitivity": 0.8, "specificity": 0.95}
STD = {"a": A, "b": A, "c": C}

CASES = [
    ("zero-no-evidence", "No records: 0 G, inconclusive.", [], STD, None, None),
    ("one-confirms", "One 90/90 operator confirms (docs example 1).", [("a", True)], STD, None, None),
    ("one-contradicts", "One 90/90 operator signs false.", [("a", False)], STD, None, None),
    ("two-confirm-additive", "Two independent operators add.", [("a", True), ("b", True)], STD, None, None),
    ("three-confirm", "Three operators confirm (docs example 2).", [("a", True), ("b", True), ("c", True)], STD, None, None),
    ("contested", "Two confirm, one signs false (docs example 3).", [("a", True), ("b", True), ("c", False)], STD, None, None),
    ("decayed-60d-hl30d", "Three confirm, all 60 days old, half life 30 days (docs example 4).",
     [("a", True), ("b", True), ("c", True)], STD, {"a": 60 * DAY, "b": 60 * DAY, "c": 60 * DAY}, 30 * DAY),
    ("decay-one-half-life", "One check exactly one half life old counts half.", [("a", True)], STD, {"a": 30 * DAY}, 30 * DAY),
    ("renewed-check", "Age 0 with a half life: full weight (renewal restores it).", [("a", True)], STD, {"a": 0}, 30 * DAY),
    ("sybil-50-keys", "50 keys of one operator count once.", [("a", True)] * 50, STD, None, None),
    ("operator-majority", "One operator, keys 2 true 1 false: its majority verdict is true.",
     [("a", True), ("a", True), ("a", False)], STD, None, None),
    ("operator-tie", "One operator, keys tied 1 true 1 false: no verdict, counts nothing.",
     [("a", True), ("a", False)], STD, None, None),
    ("no-verdict", "Null verdict counts nothing and is noted.", [("a", None)], STD, None, None),
    ("unknown-operator", "Operator without measured reliability counts nothing and is noted.", [("ghost", True)], STD, None, None),
    ("asymmetric-confirms", "80/95 operator confirms: LR = 0.8 / 0.05.", [("c", True)], STD, None, None),
    ("asymmetric-contradicts", "80/95 operator signs false: LR = 0.2 / 0.95.", [("c", False)], STD, None, None),
    ("weak-operator", "60/60 operator confirms: inconclusive.", [("w", True)], {"w": {"sensitivity": 0.6, "specificity": 0.6}}, None, None),
    ("useless-operator", "50/50 operator: likelihood ratio 1, 0 G.", [("u", True)], {"u": {"sensitivity": 0.5, "specificity": 0.5}}, None, None),
    ("five-confirm-decisive", "Five 90/90 operators confirm.", [(k, True) for k in "abdef"], {k: A for k in "abdef"}, None, None),
    ("two-contradict", "Two operators sign false: strong contradiction, contested.", [("a", False), ("b", False)], STD, None, None),
    ("mixed-ages", "Two confirm, one fresh and one 90 days old, half life 30 days.",
     [("a", True), ("b", True)], STD, {"a": 0, "b": 90 * DAY}, 30 * DAY),
]


def r6(x):
    return round(x, 6)


def main():
    vectors = []
    for vid, desc, records, params, ages, hl in CASES:
        r = reading(records, params, ages=ages, half_life_seconds=hl)
        vectors.append({
            "id": vid,
            "description": desc,
            "input": {
                "records": [[op, v] for op, v in records],
                "params": params,
                "ages_seconds": ages,
                "half_life_seconds": hl,
                "interval": 0.9,
            },
            "expected": {
                "G_dB": r6(r.value),
                "interval_dB": [r6(r.low), r6(r.high)],
                "band": r.band,
                "independent_operators": r.independent_operators,
                "contradicted": r.contradicted,
                "contributions_dB": {k: r6(v) for k, v in sorted(r.contributions.items())},
                "notes": r.notes,
            },
        })
        assert math.isfinite(r.value)
    doc = {
        "name": "Graviteron unit test vectors",
        "version": "0.4.0",
        "definition": "docs/graviteron-unit.md",
        "tolerance_dB": {"G_dB": 1e-6, "contributions_dB": 1e-6, "interval_dB": 1e-4},
        "notes": "Values are rounded to 6 decimals. The interval comes from a Beta quantile found by "
                 "bisection, hence the wider tolerance. Records are [operator, true|false|null]; "
                 "keys of one operator are listed under the same operator name.",
        "vectors": vectors,
    }
    out = pathlib.Path(__file__).with_name("graviteron-unit-v0.4.json")
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(vectors)} vectors -> {out}")


if __name__ == "__main__":
    main()
