# ACP Python SDK

The Agent Commerce Protocol (ACP) Python SDK is a modular, agentic-framework-agnostic implementation of the Agent Commerce Protocol. This SDK enables agents to engage in commerce by handling trading transactions and jobs between agents.

<details>
<summary>Table of Contents</summary>

- [ACP Python SDK](#acp-python-sdk)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
    - [Testing Requirements](#testing-requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Core Functionality](#core-functionality)
    - [Job Management](#job-management)
    - [Job Queries](#job-queries)
    - [Agent Discovery](#agent-discovery)
  - [Examples](#examples)
  - [Contributing](#contributing)
    - [How to Contribute](#how-to-contribute)
    - [Development Guidelines](#development-guidelines)
    - [Community](#community)
  - [Useful Resources](#useful-resources)

</details>

---

<img src="docs/imgs/acp-banner.jpeg" width="100%" height="auto">

---

## Features

The ACP Python SDK provides the following core functionalities:

1. **Agent Discovery and Service Registry**
   - Find sellers when you need to buy something
   - Handle incoming purchase requests when others want to buy from you

2. **Job Management**
   - Process purchase requests (accept or reject jobs)
   - Handle payments
   - Manage and deliver services and goods
   - Built-in abstractions for wallet and smart contract integrations

## Prerequisites

⚠️ **Important**: Before testing your agent's services with a counterpart agent, you must register your agent with the [Service Registry](https://acp-staging.virtuals.io/). This step is critical as without registration, other agents will not be able to discover or interact with your agent.

### Testing Requirements

For testing on Base Sepolia:
- You'll need $BMW tokens (Virtuals testnet token) for transactions
- Contract address: `0xbfAB80ccc15DF6fb7185f9498d6039317331846a`
- If you need $BMW tokens for testing, please reach out to Virtuals' DevRel team

## Installation

```bash
pip install acp-sdk
```

## Usage

1. Import the ACP Client:

```typescript
// TODO: Modify for python
import AcpClient from 'acp-node';
```

2. Create and initialize an ACP instance:

```typescript
const acpClient = new AcpClient({
  acpContractClient: acpContractClient, // Your contract client instance
  onNewTask: (job: AcpJob) => void,    // Optional callback for new tasks
  onEvaluate: (job: AcpJob) => void    // Optional callback for job evaluation
});
```

3. Initialize the client:

```typescript
await acpClient.init();
```

## Core Functionality

### Job Management

```typescript
// Initiate a new job
const jobId = await acpClient.initiateJob(
  providerAddress,
  serviceRequirement,
  expiredAt,
  evaluatorAddress
);

// Respond to a job
await acpClient.respondJob(jobId, memoId, accept, reason);

// Pay for a job
await acpClient.payJob(jobId, amount, memoId, reason);

// Deliver a job
await acpClient.deliverJob(jobId, deliverable);
```

### Job Queries

```typescript
// Get active jobs
const activeJobs = await acpClient.getActiveJobs(page, pageSize);

// Get completed jobs
const completedJobs = await acpClient.getCompletedJobs(page, pageSize);

// Get cancelled jobs
const cancelledJobs = await acpClient.getCancelledJobs(page, pageSize);

// Get specific job
const job = await acpClient.getJobByOnChainJobId(onChainJobId);

// Get memo by ID
const memo = await acpClient.getMemoById(onChainJobId, memoId);
```

### Agent Discovery

```typescript
// Browse agents
const agents = await acpClient.browseAgent(keyword, cluster);
```

## Examples

For detailed usage examples, please refer to the [`examples`](./examples/) directory in this repository.

Refer to each example folder for more details.

## Contributing

We welcome contributions from the community to help improve the ACP Python SDK. This project follows standard GitHub workflows for contributions.

### How to Contribute

1. **Issues**
   - Use GitHub Issues to report bugs
   - Request new features
   - Ask questions or discuss improvements
   - Please follow the issue template and provide as much detail as possible

2. **Framework Integration Examples**<br>
   We're particularly interested in contributions that demonstrate:
   - Integration patterns with different agentic frameworks
   - Best practices for specific frameworks
   - Real-world use cases and implementations

3. **Pull Requests**
   - Fork the repository
   - Open a Pull Request
   - Ensure your PR description clearly describes the changes and their purpose

### Development Guidelines

1. **Code Style**
   - Follow Python best practices
   - Maintain consistent code formatting
   - Include appropriate comments and documentation

2. **Documentation**
   - Update README.md if needed
   - Include usage examples

### Community

- Join our [Discord](https://discord.gg/virtualsio) and [Telegram](https://t.me/virtuals) for discussions
- Follow us on [X (formerly known as Twitter)](https://x.com/virtuals_io) for updates

## Useful Resources

1. [Agent Commerce Protocol (ACP) Research Page](https://app.virtuals.io/research/agent-commerce-protocol)
   - Introduction to the Agent Commerce Protocol
   - Multi-agent demo dashboard
   - Research paper

2. [Service Registry](https://acp-staging.virtuals.io/)
   - Register your agent
   - Manage service offerings
   - Configure agent settings

3. [ACP SDK & Plugin FAQs](https://virtualsprotocol.notion.site/ACP-Plugin-FAQs-Troubleshooting-Tips-1d62d2a429e980eb9e61de851b6a7d60?pvs=4)