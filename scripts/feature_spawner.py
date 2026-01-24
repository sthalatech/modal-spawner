import modal
import os
import json
import time
from datetime import datetime

app = modal.App("feature-spawner")

# Reuse the dev image from phase 2
dev_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install([
        "git", "curl", "wget", "build-essential", "sqlite3", "vim", "tmux", "jq",
    ])
    .run_commands([
        "curl -LO https://go.dev/dl/go1.23.4.linux-amd64.tar.gz",
        "tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz",
        "rm go1.23.4.linux-amd64.tar.gz",
    ])
    .env({
        "PATH": "/usr/local/go/bin:/root/go/bin:/root/.local/bin:$PATH",
        "GOPATH": "/root/go",
    })
    .run_commands([
        # Download opencode directly from GitHub releases
        "mkdir -p /root/.opencode/bin",
        "curl -sL https://github.com/anomalyco/opencode/releases/latest/download/opencode-linux-x64.tar.gz | tar xz -C /root/.opencode/bin",
        "chmod +x /root/.opencode/bin/opencode",
        "ln -sf /root/.opencode/bin/opencode /usr/local/bin/opencode",
    ])
    .pip_install(["anthropic","fastapi[standard]"])
)

# Dict to store active sandboxes (in production, use Modal Dict or external DB)
feature_status = modal.Dict.from_name("feature-status", create_if_missing=True)


@app.function(
    image=dev_image,
    secrets=[
        modal.Secret.from_name("github-pat"),
        modal.Secret.from_name("anthropic-key"),
    ],
    timeout=7200,  # 2 hours max per feature
    cpu=2.0,
    memory=4096,
)
def run_feature_development(
    repo_url: str,
    feature_name: str,
    feature_description: str,
    base_branch: str = "main",
):
    """
    Spawn isolated development for a feature.
    Clones repo, creates branch, runs opencode agent.
    """
    import subprocess
    import os
    
    feature_id = f"feature-{feature_name}-{int(time.time())}"
    workspace = f"/tmp/{feature_id}"
    
    # Update status
    feature_status[feature_id] = {
        "status": "initializing",
        "feature_name": feature_name,
        "started_at": datetime.utcnow().isoformat(),
        "logs": [],
    }
    
    def log(msg):
        status = feature_status[feature_id]
        status["logs"].append(f"{datetime.utcnow().isoformat()}: {msg}")
        feature_status[feature_id] = status
        print(msg)
    
    try:
        # Setup opencode auth.json with Anthropic API key
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if anthropic_key:
            auth_dir = "/root/.local/share/opencode"
            os.makedirs(auth_dir, exist_ok=True)
            import json as json_module
            auth_data = {
                "anthropic": {
                    "apiKey": anthropic_key
                }
            }
            with open(f"{auth_dir}/auth.json", "w") as auth_file:
                json_module.dump(auth_data, auth_file)
            log("Created opencode auth.json with Anthropic key")
            
            # Also create opencode config
            config_dir = "/root/.config/opencode"
            os.makedirs(config_dir, exist_ok=True)
            opencode_config = {
                "$schema": "https://opencode.ai/config.json",
                "model": "opencode/big-pickle",
                "autoupdate": False
            }
            with open(f"{config_dir}/opencode.json", "w") as config_file:
                json_module.dump(opencode_config, config_file)
            log("Created opencode config with big-pickle (free)")
        
        # Setup git credentials
        token = os.environ.get("GITHUB_TOKEN", "")
        authed_url = repo_url.replace("https://", f"https://{token}@")
        
        # Clone repository
        log(f"Cloning {repo_url}...")
        subprocess.run(["git", "clone", authed_url, workspace], check=True)
        os.chdir(workspace)
        
        # Configure git
        subprocess.run(["git", "config", "user.email", "agent@modal.dev"], check=True)
        subprocess.run(["git", "config", "user.name", "Modal Agent"], check=True)
        
        # Create feature branch
        branch_name = f"feature/{feature_name}"
        log(f"Creating branch {branch_name}...")
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        
        # Update status
        status = feature_status[feature_id]
        status["status"] = "developing"
        status["branch"] = branch_name
        feature_status[feature_id] = status
        
        # Create AGENTS.md with feature instructions
        agents_md = f"""# Feature Development Task

## Feature: {feature_name}

## Description
{feature_description}

## Instructions
1. Understand the existing codebase structure
2. Implement the feature as described
3. Write tests for the new functionality
4. Ensure existing tests pass
5. Commit your changes with clear messages
6. When done, create a summary of changes

## Project Context
- This is a Go project using Fiber web framework
- Database: Neo4j (graph), Redis (cache)
- Follow existing code patterns in internal/

## Completion Criteria
- Code compiles: `go build ./...`
- Tests pass: `go test ./...`
- Changes committed to branch: {branch_name}
"""
        with open(f"{workspace}/FEATURE_TASK.md", "w") as f:
            f.write(agents_md)
        
        # Run opencode agent
        log("Starting opencode agent...")
        
        env = {
            **os.environ,
            "PATH": "/usr/local/go/bin:/root/go/bin:/root/.local/bin:" + os.environ.get("PATH", ""),
            "GOPATH": "/root/go",
            "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
        }
        
        # Run opencode in non-interactive mode with the task
        prompt = f"""Read FEATURE_TASK.md and implement the feature described.
        
Work step by step:
1. First explore the codebase to understand the structure
2. Plan your implementation
3. Implement the changes
4. Test your changes
5. Commit with a descriptive message
6. Push to the remote branch

Start now."""

        result = subprocess.run(
            ["opencode", "run", prompt],
            cwd=workspace,
            env=env,
            capture_output=True,
            text=True,
            timeout=6000,  # 100 min timeout for agent
        )
        
        log(f"Agent stdout: {result.stdout[-2000:]}")  # Last 2000 chars
        if result.stderr:
            log(f"Agent stderr: {result.stderr[-1000:]}")
        
        # Push changes
        log("Pushing changes...")
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=False)
        
        # Get diff summary
        diff_result = subprocess.run(
            ["git", "diff", f"origin/{base_branch}..HEAD", "--stat"],
            capture_output=True,
            text=True,
        )
        
        # Final status
        status = feature_status[feature_id]
        status["status"] = "completed"
        status["completed_at"] = datetime.utcnow().isoformat()
        status["diff_summary"] = diff_result.stdout
        feature_status[feature_id] = status
        
        log("Feature development completed!")
        
        return {
            "feature_id": feature_id,
            "status": "completed",
            "branch": branch_name,
            "diff_summary": diff_result.stdout,
        }
        
    except Exception as e:
        log(f"Error: {str(e)}")
        status = feature_status[feature_id]
        status["status"] = "failed"
        status["error"] = str(e)
        feature_status[feature_id] = status
        raise


