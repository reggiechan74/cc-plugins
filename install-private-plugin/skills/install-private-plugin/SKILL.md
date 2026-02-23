---
name: install-private-plugin
description: "Configure git auth for installing Claude Code plugins from private GitHub repos. Use when /plugin marketplace add fails with 403 or HTTPS auth errors."
argument-hint: "<github-repo-url>"
---

# Install Private Plugin

Configure git authentication so that `/plugin marketplace add` can access
private GitHub repositories from within a Codespace.

## Why This Is Needed

Claude Code's `/plugin marketplace add` uses an internal git library that does
not read Codespace credential helpers. The auto-provisioned credential helper
(`/.codespaces/bin/gitcredential_github.sh`) is scoped to only the repo the
Codespace was created from. To clone a **different** private repo, git needs a
credential helper that can authenticate to it.

## Parse Arguments

Extract from `$ARGUMENTS`:
- **Arg 1 (required):** GitHub repository URL or shorthand
  - Full URL: `https://github.com/owner/repo`
  - Shorthand: `github.com/owner/repo` or `owner/repo`

Normalize all formats to extract `OWNER/REPO`.

If no arguments provided, show the **Troubleshooting** section and stop.

---

## Workflow

### Step 1: Check gh CLI authentication

```bash
gh auth status 2>&1
```

If `gh` is not authenticated at all, jump to **Manual Setup** below.

### Step 2: Test repo access via gh CLI

```bash
gh api repos/OWNER/REPO --jq '.full_name' 2>&1
```

**If successful:** The current `gh` auth token can access the repo. Proceed to
Step 3.

**If failed (404 or 403):** The token doesn't have access to this repo. Output:

```
Error: Your current gh auth token cannot access OWNER/REPO.

Your gh CLI is authenticated but the token doesn't have permissions for this
repository. To fix this:

1. Go to: github.com > Settings > Developer settings > Personal access tokens
2. Edit the token shown in `gh auth status`
3. Under "Repository access", add OWNER/REPO
4. Ensure "Contents: Read-only" and "Metadata: Read-only" are set
5. Save, then re-run: /install-private-plugin OWNER/REPO
```

Stop here if access check fails.

### Step 3: Configure gh as git credential helper

```bash
gh auth setup-git 2>&1
```

This registers the `gh` CLI as a git credential helper in `~/.gitconfig`. When
any git client (including Claude Code's internal library) needs credentials for
a GitHub repo, it asks `gh`, which provides the authenticated token.

### Step 4: Verify git access

```bash
git ls-remote https://github.com/OWNER/REPO 2>&1 | head -3
```

**If successful:** Proceed to Step 5.

**If failed:** The credential helper didn't take effect. Try the fallback:

```bash
# Check if a classic PAT is in use (starts with ghp_)
TOKEN=$(gh auth token 2>/dev/null)
if [[ "$TOKEN" == ghp_* ]]; then
    # Classic PATs work with x-access-token URL rewrite
    git config --global url."https://x-access-token:${TOKEN}@github.com/OWNER/REPO".insteadOf "https://github.com/OWNER/REPO"
    git ls-remote https://github.com/OWNER/REPO 2>&1 | head -3
fi
```

If still failing, show Troubleshooting section and stop.

### Step 5: Confirm and instruct

Output:

```
Git authentication configured for OWNER/REPO.

Now run:
  /plugin marketplace add https://github.com/OWNER/REPO

Note: After a Codespace rebuild, re-run these commands:
  gh auth setup-git
  /plugin marketplace add https://github.com/OWNER/REPO
```

---

## Manual Setup

If `gh` CLI is not authenticated, walk the user through setup:

### Option A: Use an existing Codespace secret (recommended)

If `GH_TOKEN` or another env var already contains a PAT:

```bash
# Check for existing PAT env vars
env | grep -E '^(GH_TOKEN|GITHUB_PAT|REGGIE_PAT)=' | sed 's/=.*/=***/'
```

If a PAT is found:

```bash
echo "$PAT_VALUE" | gh auth login --with-token 2>&1
gh auth setup-git 2>&1
```

Then return to **Step 2** to verify access.

### Option B: Create a new PAT

1. Go to **github.com** > **Settings** > **Developer settings** >
   **Personal access tokens** > **Fine-grained tokens**
2. Click **"Generate new token"**
3. Configure:
   - **Token name:** `codespace-private-plugins`
   - **Expiration:** 90 days (or longer)
   - **Repository access:** Select the private repo(s) you need
   - **Permissions:** Contents (Read-only), Metadata (Read-only)
4. Click **"Generate token"** and copy it
5. Store as a Codespace secret:
   - **github.com** > **Settings** > **Codespaces** > **Secrets** > **New secret**
   - Name it (e.g., `PLUGIN_PAT`) and paste the token
   - Grant access to your Codespace's repo
6. Rebuild the Codespace to inject the secret
7. Re-run this command

---

## Troubleshooting

### "Write access to repository not granted" (403)

The token doesn't have permissions for this repo. Edit the token in GitHub
Settings > Developer settings > Personal access tokens and add the repo.

### "Invalid username or token"

Fine-grained PATs (`github_pat_...`) do **not** work with the
`x-access-token:TOKEN@github.com` URL rewrite format. Use `gh auth setup-git`
instead, which handles all PAT types correctly.

### Plugin install still fails after git auth works

Claude Code's plugin system may cache auth failures. Try:
1. Delete any leftover marketplace directories:
   `rm -rf ~/.claude/plugins/marketplaces/temp_*`
2. Re-run `/plugin marketplace add https://github.com/OWNER/REPO`

### Auth doesn't persist after Codespace rebuild

`~/.gitconfig` is ephemeral in Codespaces. Add to `.devcontainer/postCreateCommand`:
```json
"postCreateCommand": "gh auth setup-git"
```

## Notes

- `gh auth setup-git` registers gh as a credential helper for **all** GitHub
  repos the token can access — not just one specific repo.
- This is safe in Codespaces (single-user, ephemeral environment).
- For non-GitHub repos (GitLab, Bitbucket), the URL rewrite approach with a
  classic PAT is still the recommended method.
