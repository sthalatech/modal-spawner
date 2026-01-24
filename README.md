# 🚀 Modal Spawner

> Parallel AI-powered feature development with isolated Modal VMs

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

⚠️ **Autonomous Development.** This tool spawns AI agents that write code, run tests, and push to GitHub. Review all changes before merging.

## Quick Start

### Install as Agent Skill

```bash
# Using Vercel's add-skill
npx add-skill sthalatech/modal-spawner

# Using OpenSkills
openskills install sthalatech/modal-spawner
```

### Or Tell Your AI Agent

> "Set up Modal Spawner using https://github.com/sthalatech/modal-spawner"

---

## What is Modal Spawner?

Modal Spawner enables **parallel feature development** by spinning up isolated VMs on [Modal](https://modal.com) for each feature. Each VM runs an AI coding agent (opencode) that:

1. Clones your repository
2. Creates a feature branch
3. Implements the feature autonomously
4. Runs tests and verifies
5. Commits and pushes to GitHub
6. Creates a PR-ready branch

### Key Features

- 🔄 **Parallel Development** — Multiple features developed simultaneously
- 🔒 **Complete Isolation** — Each feature gets its own VM, no conflicts
- 🤖 **Autonomous Coding** — AI agent handles implementation end-to-end
- 📋 **PR-Ready Branches** — Just review and merge
- 💰 **Cost Effective** — VMs auto-terminate, pay only for compute time

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     MODAL SPAWNER                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: "Add rate limiting"                                  │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Modal Cloud                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Feature-A   │  │ Feature-B   │  │ Feature-C   │  │   │
│  │  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │  │   │
│  │  │ │opencode │ │  │ │opencode │ │  │ │opencode │ │  │   │
│  │  │ │  agent  │ │  │ │  agent  │ │  │ │  agent  │ │  │   │
│  │  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │  │   │
│  │  │  Go, Git    │  │  Go, Git    │  │  Go, Git    │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   │
│  └─────────┼────────────────┼────────────────┼─────────┘   │
│            │                │                │             │
│            ▼                ▼                ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              GitHub Repository                       │   │
│  │  ├── feature/rate-limiting                          │   │
│  │  ├── feature/add-auth                               │   │
│  │  └── feature/dashboard-ui                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

1. **Modal Account** — Sign up at [modal.com](https://modal.com)
2. **GitHub PAT** — For pushing to repositories
3. **Server with Modal CLI** — Where the spawner runs

### Setup on Your Server

```bash
# 1. Install Modal
pip install modal
modal setup

# 2. Create secrets
modal secret create github-pat GITHUB_TOKEN=ghp_your_token
modal secret create anthropic-key ANTHROPIC_API_KEY=sk-ant-xxx  # Optional

# 3. Clone and deploy
git clone https://github.com/sthalatech/modal-spawner.git
cd modal-spawner
modal deploy scripts/feature_spawner.py
```

---

## Usage

### Spawn a Feature

```bash
curl -X POST https://YOUR_USERNAME--feature-spawner-spawn-feature.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/your/repo.git",
    "feature_name": "add-health-endpoint",
    "feature_description": "Add a health check endpoint at /api/health that returns {status: ok, timestamp: current_time}",
    "base_branch": "main"
  }'
```

### Check Status

```bash
# All features
curl -s "https://YOUR_USERNAME--feature-spawner-status.modal.run" | jq .

# Specific feature
curl -s "https://YOUR_USERNAME--feature-spawner-status.modal.run?feature_id=feature-xxx" | jq .
```

### Watch Progress

```bash
watch -n 5 'curl -s "https://YOUR_USERNAME--feature-spawner-status.modal.run" | jq .'
```

---

## Writing Good Feature Descriptions

The AI agent uses your description to implement the feature. Be specific!

### ❌ Bad Description
```
"Add authentication"
```

### ✅ Good Description
```
"Add JWT-based authentication:
1. POST /api/auth/login accepts {email, password} and returns JWT token
2. Tokens expire after 24 hours
3. Add middleware to protect /api/* routes (except /api/auth/*)
4. Return 401 Unauthorized for invalid/expired tokens
5. Store refresh tokens in Redis"
```

---

## Status Values

| Status | Description |
|--------|-------------|
| `initializing` | Setting up VM, cloning repository |
| `developing` | AI agent actively coding |
| `completed` | Feature implemented and pushed |
| `failed` | Error occurred (check logs) |

---

## Configuration

### Default Model

Uses `opencode/big-pickle` (free, no API key required).

To use a different model, edit `scripts/feature_spawner.py`:

```python
opencode_config = {
    "model": "anthropic/claude-sonnet-4-5",  # Requires API key
    ...
}
```

### Timeout

Default: 2 hours per feature. Adjust in `feature_spawner.py`:

```python
@app.function(
    timeout=7200,  # seconds
    ...
)
```

---

## Cost

- **Modal Compute:** ~$0.10-0.50 per feature (depends on complexity)
- **LLM:** Free with `opencode/big-pickle`, or your API costs
- VMs auto-terminate after completion

---

## Links

- **GitHub:** https://github.com/sthalatech/modal-spawner
- **Modal:** https://modal.com
- **OpenCode:** https://opencode.ai

---

## License

MIT
