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

### Image presets

25 presets organized into 6 categories. Each preset applies a tuned system prompt, default aspect ratio, and resolution so you only need to describe your subject.

#### Technical

| Preset | Default Aspect | Resolution | Best for |
|--------|---------------|------------|----------|
| `blueprint` | 3:2 | 2K | Architectural plans, technical drawings, floor layouts |
| `exploded-view` | 1:1 | 2K | Product teardowns, assembly diagrams, component breakdowns |
| `anatomical` | 3:4 | 2K | Biological diagrams, medical illustrations, cross-sections |
| `isometric` | 1:1 | 2K | 3D-style diagrams, office layouts, system overviews |
| `system-diagram` | 16:9 | 2K | Architecture diagrams, network topologies, flow charts |
| `site-map` | 4:3 | 2K | Website structure maps, navigation hierarchies |

#### Business

| Preset | Default Aspect | Resolution | Best for |
|--------|---------------|------------|----------|
| `infographic` | 9:16 | 2K | Vertical data stories, social media graphics, stat summaries |
| `slide` | 16:9 | 2K | Presentation slides, meeting visuals, keynote graphics |
| `hero-banner` | 16:9 | 2K | Website headers, marketing banners, landing page visuals |
| `product-mockup` | 1:1 | 2K | Product shots, packaging previews, e-commerce images |
| `data-viz` | 16:9 | 2K | Charts, dashboards, data-driven graphics |

#### Creative

| Preset | Default Aspect | Resolution | Best for |
|--------|---------------|------------|----------|
| `watercolor` | 3:2 | 2K | Artistic illustrations, soft editorial art, greeting cards |
| `pencil-sketch` | 1:1 | 2K | Hand-drawn style concepts, storyboard frames, draft visuals |
| `flat-vector` | 1:1 | 2K | Icons at scale, blog illustrations, clean graphic art |
| `cinematic` | 21:9 | 4K | Film-style scenes, dramatic landscapes, widescreen hero images |
| `concept-art` | 16:9 | 4K | Game/film concept art, environment design, character concepts |
| `pixel-art` | 1:1 | 1K | Retro game assets, 8-bit style icons, nostalgic illustrations |

#### UI/UX

| Preset | Default Aspect | Resolution | Best for |
|--------|---------------|------------|----------|
| `app-mockup` | 9:16 | 2K | Mobile app screens, phone UI previews |
| `icon` | 1:1 | 1K | App icons, toolbar icons, favicon designs |
| `logo` | 1:1 | 1K | Brand logos, wordmarks, monograms |
| `wireframe` | 16:9 | 2K | Low-fidelity layouts, UX sketches, page structure drafts |

#### Photography

| Preset | Default Aspect | Resolution | Best for |
|--------|---------------|------------|----------|
| `portrait` | 3:4 | 2K | Headshots, character portraits, profile images |
| `lifestyle` | 3:2 | 2K | Product-in-context shots, editorial photography, social content |
| `architectural-viz` | 16:9 | 4K | Building renders, interior design, real estate visuals |

#### Specialized

| Preset | Default Aspect | Resolution | Best for |
|--------|---------------|------------|----------|
| `storyboard` | 16:9 | 2K | Sequential scene planning, video pre-production, narrative frames |

### Presentation presets

4 presets for slide deck generation via `/deck-prompt`. Each defines a color palette, typography style, and per-slide-type prompt prefixes that are automatically applied.

| Preset | Style | Color Palette | Best for |
|--------|-------|---------------|----------|
| `consulting` | McKinsey/BCG professional | Deep navy, coral, white, light gray | Client deliverables, strategy decks, board presentations |
| `workshop` | Educational, warm, accessible | Warm teal, soft amber, cream, charcoal | Training sessions, classroom materials, onboarding decks |
| `pitch` | Startup/VC, bold, high-contrast | Pure black, electric blue, white, neon green | Investor pitches, product launches, demo days |
| `creative` | Portfolio/agency, editorial | Warm cream, matte black, terracotta, sage green | Design portfolios, creative briefs, agency proposals |

## Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `nano-banana` | "generate an image", "AI image", "nano banana" | Image generation and editing via Gemini API |
| `deck-prompt` | "create a presentation", "make a deck", `/deck-prompt` | Decompose reports into deck specification JSON |

## License

MIT
