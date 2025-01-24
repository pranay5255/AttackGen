# AttackGen: AI-Powered Smart Contract Vulnerability Analyzer

<div align="center">
  <img height="320" src="./public/AI-Agent-Contract.jpg" />
  <br />
  <img height="32" src="public/powered-by-openai-badge-filled-on-light.svg" />
</div>

## Overview

AttackGen is a decentralized AI agent that analyzes smart contracts for potential vulnerabilities and generates exploit contracts. It leverages OpenAI's GPT models and runs on Phala Network's decentralized TEE infrastructure.

### Key Features

- Smart contract vulnerability analysis
- Automated exploit contract generation
- Secure API key management through TEE
- Integration with Etherscan API for contract verification
- Decentralized hosting on Phala Network

### Architecture

<div align="center">
  <img height="320" src="./public/ai-agent-architecture.jpg" />
</div>

## Getting Started

### Prerequisites
- Node.js
- npm
- OpenAI API key
- Etherscan API key

### Installation

```bash
npm install
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your API keys to the secrets configuration:
```json
{
  "openaiApiKey": "YOUR_OPENAI_API_KEY",
  "etherscanApiKey": "YOUR_ETHERSCAN_API_KEY"
}
```

### Build and Test

```bash
npm run build
npm run test
```

### Deployment

1. Publish your agent:
```bash
npm run publish-agent
```

2. Set your secrets:
```bash
npm run set-secrets
```

3. Access your agent at the provided URL:
```
https://wapo-testnet.phala.network/ipfs/<your-cid>?key=<your-key>
```

## Project Structure

- `/scripts` - Build and deployment utilities
- `/src` - Core application code
- `/public` - Static assets

## Security

This project runs on Phala Network's TEE (Trusted Execution Environment) infrastructure, ensuring:
- Secure execution in hardware-encrypted environments
- Protected API keys and sensitive data
- Verifiable code execution

## License

[Add your license information here]
