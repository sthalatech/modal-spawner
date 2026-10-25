# modal-spawner

Parallel AI-powered feature development: spins up an isolated Modal VM per feature, each running an AI coding agent that implements it, tests it, and pushes a PR-ready branch.

> ⚠️ **Autonomous development.** This tool spawns AI agents that write code, run tests, and push to GitHub. Review all changes before merging.

## Install

```bash
pip install modal
modal setup
modal secret create github-pat GITHUB_TOKEN=ghp_your_token

git clone https://github.com/sthalatech/modal-spawner.git
cd modal-spawner
modal deploy scripts/feature_spawner.py
```

Requires a [Modal](https://modal.com) account and a GitHub PAT for pushing to repositories.

## Usage

```bash
curl -X POST https://YOUR_USERNAME--feature-spawner-spawn-feature.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/your/repo.git",
    "feature_name": "add-health-endpoint",
    "feature_description": "Add a health check endpoint at /api/health",
    "base_branch": "main"
  }'

curl -s "https://YOUR_USERNAME--feature-spawner-status.modal.run" | jq .
```

Default model is free (`opencode/big-pickle`, no API key); edit `scripts/feature_spawner.py` to use a different one.

## Contributing

Issues and PRs are welcome. For significant changes, please open an issue first to discuss what you'd like to change.

## Reporting Issues

Found a bug or have a feature request? [Open an issue](../../issues/new) with steps to reproduce (or the use case, for feature requests).

## License

MIT © Sthala
