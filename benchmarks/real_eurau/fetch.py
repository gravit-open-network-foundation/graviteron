#!/usr/bin/env python3
"""Fetch 30 days of real data for the EURAU venue study (run once; the snapshot is committed).

Sources, all public and free, no account:
  * GeckoTerminal: hourly OHLCV (USD) of every EURAU pool on Ethereum, Base and Solana;
    hours without a trade are absent, which is itself information (a stale venue).
  * Chainlink EUR/USD price feed on Ethereum (0xb49f677943BC038e9857d61E7d053CaA2C1734C1),
    every round of the window, read from the chain with eth_call.
  * European Central Bank reference rates (EUR/USD, daily), via api.frankfurter.dev.

Writes data/*.json and data/SHA256SUMS. The analysis (analyse.py) reads only this snapshot.
"""

import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
END = datetime(2026, 10, 13, 18, 0, tzinfo=timezone.utc)
START = END - timedelta(days=30)
POOLS = [  # (network, pool address, label)
    ("eth", "0x4286b14c3d142d1bbf75c2880037745c28ad0390", "uniswap-eth-EURAU/USDC"),
    ("eth", "0x5b1c2cbf578be98f6e627f000c745f1ee4802733", "uniswap-eth-EURAU/USDT"),
    ("base", None, "base"),  # resolved below
    ("solana", "HvCm8bKZPFKyZ5cRtbWZN7KLzvWANRgHnSgsMSjBhW4", "raydium-sol-EURAU/USDT"),
    ("solana", "Gzr9pqtuAx8KZSS8YrsrRnS7qiugWt1JiX7zJ35tVX9Z", "raydium-sol-EURAU/USDC"),
]
EURAU = {"eth": "0x4933a85b5b5466fbaf179f72d3de273c287ec2c2", "base": "0x4933a85b5b5466fbaf179f72d3de273c287ec2c2"}
FEED = "0xb49f677943BC038e9857d61E7d053CaA2C1734C1"
RPC = "https://ethereum-rpc.publicnode.com"


def get(url, tries=8):
    req = urllib.request.Request(url, headers={"accept": "application/json", "user-agent": "gravit-research"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1:
                raise
            time.sleep(20 * (i + 1))  # public API rate limit: wait and retry


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"content-type": "application/json", "user-agent": "gravit-research"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["result"]


def pools():
    out = []
    for net, addr, label in POOLS:
        if net == "base":
            for p in get(f"https://api.geckoterminal.com/api/v2/networks/base/tokens/{EURAU['base']}/pools?page=1")["data"]:
                a = p["attributes"]
                out.append(("base", a["address"], "base-" + a["name"].replace(" ", "")))
            time.sleep(4)
        else:
            out.append((net, addr, label))
    return out


def ohlcv(net, addr):
    rows, before = [], int(END.timestamp())
    while before > START.timestamp():
        d = get(f"https://api.geckoterminal.com/api/v2/networks/{net}/pools/{addr}/ohlcv/hour"
                f"?aggregate=1&limit=1000&currency=usd&before_timestamp={before}")
        lst = d["data"]["attributes"]["ohlcv_list"]
        time.sleep(4)
        if not lst:
            break
        rows += [r for r in lst if START.timestamp() <= r[0] < END.timestamp()]
        before = min(r[0] for r in lst)
        if len(lst) < 1000:
            break
    return sorted({r[0]: r for r in rows}.values())


def chainlink():
    def round_data(rid):
        h = rpc("eth_call", [{"to": FEED, "data": "0x9a6fc8f5" + f"{rid:064x}"}, "latest"])[2:]
        v = [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]
        return {"round_id": rid, "answer": v[1] / 1e8, "updated_at": v[3]}
    h = rpc("eth_call", [{"to": FEED, "data": "0xfeaf968c"}, "latest"])[2:]
    rid = int(h[:64], 16)
    rounds = []
    while True:
        r = round_data(rid)
        if r["updated_at"] == 0:
            break
        rounds.append(r)
        if r["updated_at"] < START.timestamp() - 2 * 86400:
            break
        rid -= 1
    return sorted(rounds, key=lambda r: r["updated_at"])


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    meta = {"start": START.isoformat(), "end": END.isoformat(), "fetched_at": datetime.now(timezone.utc).isoformat()}
    venues = {}
    for net, addr, label in pools():
        venues[label] = {"network": net, "pool": addr, "ohlcv_hour_usd": ohlcv(net, addr)}
        print(label, len(venues[label]["ohlcv_hour_usd"]), "hours with trades")
    files = {
        "venues.json": venues,
        "chainlink_eur_usd.json": {"feed": FEED, "rounds": chainlink()},
        "ecb_eur_usd.json": get(f"https://api.frankfurter.dev/v1/{(START - timedelta(days=5)).date()}..{END.date()}?from=EUR&to=USD"),
        "meta.json": meta,
    }
    print("chainlink rounds", len(files["chainlink_eur_usd.json"]["rounds"]), "ecb days", len(files["ecb_eur_usd.json"].get("rates", {})))
    sums = []
    for name, obj in files.items():
        b = (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode()
        (DATA / name).write_bytes(b)
        sums.append(f"{hashlib.sha256(b).hexdigest()}  {name}")
    (DATA / "SHA256SUMS").write_text("\n".join(sums) + "\n")


if __name__ == "__main__":
    main()
