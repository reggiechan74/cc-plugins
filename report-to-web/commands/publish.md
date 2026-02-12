---
description: Build and publish a generated site to GitHub Pages
argument-hint: <path-to-site-directory>
allowed-tools: ["Read", "Bash", "Glob", "Grep", "AskUserQuestion"]
---

# Publish Site to GitHub Pages

Build a generated report site and publish it to GitHub Pages.

## Workflow

### Step 1: Locate the Site

If a path was provided in the arguments, use it. Otherwise, ask the user:
- "What is the path to the generated site directory?"

Verify it's a valid site project by checking for `package.json` in the directory.

### Step 2: Detect Project Type

Read `package.json` to determine the framework:

- **Vite** (has `vite` in devDependencies): build output goes to `dist/`
- **Next.js** (has `next` in dependencies): build output goes to `out/` (requires `output: "export"` in `next.config.ts`)

### Step 3: Ask Publish Method

Use AskUserQuestion to ask:

**"How do you want to publish?"** with options:

1. **GitHub Pages (Recommended)** — Create a GitHub repo, push the code, and enable GitHub Pages with automatic deployments. Every future `git push` will redeploy.
2. **Build only** — Just run the build. You'll get a folder (`dist/` or `out/`) with static HTML/CSS/JS files you can upload anywhere (Netlify, Vercel, any web host).

### Step 4: Build the Site

Run the build:

```bash
cd <site-directory>
npm install   # only if node_modules/ doesn't exist
npm run build
```

Verify the build succeeds and the output directory (`dist/` or `out/`) exists.

If the build fails, diagnose and fix the error, then retry.

### Step 5a: GitHub Pages Publish

If the user chose GitHub Pages:

1. **Ask for repo name** — Use AskUserQuestion: "What should the GitHub repository be called?" with options:
   - The site directory name (e.g., `ontario-tax-valuation-site`)
   - Custom name

2. **Set base path** — The site will be hosted at `https://<username>.github.io/<repo-name>/`, so asset paths need the repo name as a prefix:
   - **Vite sites**: Update `base` in `vite.config.js` to `'/<repo-name>/'`
   - **Next.js sites**: Add `basePath: '/<repo-name>'` in `next.config.ts` (or `next.config.mjs`)

   After updating the config, **rebuild** so the output reflects the new base path.

3. **Ensure GitHub Actions workflow exists** — Check for `.github/workflows/deploy.yml`:
   - If missing, create it using the standard GitHub Pages deploy workflow
   - For **Vite** sites, the artifact path is `./dist`
   - For **Next.js** sites, the artifact path is `./out`

4. **Ensure Next.js static export is configured** (Next.js only):
   - Check `next.config.ts` (or `.mjs`/`.js`) has `output: "export"`
   - If missing, add it and rebuild

5. **Create repo and push**:
   ```bash
   cd <site-directory>
   git init
   git add -A
   git commit -m "Initial commit — generated report site"
   gh repo create <repo-name> --public --source=. --push
   ```

6. **Enable GitHub Pages**:
   ```bash
   gh api repos/<owner>/<repo-name>/pages -X POST -f build_type=workflow
   ```

   If this fails (Pages may already be enabled), that's fine — the Actions workflow will handle deployment on push.

7. **Wait for deployment** — Tell the user:
   - The GitHub Actions workflow is now running
   - The site will be live at `https://<username>.github.io/<repo-name>/` in 1-2 minutes
   - They can check deployment status at `https://github.com/<owner>/<repo-name>/actions`

### Step 5b: Build-Only Publish

If the user chose build-only:

Tell the user:
- The built site is at `<site-directory>/dist/` (or `out/` for Next.js)
- This folder contains plain HTML, CSS, and JS — ready to upload to any web host
- Common options: drag-and-drop to Netlify, upload to any static hosting, or serve locally with `npx serve dist`

### Step 6: Summary

Print a summary:
- Build status (success/failure)
- Output directory and size
- If GitHub Pages: the live URL and repo URL
- If build-only: the path to the built files and hosting suggestions

## GitHub Actions Workflow Template

If `.github/workflows/deploy.yml` is missing, create it with this content:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: ['main']
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './BUILD_OUTPUT_DIR'

  deploy:
    environment:
      name: github-pages
      url: ${{ github.event.repository.html_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

Replace `BUILD_OUTPUT_DIR` with `dist` for Vite sites or `out` for Next.js sites.
