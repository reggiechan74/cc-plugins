# Changelog

All notable changes to nano-banana will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `notebooklm` presentation preset — architectural engineering aesthetic with blueprint-inspired styling, engineering cream background, and copper/teal accents for institutional investor reports

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
