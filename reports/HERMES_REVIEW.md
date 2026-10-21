# HERMES_REVIEW — Intercom DEX v0.1.5

**Commit reviewed:** 57859693b4ab9cb6988af89559ef213587361cf6 (`main`)
**Branch:** `hermes/review-2026-10-21`
**Date:** 2026-10-21

## Files reviewed

| File | Purpose |
|------|---------|
| `HERMES_NEXT_STEPS.md` | Safe staged handoff guide |
| `PROJECT_OVERVIEW.md` | Project scope, phases, boundaries, and risks |
| `README.md` | Setup phases and safeguards |
| `TEST_REPORT.md` | 31 checks on Node 24.19.0 and 26.12.0 with synthetic wallets |

## What has been done

### Release and setup helper

- Upstream release is Intercom DEX v0.1.5, pinned to the release archive rather than the development branch.
- Expected archive SHA-256: `63cef1771c8596e095cd7eaa52da2c74bc3670fad54f0d7b20f32b8a1b547b56`.
- The helper verifies the archive hash before extraction and rejects unsafe archive entries.
- The helper has three separate phases: `plan`, `prepare`, and interactive `wallet-setup`.
- `plan` was reported successful. It only displays the plan and does not download, write files, read wallet contents, or start processes.

### Synthetic tests

- 31 checks passed on Node 24.19.0 and 31 passed on Node 26.12.0.
- Tests cover source-wallet immutability, encrypted output permissions, fresh synthetic Solana identities, rejection of overwrites and unsafe archives, and absence of peer/trader/MCP or network-transaction activity.
- A complete `prepare` test also passed in Sandbox on Node 24.
- These are synthetic Sandbox tests, not a full security audit and not a test on the owner's WSL laptop. The test report notes deprecated dependencies and two Git dependencies without integrity metadata.

### Wallet and authority boundary

- `prepare` installs the pinned release and dependencies into a new dedicated directory under Linux `HOME`; it does not read wallet data.
- `wallet-setup` is interactive and uses an encrypted snapshot of the existing RESET keystore. It creates a fresh, unfunded Solana wallet plus an encrypted RESET/Trac copy.
- The RESET/Trac copy has the same address, authority, and funds as its source. This is not fund isolation.
- No proof key, runtime configuration, peer, trader, MCP service, offer, or transaction has been created or started by this setup helper.

## What has not been done

| Item | Status |
|------|--------|
| `prepare` on the owner's WSL | Not reported as run. The owner previously reported Node.js 26.12.0 installed in WSL; confirm `node --version` and `npm --version` in the intended shell before `prepare`. |
| `wallet-setup` | Not run; requires a separate decision and hidden interactive passwords in the owner's terminal. |
| Proof key | Not built. |
| Full peer/trader runtime configuration | Not created. |
| Peer, trader, or MCP | Not started or added to Hermes. Upstream MCP behavior requires review because it may start the trader automatically. |
| Current worker or mining status | Intentionally omitted from this public report. Hermes was used for initial setup; do not infer ongoing worker status from this review. |
| Live registry or market | Not currently verified. Supported pairs in code do not prove they are live or open. |
| Offers, trading, transfers, or transactions | None performed. Any such action needs separate, transaction-specific owner approval. |

## Risks and questions before later phases

1. **Dependency installation:** `prepare` downloads the pinned release and runs `npm ci`. Do not run it with `sudo`; review any failure or partial directory before retrying.
2. **Wallet concurrency and authority:** because the encrypted RESET/Trac copy retains the same authority as its source, confirm the intended timing before `wallet-setup`. Do not interrupt or stop an existing worker automatically.
3. **Wallet secrecy:** passwords belong only in hidden terminal prompts. Do not place secrets, addresses, balances, wallet paths, or worker state in this public repository, issues, or commit messages.
4. **Proof/runtime:** proof key and peer/trader configuration remain separate, unverified future tasks. Follow the tagged v0.1.5 documentation and check each generated file before starting anything.
5. **MCP start behavior:** do not assume MCP is passive or read-only. Review the exact upstream behavior before configuring it in Hermes.
6. **Market availability:** a live registry/order book has not been confirmed. Do not use an old snapshot as evidence of current pair status or price.
7. **Trading:** any offer, take, cancel, withdrawal, transfer, signing, or broadcast requires specific owner approval after the pair, side, amount, price, total, fees, destination/network, and expiry are shown.

## Suggested staged next steps

1. Run `prepare` only when the owner explicitly asks; confirm Node and npm versions in the same WSL shell first.
2. Review its output and any created files. Stop on errors, existing directories, or partial data; do not delete or retry automatically.
3. Treat `wallet-setup` as a separate sensitive step. Run it only after the owner explicitly approves and chooses a time that does not conflict with other wallet use.
4. Review proof-key and runtime configuration separately; do not start peer/trader/MCP by implication.
5. Establish a genuinely read-only market observation path before claiming that a pair is currently active.
6. Require explicit approval for each transaction, with complete terms shown beforehand.

This report intentionally excludes the owner's current worker state, round, balances, wallet addresses, local personal paths, and credentials.