# HERMES_REVIEW — Intercom DEX v0.1.5 (Updated)

**Commit reviewed:** 57859693b4ab9cb6988af89559ef213587361cf6 ()
**Branch:**
**Date:** 2026-10-21
**Previous review commit:** 03335c5

---

## Status Summary (from previous review)

### Completed
- Release pinned: Intercom DEX v0.1.5 (SHA-256: 63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56)
- Helper script phases validated: plan (display only), prepare (download/verify/install), wallet-setup (interactive)
- Synthetic tests: 31 checks pass on Node 24.19.0 & 26.12.0 (Sandbox)
- Boundaries enforced: no wallet access in prepare, no peer/trader/MCP start, no Hermes config changes
- Report committed & pushed: branch hermes/review-2026-10-21 at commit 03335c5 -> 67eeabb

### Not Done (unchanged)
| Item | Blocker |
|------|---------|
| prepare on user WSL | Node/npm available (nvm v26.12.0), not yet run |
| wallet-setup | Requires explicit owner approval + interactive passwords |
| Proof key (lockkey.zkey) | ~300 MB, separate step |
| Runtime configs (peer.json, trader.json) | Needs venue keys from release |
| Peer / trader / MCP | Not started, MCP may auto-start trader |
| Live registry / active pairs | Unverified -- requires running peer |
| Any trading / transactions | Not permitted without per-transaction approval |

---

## Key Risks (unchanged)

1. Wallet concurrency -- Encrypted RESET/Trac copy shares authority with mining wallet. Confirm no active worker before wallet-setup.
2. MCP behavior -- Upstream MCP may auto-start trader. Review before Hermes integration.
3. Dependency freshness -- Deprecated packages + 2 Git deps without integrity. Monitor advisories.
4. Proof key build -- Large download, run separately with owner present.
5. Secrets handling -- Passwords only in hidden terminal prompts. No secrets in repo/issues/commits.

---

## Next Steps (Awaiting Owner Decision)

| Order | Action | Prerequisite |
|-------|--------|--------------|
| 1 | Run prepare on WSL | Confirm Node 26.12.0 + npm in target shell |
| 2 | Review prepare output/files | Stop on errors/partial data; no auto-retry |
| 3 | Approve & run wallet-setup | Owner types passwords interactively; no conflict with mining worker |
| 4 | Build proof key | Owner present, ~300 MB download |
| 5 | Create runtime configs | Use release venue keys; review generated files |
| 6 | Start peer (supervised) | Then trader (supervised) |
| 7 | Review MCP behavior | Before any Hermes integration |
| 8 | Read live registry | Confirm RESET/USDC, TNK/USDC status |
| 9 | Per-transaction approval | Show pair, side, amount, price, total, fees, destination, expiry |

---

## What Changed Since Last Review

- Report updated with current commit state
- Branch synced with remote (67eeabb)
- No code changes, no wallet access, no config changes, no processes started

---

No secrets, wallet addresses, balances, seeds, private keys, passwords, tokens, cookies, or personal info included.
