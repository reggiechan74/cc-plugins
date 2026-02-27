#!/usr/bin/env python3
"""nano-banana: Generate or edit images via the Gemini REST API."""

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print(
        json.dumps(
            {
                "error": "Missing 'requests' library. Install with: pip install requests",
                "code": "MISSING_DEPENDENCY",
            }
        )
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODELS = {
    "flash": "gemini-3.1-flash-image-preview",
    "pro": "gemini-3-pro-image-preview",
}

VALID_ASPECTS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3",
    "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]

VALID_SIZES = ["512px", "1K", "2K", "4K"]

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
# In plugin context, resolve relative output paths from the user's working directory
PROJECT_ROOT = Path.cwd()
CONFIG_PATH = SKILL_ROOT / "config.json"

# Hardcoded fallbacks (used when config.json is missing or incomplete)
HARDCODED_DEFAULTS = {
    "output_dir": "output/nano-banana",
    "size": "1K",
    "aspect": "1:1",
    "model": "flash",
    "preset": None,
    "filename_template": "{prompt_slug}_{timestamp}.png",
}

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_config():
    """Load config.json from the skill root, merged over hardcoded defaults.

    Returns (config_dict, presets_dict).
    """
    config = dict(HARDCODED_DEFAULTS)
    presets = {}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                user_config = json.load(f)
            for key in HARDCODED_DEFAULTS:
                if key in user_config and user_config[key] is not None:
                    config[key] = user_config[key]
            presets = user_config.get("presets", {})
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Warning: could not load {CONFIG_PATH}: {exc}", file=sys.stderr)
    if not presets:
        print("Warning: no presets found in config.json", file=sys.stderr)
    return config, presets


# Load config at module level so presets are available for argparse choices
_CONFIG, PRESETS = load_config()


def generate_output_path(config, prompt_text):
    """Build an auto-generated output path from config template and output_dir."""
    import re
    slug = re.sub(r"[^a-z0-9]+", "_", prompt_text[:40].lower()).strip("_")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = config["filename_template"].format(
        prompt_slug=slug,
        timestamp=timestamp,
    )
    output_dir = Path(config["output_dir"])
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    return str(output_dir / filename)


def load_presentation_config(config_name):
    """Load a presentation config JSON from presets/presentations/.

    Returns the parsed config dict.
    Raises FileNotFoundError if the named config doesn't exist.
    """
    config_dir = SKILL_ROOT / "presets" / "presentations"
    config_path = config_dir / f"{config_name}.json"
    if not config_path.exists():
        available = [p.stem for p in config_dir.glob("*.json")] if config_dir.exists() else []
        raise FileNotFoundError(
            f"Presentation config '{config_name}' not found at {config_path}. "
            f"Available: {', '.join(sorted(available)) or 'none'}"
        )
    with open(config_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def list_presets():
    """Print a formatted table of all presets grouped by category, then exit."""
    by_category = {}
    for slug, info in PRESETS.items():
        cat = info["category"]
        by_category.setdefault(cat, []).append((slug, info))

    for cat in sorted(by_category):
        print(f"\n  {cat}")
        print(f"  {'─' * 40}")
        for slug, info in sorted(by_category[cat], key=lambda x: x[0]):
            print(f"  {slug:<20s} {info['default_aspect']:<6s}  {info['default_size']}")

    print()
    sys.exit(0)


def build_prompt(user_prompt, preset_name):
    """Prepend the preset's prompt_prefix (if any) to the user prompt."""
    if preset_name is not None:
        prefix = PRESETS[preset_name]["prompt_prefix"]
        combined = prefix + user_prompt
    else:
        combined = user_prompt
    if len(combined) > 4000:
        print(
            f"Warning: combined prompt is {len(combined)} characters, which may exceed model limits.",
            file=sys.stderr,
        )
    return combined


def resolve_config(args, config):
    """Apply defaults with priority: CLI flag > preset > config file > hardcoded.

    Uses None defaults in argparse to distinguish "not provided" from "explicitly
    set to a value that happens to match the global default."
    """
    # Layer 1: preset defaults (only when user didn't pass the flag)
    if args.preset is not None:
        preset = PRESETS[args.preset]
        if args.aspect is None:
            args.aspect = preset["default_aspect"]
        if args.size is None:
            args.size = preset["default_size"]
    # Layer 2: config file defaults
    if args.aspect is None:
        args.aspect = config.get("aspect")
    if args.size is None:
        args.size = config.get("size")
    if args.model is None:
        args.model = config.get("model")
    if args.preset is None and config.get("preset"):
        args.preset = config["preset"]
    # Layer 3: hardcoded fallbacks (guaranteed non-None)
    if args.aspect is None:
        args.aspect = "1:1"
    if args.size is None:
        args.size = "1K"
    if args.model is None:
        args.model = "flash"


def load_input_images(paths):
    """Read, validate, and base64-encode a list of input image file paths."""
    ext_to_mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    images = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            raise FileNotFoundError(f"Input image not found: {p}")
        ext = path.suffix.lower()
        mime = ext_to_mime.get(ext)
        if mime is None:
            raise ValueError(
                f"Unsupported image format '{ext}' for file: {p}. "
                f"Supported: {', '.join(sorted(ext_to_mime.keys()))}"
            )
        raw = path.read_bytes()
        b64_str = base64.b64encode(raw).decode("utf-8")
        images.append({"inline_data": {"mime_type": mime, "data": b64_str}})
    return images


def build_request_body(prompt, aspect, size, input_images=None):
    """Build the JSON request body for the Gemini generateContent endpoint."""
    parts = [{"text": prompt}]
    if input_images:
        parts.extend(input_images)

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect,
                "imageSize": size,
            },
        },
    }
    return body