@app.function(image=dev_image)
def get_feature_status(feature_id: str):
    """Get status of a feature development task."""
    return feature_status.get(feature_id, {"error": "Feature not found"})


@app.function(image=dev_image)
def list_features():
    """List all feature development tasks."""
    return {k: v for k, v in feature_status.items()}


@app.function(
    image=dev_image,
    secrets=[modal.Secret.from_name("github-pat")],
)
def get_feature_diff(repo_url: str, branch_name: str, base_branch: str = "main"):
    """Get the diff for a feature branch."""
    import subprocess
    import os
    
    token = os.environ.get("GITHUB_TOKEN", "")
    authed_url = repo_url.replace("https://", f"https://{token}@")
    
    workspace = "/tmp/diff-check"
    subprocess.run(["git", "clone", "--depth=50", authed_url, workspace], check=True)
    os.chdir(workspace)
    
    subprocess.run(["git", "fetch", "origin", branch_name], check=True)
    
    result = subprocess.run(
        ["git", "diff", f"origin/{base_branch}..origin/{branch_name}"],
        capture_output=True,
        text=True,
    )
    
    return {
        "branch": branch_name,
        "diff": result.stdout,
    }


# Web endpoint to trigger feature development
@app.function(
    image=dev_image,
    secrets=[
        modal.Secret.from_name("github-pat"),
        modal.Secret.from_name("anthropic-key"),
    ],
)
@modal.fastapi_endpoint(method="POST")
def spawn_feature(item: dict):
    """
    HTTP endpoint to spawn feature development.
    
    POST body:
    {
        "repo_url": "https://github.com/user/repo.git",
        "feature_name": "add-login-page",
        "feature_description": "Add a login page with email/password auth",
        "base_branch": "main"
    }
    """
    # Spawn async - returns immediately
    call = run_feature_development.spawn(
        repo_url=item["repo_url"],
        feature_name=item["feature_name"],
        feature_description=item["feature_description"],
        base_branch=item.get("base_branch", "main"),
    )
    
    return {
        "status": "spawned",
        "call_id": call.object_id,
        "message": "Feature development started. Check status with get_feature_status.",
    }


@app.function(image=dev_image)
@modal.fastapi_endpoint(method="GET")
def status(feature_id: str = ""):
    """HTTP endpoint to check feature status."""
    if feature_id:
        return get_feature_status.remote(feature_id)
    return list_features.remote()


@app.local_entrypoint()
def main(
    feature_name: str = "test-feature",
    description: str = "Add a health check endpoint at /api/health",
):
    """CLI entrypoint for testing."""
    result = run_feature_development.remote(
        repo_url="https://github.com/YOUR_USERNAME/amazon-audit-v2.git",
        feature_name=feature_name,
        feature_description=description,
    )
    print(json.dumps(result, indent=2))
