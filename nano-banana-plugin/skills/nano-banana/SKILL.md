---
name: nano-banana
description: This skill should be used when the user asks to "generate an image", "create an image", "nano banana", "AI image", "make a picture", "image preset", "edit an image with AI", or mentions generating visual content using the Gemini API. Provides 25 style presets across 6 categories with configurable aspect ratios and resolutions.
---

## Purpose

Generate and edit images via the Gemini REST API using the Python script at `scripts/nano_banana.py` (relative to this skill's base directory). Support 25 style presets across 6 categories (Technical, Business, Creative, UI/UX, Photography, Specialized) to produce consistently styled output without manual prompt engineering. Configure aspect ratios from 14 available options and resolution tiers ranging from 512px to 4K to match any output target.

## Prerequisites

- `NANO_BANANA_API_KEY` environment variable set to a valid Google AI Studio API key
- Python 3.8 or higher installed
- `requests` library installed (`pip install requests`)

## Quick Start

**Path resolution:** When this skill is loaded, Claude Code displays a "Base directory for this skill:" header. Use that absolute path to resolve script paths in all bash commands below. In the examples, `$BASE_DIR` represents this path.

**Minimal (auto-names file using config defaults):**
```bash
python3 $BASE_DIR/scripts/nano_banana.py \
  --prompt "A modern office building at sunset"
```

**With preset and explicit output:**
```bash
python3 $BASE_DIR/scripts/nano_banana.py \
  --prompt "A Victorian house with garden" \
  --output ./house_blueprint.png \
  --preset blueprint
```

**Image editing (with reference):**
```bash
python3 $BASE_DIR/scripts/nano_banana.py \
  --prompt "Convert to watercolor style" \
  --output ./watercolor_version.png \
  --preset watercolor \
  --input ./original_photo.png
```

## Arguments Reference

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--prompt` | Yes | — | Text prompt describing the image to generate |
| `--output` | No | auto | Output file path; if omitted, auto-generates from config `output_dir` + `filename_template` |
| `--preset` | No | config | Style preset slug (see Preset Reference below) |
| `--size` | No | config | Resolution tier: `512px`, `1K`, `2K`, `4K` |
| `--aspect` | No | config | Aspect ratio (see Available Aspect Ratios) |
| `--model` | No | config | Model selection: `flash` (fast) or `pro` (higher quality) |
| `--input` | No | — | Reference image path for editing (repeatable, up to 14 images) |
| `--deck` | No | — | Path to a deck spec JSON file; generates all slides (mutually exclusive with `--prompt`, `--output`, `--preset`) |
| `--force` | No | — | Regenerate all slides even if they already exist (only used with `--deck`) |
| `--list-presets` | No | — | List all available presets and exit |

**Default priority:** CLI flag > preset default > `config.json` > hardcoded fallback

## Preset Quick-Reference

Note: Preset defaults for aspect/size apply only when not explicitly overridden via `--aspect` or `--size` flags.

| Category | Slug | Aspect | Size |
|----------|------|--------|------|
| Technical | `blueprint` | 3:2 | 2K |
| Technical | `exploded-view` | 1:1 | 2K |
| Technical | `anatomical` | 3:4 | 2K |
| Technical | `isometric` | 1:1 | 2K |
| Technical | `system-diagram` | 16:9 | 2K |
| Technical | `site-map` | 4:3 | 2K |
| Business | `infographic` | 9:16 | 2K |
| Business | `slide` | 16:9 | 2K |
| Business | `hero-banner` | 16:9 | 2K |
| Business | `product-mockup` | 1:1 | 2K |
| Business | `data-viz` | 16:9 | 2K |
| Creative | `watercolor` | 3:2 | 2K |
| Creative | `pencil-sketch` | 1:1 | 2K |
| Creative | `flat-vector` | 1:1 | 2K |
| Creative | `cinematic` | 21:9 | 4K |
| Creative | `concept-art` | 16:9 | 4K |
| Creative | `pixel-art` | 1:1 | 1K |
| UI/UX | `app-mockup` | 9:16 | 2K |
| UI/UX | `icon` | 1:1 | 1K |
| UI/UX | `logo` | 1:1 | 1K |
| UI/UX | `wireframe` | 16:9 | 2K |
| Photography | `portrait` | 3:4 | 2K |
| Photography | `lifestyle` | 3:2 | 2K |
| Photography | `architectural-viz` | 16:9 | 4K |
| Specialized | `storyboard` | 16:9 | 2K |

## Available Aspect Ratios

`1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`

## Available Resolutions

`512px`, `1K`, `2K`, `4K`

## Edit Mode

Pass one or more reference images using the `--input` flag to activate edit mode instead of pure generation:

- Pass a reference image with `--input path/to/image.png`; repeat the flag up to 14 times for multi-image edits
- Up to 14 reference images are supported in a single call
- Supported formats: PNG, JPEG, WebP, GIF
- Write the prompt to describe what to do with or to the reference image(s) rather than describing a scene from scratch
- Combine with presets for style transfer — for example, `--preset watercolor --input photo.png` applies the watercolor style system prompt alongside the reference image
- When multiple `--input` files are provided, the model receives all images simultaneously and can blend, compare, or composite them based on the prompt

## Deck Mode

Generate an entire slide deck from a JSON specification file in a single invocation. Each slide is rendered as a separate image using per-slide prompts, presets, and presentation-level styling defined in the spec.

**Invoke with `--deck`:**
```bash
python3 $BASE_DIR/scripts/nano_banana.py --deck ./decks/my_deck_spec.json
```

**Key behaviors:**

- `--deck path/to/deck_spec.json` — reads the deck specification and generates all slides sequentially
- `--force` — regenerate all slides even if output files already exist; without this flag, existing slides are skipped (resume behavior)
- When `--deck` is provided, `--prompt`, `--output`, and `--preset` are mutually exclusive and must not be used — all settings come from the deck spec JSON and the presentation config
- `--model` and `--size` can still be passed to override the deck-level defaults

**Output format:**

The script creates a numbered output folder containing:
- `slide_01.png`, `slide_02.png`, ... `slide_NN.png` — one image per slide
- A copy of `deck_spec.json` — preserved alongside the output for reproducibility

**Resume behavior:**

If generation is interrupted, run the same command again. The script detects existing slide files (e.g., `slide_03.png`) and skips them automatically. Only missing slides are generated. Use `--force` to override this and regenerate everything.

**Error handling:**

- Individual slide failures do not abort the deck — the script continues to the next slide
- Failed slides are listed in the JSON summary output
- Exit code `0` if at least one slide was generated successfully
- Exit code `1` only if ALL slides failed

**JSON summary output:**

On completion, stdout contains a JSON summary:
```json
{
  "deck": "/abs/path/to/output_folder",
  "slides_generated": 8,
  "slides_failed": 1,
  "failed_slides": [{"slide_number": 3, "error": "Content filtering triggered"}],
  "total_slides": 9,
  "model": "flash",
  "presentation_config": "consulting"
}
```

**Generating deck spec files:**

Use the `/deck-prompt` skill to generate deck specification JSON files from markdown or PDF reports. That skill handles content extraction, slide planning, and per-slide prompt authoring — producing a ready-to-render spec file for `--deck`.

## Models

| Model | Flag | Best For |
|-------|------|----------|
| Gemini 3.1 Flash Image | `--model flash` | Fast generation, iteration, drafts |
| Gemini 3 Pro Image | `--model pro` | High-quality final assets, complex scenes |

Select `flash` for iterative work where speed matters. Select `pro` for final deliverables or complex scenes with fine detail requirements.

## Output

The script writes results to stdout as JSON and saves the image to the path specified by `--output`:

- **Success:** `{"output": "/abs/path.png", "model": "model-id", "preset": "slug-or-null"}` with exit code 0
- **Error:** `{"error": "message", "code": "ERROR_TYPE"}` with a non-zero exit code
- Image is always saved as PNG regardless of the `--output` extension
- Parent directories of the `--output` path are created automatically if they do not exist
- **Version safety:** If the target file already exists, the script appends `_v2`, `_v3`, etc. instead of overwriting. The JSON output reflects the actual versioned path used

Parse stdout JSON to confirm success and retrieve the resolved absolute output path.

## Configuration

Edit `$BASE_DIR/config.json` to set persistent defaults:

```json
{
  "output_dir": "output/nano-banana",
  "size": "2K",
  "aspect": "1:1",
  "model": "flash",
  "preset": null,
  "filename_template": "{prompt_slug}_{timestamp}.png"
}
```

| Key | Type | Description |
|-----|------|-------------|
| `output_dir` | string | Directory for auto-generated output (relative to project root, or absolute) |
| `size` | string | Default resolution tier (`512px`, `1K`, `2K`, `4K`) |
| `aspect` | string | Default aspect ratio |
| `model` | string | Default model (`flash` or `pro`) |
| `preset` | string/null | Default preset slug (null = none) |
| `filename_template` | string | Template for auto-generated filenames. Variables: `{prompt_slug}`, `{timestamp}` |

When `--output` is omitted, the script auto-generates a filename using `output_dir` + `filename_template` and prints the path to stderr.

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| `"Missing NANO_BANANA_API_KEY"` | Set the environment variable: `export NANO_BANANA_API_KEY=your_key_here` using a key from Google AI Studio |
| `"Missing 'requests' library"` | Install the dependency: `pip install requests` |
| Content filtering refusal | Rephrase the prompt to avoid terms that trigger Gemini safety filters; remove explicit style descriptors if necessary |
| Rate limiting errors | The script retries once after 2 seconds automatically; if the error persists, wait 60 seconds and retry manually |
| Timeout on `--model pro` | API timeout is 60 seconds; complex prompts with `pro` may approach this limit — simplify the prompt or switch to `flash` for drafts |
| Corrupt or zero-byte output | Confirm the `--output` path is writable and the filesystem has available space |

## Additional Resources

- **`$BASE_DIR/references/presets.md`** — Full prompt engineering guide with per-preset tips, example prompts, and customization advice for each of the 25 presets