def call_api(request_body, model_id, api_key):
    """POST to the Gemini generateContent endpoint with one retry on 429."""
    url = f"{API_BASE}/{model_id}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    resp = requests.post(url, headers=headers, json=request_body, timeout=60)

    if resp.status_code == 429:
        time.sleep(2)
        resp = requests.post(url, headers=headers, json=request_body, timeout=60)

    if not resp.ok:
        raise RuntimeError(
            f"API request failed (HTTP {resp.status_code}): {resp.text}"
        )

    return resp.json()


def extract_image(response):
    """Extract the first image from the Gemini response.

    Returns (b64_data, mime_type).
    """
    try:
        parts = response["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected API response structure: {exc}") from exc

    text_parts = []
    for part in parts:
        # REST API returns camelCase; check both forms for robustness
        inline = part.get("inlineData") or part.get("inline_data")
        if inline:
            mime = inline.get("mimeType") or inline.get("mime_type", "")
            if mime.startswith("image/"):
                return inline["data"], mime
        if "text" in part:
            text_parts.append(part["text"])

    # No image found — build an informative error
    detail = ""
    if text_parts:
        detail = f" Model response: {' '.join(text_parts)}"
    raise RuntimeError(f"No image found in API response.{detail}")


def resolve_versioned_path(output_path):
    """If output_path already exists, append _v2, _v3, ... to avoid overwriting.

    First file written to a path gets no version suffix.
    If that path already exists, the new file gets _v2, then _v3, etc.
    """
    import re as _re

    out = Path(output_path)
    if not out.exists():
        return str(out)

    stem = out.stem
    ext = out.suffix

    # Strip any existing _vN suffix so we can scan cleanly
    base_match = _re.match(r"^(.+?)(_v\d+)$", stem)
    base_stem = base_match.group(1) if base_match else stem

    # Find the highest existing version number
    max_ver = 1  # the existing file without suffix counts as v1
    for sibling in out.parent.iterdir():
        if not sibling.is_file():
            continue
        sib_stem = sibling.stem
        sib_match = _re.match(
            r"^" + _re.escape(base_stem) + r"_v(\d+)$", sib_stem
        )
        if sib_match:
            max_ver = max(max_ver, int(sib_match.group(1)))

    next_ver = max_ver + 1
    versioned = out.parent / f"{base_stem}_v{next_ver}{ext}"
    return str(versioned)


def save_image(b64_data, output_path):
    """Decode base64 image data and write to disk. Returns absolute path."""
    out = Path(output_path)
    if out.suffix.lower() not in (".png", ""):
        print(
            f"Warning: output extension is '{out.suffix}' but image data is PNG. "
            f"Consider using .png extension.",
            file=sys.stderr,
        )
    os.makedirs(out.parent, exist_ok=True)
    out.write_bytes(base64.b64decode(b64_data))
    return str(out.resolve())


