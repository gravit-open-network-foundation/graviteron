# CHFAU on chain: what the public ledger shows

AllUnity reports strong CHFAU volumes. This study checks what can be checked from public data only,
for the 30 days to 13 October 2026 on Ethereum.

* `fetch_blockscout.py` downloaded every CHFAU transfer of the window from the public Blockscout
  explorer (snapshot in `data/`, with `SHA256SUMS`); `analyse.py` is deterministic.
* The supply reported by Blockscout (38,963,792.92 CHFAU) equals the supply read directly from the
  token contract with `totalSupply()` through a public RPC node: two independent sources agree.

How to read the numbers:

* **Issuance is real and large;** mints and burns in the window are of the order of 13 million CHFAU
  each, so the supply stayed near 39 million.
* **Transfer volume is not the same as economic activity.** About 60 % of the volume runs through two
  unlabelled wallets, and large amounts move several times on the same day before a burn. We do not
  know who holds these wallets and do not guess.
* Ethereum only; Base, Solana and other chains hold small amounts (read on 13 Oct 2026). Off-chain
  activity (mint and redemption requests at AllUnity) is not visible here.
