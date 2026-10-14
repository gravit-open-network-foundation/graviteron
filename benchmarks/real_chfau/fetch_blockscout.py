#!/usr/bin/env python3
"""CHFAU on Ethereum: all token transfers in the 30 days to 2026-10-13 18:00 UTC, from Blockscout.

Blockscout (eth.blockscout.com) is a public, open-source explorer; no account needed. Writes
data/transfers.json and data/SHA256SUMS. Mints come from the zero address, burns go to it.
"""
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TOKEN = "0xbd4dfc058eb95b8de5ceaf39966a1a70f5556f78"
BASE = f"https://eth.blockscout.com/api/v2/tokens/{TOKEN}"
END = datetime(2026, 10, 13, 18, 0, tzinfo=timezone.utc)
START = datetime(2026, 9, 13, 18, 0, tzinfo=timezone.utc)
OUT = Path(__file__).resolve().parent / "data"


def get(url):
    for i in range(8):
        try:
            req = urllib.request.Request(url, headers={"accept": "application/json", "user-agent": "gravit-research"})
            return json.load(urllib.request.urlopen(req, timeout=40))
        except (urllib.error.URLError, TimeoutError):
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"failed: {url}")


def main():
    rows, params, pages = [], None, 0
    while True:
        url = BASE + "/transfers" + ("?" + urllib.parse.urlencode(params) if params else "")
        d = get(url)
        pages += 1
        stop = False
        for x in d["items"]:
            t = datetime.fromisoformat(x["timestamp"].replace("Z", "+00:00"))
            if t >= END:
                continue
            if t < START:
                stop = True
                break
            rows.append({"time": x["timestamp"], "block": x["block_number"], "tx": x["transaction_hash"], "log_index": x["log_index"],
                         "from": x["from"]["hash"].lower(), "to": x["to"]["hash"].lower(),
                         "amount": int(x["total"]["value"]) / 10 ** int(x["total"]["decimals"])})
        if pages % 10 == 0:
            print(f"  {pages} pages, {len(rows)} transfers in window, at {d['items'][-1]['timestamp'] if d['items'] else '-'}", flush=True)
        params = d.get("next_page_params")
        if stop or not params:
            break
        time.sleep(0.4)
    counters = get(BASE + "/counters")
    info = get(BASE)
    OUT.mkdir(parents=True, exist_ok=True)
    body = (json.dumps({"token": TOKEN, "source": "eth.blockscout.com", "window": [START.isoformat(), END.isoformat()],
                        "fetched_total_supply": int(info["total_supply"]) / 10 ** int(info["decimals"]),
                        "fetched_counters": counters, "transfers": sorted(rows, key=lambda r: (r["block"], r["log_index"]))},
                       indent=1, sort_keys=True) + "\n").encode()
    (OUT / "transfers.json").write_bytes(body)
    (OUT / "SHA256SUMS").write_text(f"{hashlib.sha256(body).hexdigest()}  transfers.json\n")
    print(f"done: {len(rows)} transfers in window from {pages} pages", flush=True)


if __name__ == "__main__":
    main()
