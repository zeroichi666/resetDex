# HERMES_REVIEW — Intercom DEX v0.1.5

**Commit reviewed:** 57859693b4ab9cb6988af89559ef213587361cf6 (main)
**Branch:** hermes/review-2026-10-21
**Date:** 2026-10-21

---

## Files Reviewed

| File | Purpose |
|------|---------|
| HERMES_NEXT_STEPS.md | Handoff guide with safe workflow steps |
| PROJECT_OVERVIEW.md | Project scope, phases, boundaries, risks |
| README.md | Usage instructions, phases, constraints |
| TEST_REPORT.md | 31 checks on Node 24.19.0 & 26.12.0 (synthetic wallets) |

---

## Summary of What Has Been Done

### Release Pinning & Verification
- Upstream release: Intercom DEX v0.1.5 (tagged, not main)
- Archive SHA-256: 63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56
- Venue keys in script match release metadata
- Archive verified against official release page

### Script Phases (setup_intercom_dex.py)
| Phase | Status | What It Does |
|-------|--------|--------------|
| plan | Reported done | Shows plan only; no download, write, wallet read, or process start |
| prepare | Not yet run on user machine | Downloads archive, verifies hash, extracts safely, runs npm ci on release + peer; creates DEX root folder under Linux HOME; no wallet/keystore access |
| wallet-setup | Not run | Interactive only; prompts for DEX password (12+ chars) and RESET keystore password; uses encrypted snapshot of ~/.reset-signer/keystore.json; runs official CLI setup --import-reset-keystore; produces new Solana wallet + encrypted RESET/Trac copy |

### Test Coverage (Sandbox, Synthetic Wallets)
- 31 checks pass on Node 24.19.0 and 26.12.0
- Verified: source immutability, Solana keys differ per setup, overwrite rejection, encrypted output modes (0600/0700), no plaintext secrets in output, no peer/trader/MCP/network calls
- prepare full install also succeeded in Sandbox (Node 24)
- Limitations: Sandbox only, not user WSL; npm warnings on deprecated deps & skipped integrity for 2 Git deps; not a full security audit

### Separation Boundaries
- DEX root: ~/.local/share/intercom-dex-v0.1.5/ (separate from ~/src/resetmnr and ~/.reset-signer)
- RESET keystore imported via encrypted snapshot — source unchanged
- Critical: Imported RESET/Trac copy has same address, authority, funds as source — not fund isolation
- New Solana identity is created fresh (unfunded)

### Constraints Enforced by Script
- Rejects overlapping paths, symlinks, wrong permissions, existing data
- No sudo, no plaintext secrets, no auto-retry on failure
- No peer/trader/MCP started, no trading commands exposed
- No Hermes config changes

---

## What Has NOT Been Done

| Item | Blocker / Status |
|------|------------------|
| prepare on user WSL | Not run (Node.js was missing; nvm v26.12.0 available) |
| wallet-setup | Requires explicit owner approval; interactive terminal only |
| Proof key (lockkey.zkey) | Not built (~300 MB, requires node bin/proof-setup.mjs) |
| Runtime config (peer.json, trader.json) | Not created; needs venue keys from release |
| Bridge/control tokens | Not generated (openssl rand -hex 32) |
| Peer process | Not started (requires supervised runtime) |
| Trader process | Not started |
| MCP server (src/mcp/server.mjs) | Not configured; upstream warns it may auto-start trader |
| Hermes MCP integration | Not added to Hermes config.yaml |
| Live registry / market read | Cannot — requires running peer to join intercom-dex channel |
| Active pair verification (RESET/USDC, TNK/USDC) | Unknown — code supports, live status unreadable without peer |
| Any trading / offer / transfer | Not permitted without explicit per-transaction approval |

---

## Questions / Risks for Next Review

1. Node.js on WSL — nvm v26.12.0 exists; confirm prepare runs cleanly on user machine (npm lifecycle scripts may differ from Sandbox).

2. RESET keystore permissions — Script requires ~/.reset-signer dir 0700, keystore.json 0600. Verify before wallet-setup.

3. Active RESET mining claim (round 403) — HERMES_NEXT_STEPS.md warns: Pastikan tidak ada worker lain yang aktif memakai wallet itu sebelum langkah ini dilakukan. Confirm mining worker stopped before DEX wallet-setup.

4. Proof key build — ~300 MB download, takes minutes. Run separately with owner present.

5. Runtime config generation — Need to create peer.json and trader.json with venue keys from release. Template in docs/OPERATORS.md / docs/NETWORKS.md.

6. MCP auto-start risk — Upstream docs: src/mcp/server.mjs may start trader if not running. Do not add MCP to Hermes until behavior reviewed and approved.

7. Live pair status — Cannot confirm RESET/USDC or TNK/USDC are open without peer. Plan read-only registry check after peer runs (if safe path exists).

8. Payout lock — Recommended for withdrawals to owner address only. Configure in trader.json before trading.

9. Backup strategy — After wallet-setup, encrypted data folder + DEX password must be backed up offline separately.

10. Dependency freshness — npm warnings: deprecated packages, 2 Git deps with skipped integrity (pinned by release commit). Monitor for security advisories.

---

## Next Steps (Awaiting Owner Decision)

1. Run prepare on WSL (if Node/npm environment confirmed)
2. Approve wallet-setup (interactive, owner types passwords)
3. Build proof key
4. Create runtime configs
5. Generate tokens
6. Start peer (supervised), then trader (supervised)
7. Review MCP behavior before Hermes integration
8. Read live registry → confirm active pairs
9. Per-transaction approval for any trading

---

No secrets, wallet addresses, balances, seeds, private keys, passwords, tokens, cookies, or personal info included in this report.
