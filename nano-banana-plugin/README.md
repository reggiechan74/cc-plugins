![nano-banana hero](hero.png)

# nano-banana

<!-- badges-start -->
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/reggiechan74/cc-plugins/releases/tag/nano-banana-v1.0.0)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-blueviolet)](https://claude.ai/claude-code)
[![Gemini API](https://img.shields.io/badge/powered_by-Gemini_API-orange)](https://aistudio.google.com)
<!-- badges-end -->

AI image generation and presentation deck creation plugin for Claude Code, powered by the Gemini API.

## Features

- **25 style presets** across 6 categories: Technical, Business, Creative, UI/UX, Photography, Specialized
- **Image editing** with up to 14 reference images per call
- **Batch deck generation** from JSON specifications with resume support
- **Report-to-slides** decomposition — convert markdown/PDF reports into presentation decks
- **Version-safe output** — never overwrites existing files

## Installation

### Step 1: Add the marketplace

Register the `cc-plugins` marketplace with Claude Code:

```
/plugin marketplace add reggiechan74/cc-plugins
```

This downloads the plugin catalog from `github.com/reggiechan74/cc-plugins` and makes its plugins available for installation.

### Step 2: Install the plugin

```
/plugin install nano-banana@reggiechan74-cc-plugins
```

Or open the interactive plugin manager and browse to it:

```
/plugin
```

Navigate to the **Discover** tab, find **nano-banana**, and choose your installation scope (User, Project, or Local).

## Prerequisites

1. **Google AI Studio API key** — get one at [aistudio.google.com](https://aistudio.google.com)
2. Set the environment variable:
   ```bash
   export NANO_BANANA_API_KEY=your_key_here
   ```
3. Python 3.8+ with `requests`:
   ```bash
   pip install requests
   ```

## Usage

### Generate an image

Tell Claude: *"generate an image of a modern office building at sunset using the architectural-viz preset"*

### Create a presentation

Tell Claude: *"/deck-prompt path/to/report.md --preset consulting"*

### Available presets

| Category | Presets |
|----------|---------|
| Technical | blueprint, exploded-view, anatomical, isometric, system-diagram, site-map |
| Business | infographic, slide, hero-banner, product-mockup, data-viz |
| Creative | watercolor, pencil-sketch, flat-vector, cinematic, concept-art, pixel-art |
| UI/UX | app-mockup, icon, logo, wireframe |
| Photography | portrait, lifestyle, architectural-viz |
| Specialized | storyboard |

### Presentation presets

| Preset | Style |
|--------|-------|
| `consulting` | McKinsey/BCG professional (deep navy, coral, white) |
| `workshop` | Educational, warm (teal, amber, cream) |
| `pitch` | Startup/VC bold (black, electric blue, neon green) |
| `creative` | Portfolio/agency (cream, matte black, terracotta) |

## Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `nano-banana` | "generate an image", "AI image", "nano banana" | Image generation and editing via Gemini API |
| `deck-prompt` | "create a presentation", "make a deck", `/deck-prompt` | Decompose reports into deck specification JSON |

## License

MIT
