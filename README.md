# AttackGen (YudaiV4 Base Mini-App)

Base mini-app UI for YudaiV4: an AI agent that teaches, audits, and safely
simulates smart contract vulnerabilities using a unified Foundry pipeline.

## Quickstart

```bash
cp .env.example .env.local
npm install
npm run dev
```

Update `.env.local` with your OnchainKit API key and public app URL.

## Key routes
- `/.well-known/farcaster.json` - Farcaster manifest (update with signed data)
- `/api/health` - health check
- `/api/tasks` - task orchestration stub (POST)

## Notes
- The UI calls `sdk.actions.ready()` to hide the Base mini-app splash screen.
- Farcaster identity uses `useAuthenticate()`, wallet flows use
  `<ConnectWallet>`.
- `useMiniKit()` context is treated as untrusted metadata in the UI.

## Docs
- `docs/ARCHITECTURE.md`
