# Changelog

All notable changes to nano-banana will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `notebooklm` presentation preset — architectural engineering aesthetic with blueprint-inspired styling, engineering cream background, and copper/teal accents for institutional investor reports
- **Structured prompt schema** — new deck spec fields (`heading`, `visual`, `labels`, `text_panel`, `reference_image`, `style_overrides`) replace freeform `prompt` field
- **Template assembly engine** — presentation configs define per-slide-type templates with `{style_context}`, `{heading}`, `{visual}`, `{label_instruction}`, `{text_panel}` slots
- Per-slide `reference_image` support for style consistency chaining
- Retry with simplification — on failure, retries once with `text_panel` stripped, tracks `warnings` in JSON summary

### Changed
- Default model switched from `flash` to `pro` across all 5 presentation configs for better text fidelity
- `style_context` replaces hex color codes with color names to prevent codes leaking into rendered slides
- Templates use `No slide number` instruction to prevent Gemini from hallucinating arbitrary numbers
- `deck-prompt` skill rewritten with structured field authoring rules (physical metaphor first, claim headings, 2-sentence text panels)

### Fixed
- `shutil.copy2` same-file error when `deck_spec.json` is already in the output directory
- Quote marks around `{heading}` and label format strings no longer leak into rendered slide text

## [1.0.0] - 2026-02-27

### Added
- AI image generation via Gemini API with 25 style presets across 6 categories
  - Technical: blueprint, exploded-view, anatomical, isometric, system-diagram, site-map
  - Business: infographic, slide, hero-banner, product-mockup, data-viz
  - Creative: watercolor, pencil-sketch, flat-vector, cinematic, concept-art, pixel-art
  - UI/UX: app-mockup, icon, logo, wireframe
  - Photography: portrait, lifestyle, architectural-viz
  - Specialized: storyboard
- Image editing with up to 14 reference images per call
- Batch deck generation from JSON specifications with resume support
- Report-to-slides decomposition for markdown and PDF reports
- 4 presentation presets: consulting, workshop, pitch, creative
- Version-safe output — never overwrites existing files
- `nano-banana` skill for image generation and editing
- `/deck-prompt` skill for report-to-deck decomposition
