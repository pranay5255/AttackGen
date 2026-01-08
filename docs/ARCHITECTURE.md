# YudaiV4 Architecture (Base Mini-App)

## Purpose
YudaiV4 unifies learning, auditing, and safe exploit simulation for smart
contracts. The Base mini-app surface runs the same task pipeline as CLI and
GitHub bots, with a UI tailored for education and quick audit runs.

## Product Surfaces
- Base mini-app UI (this repo)
- CLI and mini-swe-agent runner
- GitHub PR bot and CI workflow

## Task Primitives
1. Discover context
2. Generate or modify contracts/tests/scripts
3. Compile and test (Forge)
4. Analyze (Slither, Aderyn, Mythril, Echidna)
5. Simulate and validate (Anvil fork + Cast traces)
6. Explain and teach
7. Report and recommend
8. Share and distribute

## Unified Pipeline
All flows map to the same pipeline; the entry point changes, but tooling and
safety boundaries remain consistent.

## Base Mini-App Integration
- Uses `@coinbase/onchainkit` for wallet and Farcaster identity.
- Calls `sdk.actions.ready()` on load to hide the splash screen.
- Serves `/.well-known/farcaster.json` for Farcaster manifest support.
- Uses `<ConnectWallet>` and `useAuthenticate()` for in-app auth.
- Treats `useMiniKit()` context as untrusted metadata.

## Safety Boundaries
- All exploits run only on Anvil forks or local testnets.
- No mainnet signing or production keys in this flow.
- Command execution is confirm-mode gated in the agent backend.

## Current Stubs
- `app/api/tasks/route.ts` is a placeholder. It should enqueue and stream
  actual agent runs.
- `public/.well-known/farcaster.json` must be updated with signed
  accountAssociation data and live URLs.
