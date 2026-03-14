"""Generate clean paper artifact by stripping validation blocks."""

from __future__ import annotations

from meta_compiler.compiler.parser import Block, MathBlock, ProseBlock, ValidationBlock


def generate_paper(
    blocks: list[Block],
    *,
    depth: str | None = None,
) -> str:
    """Generate a clean paper from parsed blocks.

    Args:
        blocks: Parsed document blocks.
        depth: Optional depth filter ('executive', 'technical', 'appendix').
               If None, include all content.

    Returns:
        Markdown string with validation blocks stripped.
    """
    parts: list[str] = []

    if depth is not None:
        blocks = _filter_by_depth(blocks, depth)

    for block in blocks:
        if isinstance(block, ProseBlock):
            parts.append(block.content)
        elif isinstance(block, MathBlock):
            parts.append(block.raw)
            parts.append("")  # Blank line after math
        # ValidationBlocks are silently skipped

    return "\n".join(parts).strip() + "\n"


def _filter_by_depth(blocks: list[Block], target_depth: str) -> list[Block]:
    """Filter blocks to only include content at or above the target depth.

    Depth markers are <!-- depth:executive -->, <!-- depth:technical -->,
    <!-- depth:appendix --> found within prose blocks.

    Depth hierarchy: executive < technical < appendix.
    A target of 'technical' includes executive and technical but not appendix.
    """
    depth_order = {"executive": 0, "technical": 1, "appendix": 2}
    target_level = depth_order.get(target_depth, 1)

    # First, split prose blocks at depth markers so each segment can be
    # filtered independently.
    expanded: list[Block] = []
    for block in blocks:
        if isinstance(block, ProseBlock):
            expanded.extend(_split_prose_at_depth_markers(block, depth_order))
        else:
            expanded.append(block)

    result: list[Block] = []
    current_level = 0  # Start with executive (always included)
    include = True

    for block in expanded:
        if isinstance(block, ProseBlock):
            # Check if the first non-empty line is a depth marker
            for line in block.content.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("<!-- depth:") and stripped.endswith("-->"):
                    marker = stripped[len("<!-- depth:"):-len("-->")].strip()
                    if marker in depth_order:
                        current_level = depth_order[marker]
                        include = current_level <= target_level
                break  # Only examine the leading marker line

        if include:
            result.append(block)

    return result


def _split_prose_at_depth_markers(
    block: ProseBlock,
    depth_order: dict[str, int],
) -> list[ProseBlock]:
    """Split a ProseBlock into sub-blocks at each depth marker boundary."""
    lines = block.content.split("\n")
    segments: list[ProseBlock] = []
    current: list[str] = []

    for line in lines:
        stripped = line.strip()
        if (
            stripped.startswith("<!-- depth:")
            and stripped.endswith("-->")
            and stripped[len("<!-- depth:"):-len("-->")].strip() in depth_order
        ):
            # Flush accumulated lines as a segment (even if empty — the marker
            # itself will start the new segment)
            if current:
                text = "\n".join(current)
                if text.strip():
                    segments.append(ProseBlock(content=text + "\n"))
                current = []
            # Start new segment with the marker line
            current.append(line)
        else:
            current.append(line)

    if current:
        text = "\n".join(current)
        if text.strip():
            segments.append(ProseBlock(content=text + "\n"))

    return segments