def run_deck(deck_spec_path, force=False):
    """Generate all slides from a deck specification JSON file.

    Returns a summary dict with generation results.
    """
    import shutil

    # --- Parse deck spec ---------------------------------------------------
    deck_path = Path(deck_spec_path)
    if not deck_path.exists():
        raise FileNotFoundError(f"Deck spec not found: {deck_spec_path}")

    with open(deck_path) as f:
        deck = json.load(f)

    # --- Load presentation config ------------------------------------------
    pres_config = load_presentation_config(deck["presentation_config"])

    # --- Resolve output directory ------------------------------------------
    output_dir = Path(deck["output_dir"])
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Copy deck spec into output dir for reference
    spec_dest = output_dir / "deck_spec.json"
    if not spec_dest.exists() or force:
        shutil.copy2(deck_path, spec_dest)

    # --- Get API key -------------------------------------------------------
    api_key = os.environ.get("NANO_BANANA_API_KEY")
    if not api_key:
        raise RuntimeError("NANO_BANANA_API_KEY environment variable is not set")

    # --- Generate slides ---------------------------------------------------
    total = deck["total_slides"]
    slides = deck["slides"]
    generated = 0
    failed = []

    for slide in slides:
        num = slide["slide_number"]
        slide_type = slide["slide_type"]
        layout = slide.get("layout", pres_config["slide_types"].get(slide_type, {}).get("default_layout", ""))
        prompt_text = slide["prompt"]
        overrides = slide.get("style_overrides", {})

        slide_file = output_dir / f"slide_{num:02d}.png"

        # Resume support: skip existing slides unless --force
        if slide_file.exists() and not force:
            print(
                f"  [{num}/{total}] Skipping slide {num} (already exists)",
                file=sys.stderr,
            )
            generated += 1
            continue

        # Assemble prompt: global + type prefix + layout hint + user prompt
        global_prefix = pres_config.get("global_prompt_prefix", "")
        type_info = pres_config["slide_types"].get(slide_type, {})
        type_prefix = type_info.get("prompt_prefix", "")
        layout_hint = f"Layout: {layout}. " if layout else ""
        full_prompt = global_prefix + type_prefix + layout_hint + prompt_text

        # Resolve settings
        aspect = overrides.get("aspect", pres_config.get("default_aspect", "16:9"))
        size = overrides.get("size", pres_config.get("default_size", "2K"))
        model_key = overrides.get("model", pres_config.get("default_model", "flash"))
        model_id = MODELS.get(model_key, MODELS["flash"])

        # Progress
        label = prompt_text[:50] + ("..." if len(prompt_text) > 50 else "")
        print(
            f"  [{num}/{total}] Generating {slide_type} slide: \"{label}\"",
            file=sys.stderr,
        )

        try:
            body = build_request_body(full_prompt, aspect, size)
            response = call_api(body, model_id, api_key)
            b64_data, _mime = extract_image(response)
            save_image(b64_data, str(slide_file))
            generated += 1
        except Exception as exc:
            error_msg = str(exc)
            print(
                f"  [{num}/{total}] FAILED: {error_msg[:100]}",
                file=sys.stderr,
            )
            failed.append({"slide_number": num, "error": error_msg})

    # --- Summary -----------------------------------------------------------
    summary = {
        "deck": str(output_dir.resolve()),
        "slides_generated": generated,
        "slides_failed": len(failed),
        "failed_slides": failed,
        "total_slides": total,
        "model": pres_config.get("default_model", "flash"),
        "presentation_config": deck["presentation_config"],
    }
    return summary


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    """Entry-point: parse args, generate image, write output."""
    # --- Argument parser ---------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Generate or edit images via Gemini API"
    )
    parser.add_argument(
        "--prompt", default=None, help="Text prompt describing the image"
    )
    parser.add_argument(
        "--output", default=None,
        help="Output file path (auto-generated from config if omitted)",
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        default=None,
        help="Style preset slug",
    )
    parser.add_argument(
        "--size",
        choices=VALID_SIZES,
        default=None,
        help="Resolution (default from config)",
    )
    parser.add_argument(
        "--aspect",
        choices=VALID_ASPECTS,
        default=None,
        help="Aspect ratio (default from config)",
    )
    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()),
        default=None,
        help="Model: flash or pro (default from config)",
    )
    parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        default=None,
        help="Reference image path (repeatable, up to 14)",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available presets and exit",
    )
    parser.add_argument(
        "--deck",
        default=None,
        help="Deck spec JSON file path (generates all slides in batch mode)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regenerate all slides in deck mode (ignore existing files)",
    )

    # Handle --list-presets before requiring --prompt/--output
    # by checking for it in sys.argv before full parse
    if "--list-presets" in sys.argv:
        list_presets()

    args = parser.parse_args()

    # --- Deck mode ---------------------------------------------------------
    if args.deck:
        api_key = os.environ.get("NANO_BANANA_API_KEY")
        if not api_key:
            print(json.dumps({"error": "NANO_BANANA_API_KEY environment variable is not set", "code": "MISSING_API_KEY"}))
            sys.exit(1)
        try:
            summary = run_deck(args.deck, force=args.force)
            print(json.dumps(summary))
            sys.exit(0 if summary["slides_generated"] > 0 else 1)
        except Exception as exc:
            print(json.dumps({"error": str(exc), "code": "DECK_ERROR"}))
            sys.exit(1)

    # --- Single image mode (existing logic) --------------------------------
    if not args.prompt:
        parser.error("--prompt is required (unless using --deck mode)")

    # --- Load config (already loaded at module level) -----------------------
    config = _CONFIG

    # --- Auto-generate output path if omitted ------------------------------
    if args.output is None:
        args.output = generate_output_path(config, args.prompt)
        print(f"Output: {args.output}", file=sys.stderr)

    # --- Validate input count ----------------------------------------------
    if args.inputs and len(args.inputs) > 14:
        print(
            json.dumps(
                {
                    "error": f"Too many input images ({len(args.inputs)}). Maximum is 14.",
                    "code": "INVALID_INPUT",
                }
            )
        )
        sys.exit(1)

    # --- API key -----------------------------------------------------------
    api_key = os.environ.get("NANO_BANANA_API_KEY")
    if not api_key:
        print(
            json.dumps(
                {
                    "error": "NANO_BANANA_API_KEY environment variable is not set",
                    "code": "MISSING_API_KEY",
                }
            )
        )
        sys.exit(1)

    try:
        # --- Resolve config ------------------------------------------------
        resolve_config(args, config)

        # --- Build prompt --------------------------------------------------
        prompt = build_prompt(args.prompt, args.preset)

        # --- Load input images (if any) ------------------------------------
        input_images = None
        if args.inputs:
            input_images = load_input_images(args.inputs)

        # --- Build request body --------------------------------------------
        model_id = MODELS[args.model]
        body = build_request_body(prompt, args.aspect, args.size, input_images)

        # --- Call API ------------------------------------------------------
        response = call_api(body, model_id, api_key)

        # --- Extract image -------------------------------------------------
        b64_data, _mime = extract_image(response)

        # --- Resolve versioned path (never overwrite) ----------------------
        args.output = resolve_versioned_path(args.output)

        # --- Save image ----------------------------------------------------
        abs_path = save_image(b64_data, args.output)

        # --- Success -------------------------------------------------------
        print(
            json.dumps(
                {
                    "output": abs_path,
                    "model": model_id,
                    "preset": args.preset,
                }
            )
        )

    except Exception as exc:
        code = type(exc).__name__.upper()
        # Map common exception types to cleaner codes
        code_map = {
            "FILENOTFOUNDERROR": "FILE_NOT_FOUND",
            "VALUEERROR": "INVALID_INPUT",
            "RUNTIMEERROR": "API_ERROR",
            "CONNECTIONERROR": "CONNECTION_ERROR",
            "TIMEOUT": "TIMEOUT",
            "CONNECTTIMEOUT": "TIMEOUT",
            "READTIMEOUT": "TIMEOUT",
        }
        code = code_map.get(code, code)
        print(json.dumps({"error": str(exc), "code": code}))
        sys.exit(1)


if __name__ == "__main__":
    main()
