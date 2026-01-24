---
name: modal-spawner
description: Spawn isolated Modal VMs for parallel feature development. Each VM runs an AI agent (opencode) that implements features autonomously - codes, tests, commits, and pushes to GitHub. Use when you want parallel/background feature development.
license: MIT
metadata:
  author: sthalatech
  version: "1.0"
  repository: https://github.com/sthalatech/modal-spawner
---

# Modal Spawner

> Parallel AI-powered feature development with isolated Modal VMs

## What is Modal Spawner?

Modal Spawner enables **parallel feature development** by spinning up isolated VMs on Modal for each feature. Each VM runs an AI agent that autonomously implements the feature.

The key insight: **Complete isolation**. Each feature gets its own VM with fresh codebase, no merge conflicts, no shared state.

## When to Use This Skill

Use Modal Spawner when:

- You want to develop features in parallel/background
- You need autonomous feature implementation
- You say "spawn", "develop in background", "parallel development"
- Multiple features need to be worked on simultaneously
- You want PR-ready branches without manual coding

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     SPAWN FEATURE                           │
├─────────────────────────────────────────────────────────────┤
│  1. Spin up isolated Modal VM                               │
│  2. Clone repository                                        │
│  3. Create feature branch                                   │
│  4. AI agent implements feature                             │
│  5. Run tests, verify                                       │
│  6. Commit and push                                         │
│  7. VM auto-terminates                                      │
│                                                             │
│  Result: PR-ready branch on GitHub                          │
└─────────────────────────────────────────────────────────────┘
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `https://kirthiss--feature-spawner-spawn-feature.modal.run` | POST | Spawn new feature |
| `https://kirthiss--feature-spawner-status.modal.run` | GET | Check status |

## Usage

### Spawn a Feature

```bash
curl -X POST https://kirthiss--feature-spawner-spawn-feature.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/kirthiss/amazon-audit-v2.git",
    "feature_name": "<kebab-case-name>",
    "feature_description": "<detailed description of what to implement>",
    "base_branch": "main"
  }'
```

**Parameters:**
- `repo_url` — GitHub repository URL
- `feature_name` — Kebab-case name (becomes branch name)
- `feature_description` — Detailed description for the AI agent
- `base_branch` — Branch to create feature from (default: main)

### Check Status

```bash
# All features
curl -s "https://kirthiss--feature-spawner-status.modal.run" | jq .

# Specific feature
curl -s "https://kirthiss--feature-spawner-status.modal.run?feature_id=<id>" | jq .
```

### Watch Progress

```bash
watch -n 5 'curl -s "https://kirthiss--feature-spawner-status.modal.run" | jq ".[] | select(.feature_name==\"<name>\")"'
```

## Status Values

| Status | Description |
|--------|-------------|
| `initializing` | Setting up VM, cloning repo |
| `developing` | AI agent actively coding |
| `completed` | Done, branch pushed |
| `failed` | Error (check logs) |

## Examples

### Simple Feature

```bash
curl -X POST https://kirthiss--feature-spawner-spawn-feature.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/kirthiss/amazon-audit-v2.git",
    "feature_name": "health-endpoint",
    "feature_description": "Add a health check endpoint at /api/health that returns JSON {status: ok, timestamp: current_time}"
  }'
```

### Complex Feature

```bash
curl -X POST https://kirthiss--feature-spawner-spawn-feature.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/kirthiss/amazon-audit-v2.git",
    "feature_name": "rate-limiting",
    "feature_description": "Add rate limiting middleware: 1) Limit to 100 requests/minute per IP, 2) Use Redis for tracking, 3) Return 429 Too Many Requests when exceeded, 4) Add X-RateLimit-* headers to responses"
  }'
```

### Parallel Features

Spawn multiple simultaneously:

```bash
# Feature 1
curl -X POST https://kirthiss--feature-spawner-spawn-feature.modal.run \
  -d '{"repo_url": "...", "feature_name": "api-logging", "feature_description": "Add structured logging"}'

# Feature 2 (immediately)
curl -X POST https://kirthiss--feature-spawner-spawn-feature.modal.run \
  -d '{"repo_url": "...", "feature_name": "metrics", "feature_description": "Add Prometheus metrics"}'
```

## After Completion

1. **Branch location:** `feature/<feature-name>`
2. **Create PR:** `https://github.com/kirthiss/amazon-audit-v2/pull/new/feature/<feature-name>`
3. **Review changes:** `git diff main..origin/feature/<feature-name>`

## View Live Logs

```bash
# On the server where Modal is deployed
cd ~/modal && source .venv/bin/activate && modal app logs feature-spawner
```

## Writing Good Descriptions

The AI agent uses your description to implement. Be specific!

**❌ Bad:** "Add authentication"

**✅ Good:** "Add JWT authentication: 1) POST /api/auth/login accepts email/password, returns JWT, 2) Tokens expire in 24h, 3) Middleware protects /api/* routes, 4) Return 401 for invalid tokens"

## Configuration

### Model

Default: `opencode/big-pickle` (free)

To change, edit `feature_spawner.py` on the deployment server.

### Timeout

Default: 2 hours per feature.

## Cost

- **Modal:** ~$0.10-0.50 per feature
- **LLM:** Free with default model
- VMs auto-terminate after completion
