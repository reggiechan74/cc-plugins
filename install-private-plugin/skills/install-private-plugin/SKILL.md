---
name: install-private-plugin
description: "Configure git auth for installing Claude Code plugins from private GitHub repos. Use when /plugin marketplace add fails with 403 or HTTPS auth errors."
argument-hint: "<github-repo-url> <env-var-name>"
---

# Install Private Plugin

Configure git URL rewriting so that `/plugin marketplace add` can authenticate
to private GitHub repositories using a PAT stored as a Codespace secret.

## Why This Is Needed

Claude Code's `/plugin marketplace add` uses an internal git library that does
not read Codespace credential helpers. The auto-provisioned `GITHUB_TOKEN` in
Codespaces is scoped to only the repo the Codespace was created from. To access
a **different** private repo, you need a Personal Access Token (PAT) and a git
URL rewrite rule that injects it into HTTPS requests.

## Parse Arguments

Extract from `$ARGUMENTS`:
- **Arg 1:** GitHub repository URL (e.g., `https://github.com/org/repo`)
- **Arg 2:** Environment variable name holding the PAT (e.g., `MY_PAT_SECRET`)

If no arguments provided, show the **Prerequisites** section below as a
step-by-step guide and stop.

## Prerequisites: Creating a PAT and Codespace Secret

If the user has not yet set up a PAT, walk them through every step:

### Part A: Create a Fine-Grained Personal Access Token

1. Open your browser and go to: **github.com**
2. Click your **profile picture** (top-right) > **Settings**
3. In the left sidebar, scroll to the bottom and click **Developer settings**
4. Click **Personal access tokens** > **Fine-grained tokens**
5. Click the green **"Generate new token"** button
6. Fill in the form:
   - **Token name:** Give it a memorable name (e.g., `codespace-private-plugins`)
   - **Expiration:** Choose 90 days (or longer if you prefer)
   - **Resource owner:** Select your personal account (or your organization)
   - **Repository access:** Click **"Only select repositories"**, then use the
     dropdown to check the private repo you want to install as a plugin
   - **Permissions:** Expand **"Repository permissions"** and set:
     - **Contents:** Read-only
     - **Metadata:** Read-only
     - Leave everything else as "No access"
7. Click **"Generate token"** at the bottom
8. **Copy the token immediately** — you will not be able to see it again.
   It starts with `github_pat_...`

### Part B: Store the Token as a Codespace Secret

1. Go to: **github.com** > **Settings** (same profile menu as above)
2. In the left sidebar, click **Codespaces** (under "Code, planning, and automation")
3. Under **"Secrets"**, click **"New secret"**
4. Fill in:
   - **Name:** A descriptive name using UPPER_SNAKE_CASE (e.g., `MY_PRIVATE_REPO`)
     — this becomes the environment variable name you will pass as Arg 2
   - **Value:** Paste the `github_pat_...` token you copied
5. Under **"Repository access"**, click **"Selected repositories"** and add the
   repo your Codespace runs in (e.g., `myorg/my-main-project`). This grants the
   Codespace permission to see the secret.
6. Click **"Add secret"**

### Part C: Rebuild the Codespace

Codespace secrets are only injected when the container starts. You must rebuild:

1. In VS Code / Codespace: press **Cmd+Shift+P** (Mac) or **Ctrl+Shift+P** (Windows/Linux)
2. Type **"Codespaces: Rebuild Container"** and select it
3. Wait for the rebuild to complete (1-2 minutes)
4. Open a terminal and verify: `echo $YOUR_SECRET_NAME` — you should see
   the first characters of your token

### Part D: Run this command

```
/install-private-plugin https://github.com/OWNER/REPO YOUR_SECRET_NAME
```

---

## Workflow (when arguments are provided)

### Step 1: Validate environment variable

```bash
echo "${!ENV_VAR_NAME}" | head -c 12
```

If empty, output the error below and print the full **Prerequisites** section above:

```
Error: Environment variable ENV_VAR_NAME is not set.

The secret either doesn't exist, isn't granted to this Codespace's repo,
or the Codespace hasn't been rebuilt since adding it.
```

Stop here if the variable is not set.

### Step 2: Extract owner/repo from URL

Parse the GitHub URL to extract the `owner/repo` path. Support both formats:
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`

If the URL does not match a GitHub HTTPS pattern, show an error and stop.

### Step 3: Configure git URL rewrite

```bash
git config --global url."https://x-access-token:${!ENV_VAR_NAME}@github.com/OWNER/REPO".insteadOf "https://github.com/OWNER/REPO"
```

This tells git to transparently inject the PAT as an `x-access-token` credential
whenever any git client (including Claude Code's internal library) accesses this
specific repository over HTTPS.

### Step 4: Verify access

```bash
git ls-remote https://github.com/OWNER/REPO 2>&1 | head -3
```

If this fails, output:

```
Error: PAT cannot access OWNER/REPO.

Common causes:
  - The PAT wasn't granted access to OWNER/REPO (fix in GitHub > Settings >
    Developer settings > Personal access tokens > edit the token)
  - The PAT is expired (check expiration date on the token settings page)
  - Contents permission wasn't set to Read-only (edit the token's permissions)
```

Stop here if verification fails.

### Step 5: Confirm and instruct

Output:

```
Git authentication configured for OWNER/REPO.

Now run:
  /plugin marketplace add https://github.com/OWNER/REPO

Note: This auth persists in ~/.gitconfig for this Codespace session.
After a Codespace rebuild, re-run:
  /install-private-plugin https://github.com/OWNER/REPO ENV_VAR_NAME

To remove this auth:
  git config --global --unset-all url.https://x-access-token:***@github.com/OWNER/REPO.insteadof
```

## Notes

- The git URL rewrite persists in `~/.gitconfig` across shell sessions within
  the same Codespace, but will not survive a Codespace rebuild. Re-run this
  command after rebuilding.
- The PAT is stored in plaintext in `~/.gitconfig`. This is acceptable in a
  Codespace (single-user, ephemeral environment) but should not be done on
  shared machines.
- This approach works for any git-based private repo, not just GitHub.
  Adapt the URL pattern for GitLab or Bitbucket as needed.
