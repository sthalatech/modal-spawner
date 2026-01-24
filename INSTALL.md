# Installing Modal Spawner

## The Easy Way (Recommended)

Tell your AI agent:

> "Set up Modal Spawner in this project using https://github.com/sthalatech/modal-spawner"

---

## Manual Installation

### Prerequisites

1. **Modal Account** - Sign up at [modal.com](https://modal.com)
2. **Python 3.11+** with pip
3. **GitHub Personal Access Token** - For pushing to repositories

### Step 1: Install Modal CLI

```bash
pip install modal
modal setup  # Opens browser for authentication
```

### Step 2: Create Modal Secrets

```bash
# GitHub token (required) - needs repo push permissions
modal secret create github-pat GITHUB_TOKEN=ghp_your_token_here

# Anthropic API key (optional) - only if using paid models
modal secret create anthropic-key ANTHROPIC_API_KEY=sk-ant-your_key_here
```

### Step 3: Clone and Deploy

```bash
# Clone the repository
git clone https://github.com/sthalatech/modal-spawner.git
cd modal-spawner

# Deploy to Modal
modal deploy scripts/feature_spawner.py
```

### Step 4: Note Your Endpoints

After deployment, you'll see URLs like:
```
✓ Created web function spawn_feature => 
    https://YOUR_USERNAME--feature-spawner-spawn-feature.modal.run
✓ Created web function status => 
    https://YOUR_USERNAME--feature-spawner-status.modal.run
```

Save these - you'll use them to spawn features.

---

## Testing the Installation

### 1. Spawn a Test Feature

```bash
curl -X POST https://YOUR_USERNAME--feature-spawner-spawn-feature.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/YOUR_USER/YOUR_REPO.git",
    "feature_name": "test-feature",
    "feature_description": "Add a test file at test.txt with content Hello World"
  }'
```

### 2. Check Status

```bash
curl -s "https://YOUR_USERNAME--feature-spawner-status.modal.run" | jq .
```

### 3. Verify on GitHub

Check for branch `feature/test-feature` in your repository.

---

## Installing as a Skill

### For OpenCode

```bash
# Global installation
mkdir -p ~/.config/opencode/skills/modal-spawner
curl -o ~/.config/opencode/skills/modal-spawner/SKILL.md \
  https://raw.githubusercontent.com/sthalatech/modal-spawner/main/skills/modal-spawner/SKILL.md
```

### For Claude/Cursor

```bash
# In your project
mkdir -p .claude/skills/modal-spawner
curl -o .claude/skills/modal-spawner/SKILL.md \
  https://raw.githubusercontent.com/sthalatech/modal-spawner/main/skills/modal-spawner/SKILL.md
```

### Using add-skill

```bash
npx add-skill sthalatech/modal-spawner
```

---

## Customization

### Change the Model

Edit `scripts/feature_spawner.py`:

```python
opencode_config = {
    "model": "anthropic/claude-sonnet-4-5",  # Change this
    ...
}
```

Then redeploy:
```bash
modal deploy scripts/feature_spawner.py
```

### Adjust Timeout

```python
@app.function(
    timeout=14400,  # 4 hours instead of 2
    ...
)
```

---

## Troubleshooting

### "Secret not found" error

```bash
# List your secrets
modal secret list

# Create missing secret
modal secret create github-pat GITHUB_TOKEN=ghp_xxx
```

### "Permission denied" on git push

Your GitHub token needs `repo` scope. Create a new token at:
https://github.com/settings/tokens

### Feature stuck in "developing"

Check Modal logs:
```bash
modal app logs feature-spawner
```

### Model not found

The default `opencode/big-pickle` is free. If using a different model,
ensure you have the appropriate API key configured.
