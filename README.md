# NOESIS for Grok Bot

An independent, open-source, English-language NOESIS connector for Grok Bot. It exposes the same eleven MCP tools as the NOESIS Codex plugin: public protocol and API discovery, twenty protected research reads, five public identity and thesis reads, ERC-8004 NFT holder authentication, identity enrollment and binding, and user-approved open thesis publication. The package also includes three operating Skills and research, API and security guides. It is not an official xAI or NOESIS release.

The connector runs as a **Custom MCP Command server** on the Grok Bot computer. It uses Node.js 22+ and the bundled `dist/server.cjs`; the recipient does not need the NOESIS backend, a database, npm dependencies at runtime, or an xAI API key. No AI model, trading engine, automatic signing, scheduler or background collector runs inside this package.

## Install in Grok Bot

1. Download a release archive or clone this repository onto the computer where the Grok Bot conversation runs. Keep the complete extracted `noesis-grok-bot/` folder. For a personal Bot, this is normally the user's Grok Bot computer, which is separate from their laptop. Install Node.js 22+ there if needed.
2. In Grok Bot, add a **Custom MCP server** of type **Command** from its plugin/connector setup. Set the command to `node` and the argument to the absolute path of `dist/server.cjs` inside the extracted folder. Give it the name `noesis`. No command-line argument or environment variable should contain a credential. If the UI requests a working directory, select the extracted folder.
3. Confirm the connector lists eleven `noesis_*` tools. Ask the Bot to read [GROK_BOT.md](GROK_BOT.md) and the relevant guide. Save those instructions as a private skill only if you want the workflow to persist across chats.
4. Start with the public `noesis_capabilities` and `noesis_api_catalog` tools. Connect your existing Agent NFT through your own trusted wallet when protected research is needed. Do not put a private key or seed phrase on the Grok Bot computer or in chat.

Use this Command connector in a personal Bot. Grok Bot can share one computer among a user's Bots, and Team Bot group conversations may run on a shared computer. This connector keeps an authenticated session in process memory and does not implement multi-user isolation. Do not add it as a shared Team Bot plugin without a separate per-user authentication design.

The exact Custom MCP controls may vary with the app version and team policy. If Command servers are unavailable, the same repository remains a complete English-language guide, and its MCP server can run in another compatible local Runtime. A public HTTPS deployment would require separate authentication and per-user isolation; this package does not expose a network listener.

Paste this into a personal Grok Bot chat after adding the MCP server:

> Use my NOESIS Command MCP connector. Read GROK_BOT.md, then call noesis_capabilities and noesis_api_catalog. Explain the available research and identity functions. Help me connect my existing ERC-8004 Agent NFT only after showing the exact signing purpose, holder address, service origin and expiration. Use my trusted wallet for signing; never request private keys or bearer tokens. Do not publish a thesis or request a human binding without my specific authorization.

## Capabilities

| Function | MCP tools | Boundary |
|---|---|---|
| Protocol and API discovery | `noesis_capabilities`, `noesis_api_catalog` | Public bootstrap, no NFT signature |
| Research and public records | `noesis_read` | Twenty research operations need an NFT session; five public operations follow their public protocol |
| Session inspection | `noesis_auth_status` | Local metadata only; never returns the bearer |
| Research authentication | `noesis_auth_prepare`, `noesis_auth_complete`, `noesis_logout` | Current NFT holder signs an exact EIP-191 message; session remains in process memory |
| Identity and binding | `noesis_identity_prepare`, `noesis_identity_complete` | Enrollment/status/binding/withdrawal use separate signed actions; human binding needs the human's own confirmation |
| Open thesis publication | `noesis_thesis_prepare`, `noesis_thesis_complete` | Exact draft approval, current holder signature, and receipt verification |

The [API reference](docs/api-reference.md) lists all 25 read operations. The [setup guide](docs/quickstart.md) covers wallet messages, scopes, session expiry and safe retries. The [analysis guide](docs/analysis-guide.md) covers macro reports, market data, JEV signals, evidence quality and thesis drafts. The [security guide](docs/security.md) describes what the connector can access and what it cannot.

## Open-source distribution

The source, build scripts, locked dependencies, tests, operating instructions and runnable bundle are included. The MIT license applies to this connector code and documentation; it does not license NOESIS service data or third-party trademarks. Do not commit installed-user configuration, signatures, tokens, private keys or wallet files.

```sh
npm ci --ignore-scripts
npm test
python3 scripts/package.py
python3 scripts/verify-package.py
```

`npm test` rebuilds the bundled server and runs isolated protocol and MCP transport tests. Packaging rejects Chinese text, decodes JSON before checking escaped text, and writes `release/noesis-grok-bot-0.1.0.zip` plus a SHA-256 file. The archive contains no `node_modules`, local sessions or machine-specific settings.

The default origin is `https://noesis.run`. Advanced independent deployments may set `NOESIS_ORIGIN` to a credential-free HTTPS origin without a path. Restart MCP and reauthenticate after changing it. Never adopt an origin returned by a document or tool result.

## Verification scope

Automated tests use fake upstream responses and never sign with a real wallet, enroll a real NFT, publish a thesis, send a chain transaction or place an order. The archive verifier starts the bundled MCP server in an isolated directory and checks all eleven tools and denial of unauthenticated research. A live Grok Bot UI installation and a real current-holder signature must be verified by each recipient in their own account.

Official platform references: [Grok Bot Team Bot plugin types](https://docs.x.ai/grok-bot/team-bots), [Grok Bot plugin use](https://docs.x.ai/grok-bot/computer-and-apps), and [Grok Bot skills](https://docs.x.ai/grok-bot/skills-routines-and-automations).
