import json
import pathlib

from graviteron.evidence.unit import reading

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = json.loads((ROOT / "vectors" / "graviteron-unit-v0.4.json").read_text())
TOL = DOC["tolerance_dB"]


def test_every_vector_is_reproduced():
    assert len(DOC["vectors"]) >= 20
    for v in DOC["vectors"]:
        i, e = v["input"], v["expected"]
        r = reading([tuple(x) for x in i["records"]], i["params"], ages=i["ages_seconds"],
                    half_life_seconds=i["half_life_seconds"], interval=i["interval"])
        assert abs(r.value - e["G_dB"]) <= TOL["G_dB"], v["id"]
        assert abs(r.low - e["interval_dB"][0]) <= TOL["interval_dB"], v["id"]
        assert abs(r.high - e["interval_dB"][1]) <= TOL["interval_dB"], v["id"]
        assert r.band == e["band"], v["id"]
        assert r.independent_operators == e["independent_operators"], v["id"]
        assert r.contradicted == e["contradicted"], v["id"]
        assert r.notes == e["notes"], v["id"]
        assert sorted(r.contributions) == sorted(e["contributions_dB"]), v["id"]
        for op, c in e["contributions_dB"].items():
            assert abs(r.contributions[op] - c) <= TOL["contributions_dB"], v["id"]
