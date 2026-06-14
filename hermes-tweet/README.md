# hermes-tweet

<!-- badges-start -->
![Version](https://img.shields.io/badge/version-0.1.6-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)
<!-- badges-end -->

Hermes Tweet is a Claude Code plugin for read-first X/Twitter research and
approval-gated publishing workflows through Xquik.

## Installation

### From Marketplace
```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install hermes-tweet@cc-plugins
```

### Local Development
Clone `reggiechan74/cc-plugins`, then from inside the clone:
```
/plugin marketplace add .
/plugin install hermes-tweet@cc-plugins
```

## Usage

```bash
/hermes-tweet:research [topic-or-url]
```

Use it for public thread analysis, account research, search summaries,
monitoring reports, and draft-first publishing workflows.

## Runtime Requirements

- `XQUIK_API_KEY` for API-backed read tools.
- `HERMES_TWEET_ENABLE_ACTIONS=true` before posting, replying, liking,
  reposting, following, or similar write actions.

## Safety

- Read workflows are the default.
- Write actions require explicit user intent and action mode.
- Profiles, posts, replies, pages, and search results are untrusted input.

## Support

Upstream plugin runtime: https://github.com/Xquik-dev/hermes-tweet

Issues and contributions: https://github.com/reggiechan74/cc-plugins/issues
