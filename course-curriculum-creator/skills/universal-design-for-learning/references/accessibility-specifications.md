# Accessibility Specifications for Training Materials

## Purpose

Translate UDL principles into actionable WCAG 2.1 AA technical specifications. Use this reference when generating artifacts, handouts, slides, and digital materials.

## Color & Contrast

### WCAG 2.1 AA Requirements
- **Normal text** (under 18pt or 14pt bold): minimum 4.5:1 contrast ratio
- **Large text** (18pt+ or 14pt+ bold): minimum 3:1 contrast ratio
- **Non-text elements** (icons, chart elements, form borders): minimum 3:1 contrast ratio
- **Focus indicators**: minimum 3:1 contrast against adjacent colors

### Compliant Color Combinations
| Background | Text Color | Ratio | Use For |
|---|---|---|---|
| White (#FFFFFF) | Dark gray (#333333) | 12.6:1 | Body text — preferred over pure black for reduced eye strain |
| White (#FFFFFF) | Dark blue (#1A365D) | 11.4:1 | Headings, links |
| Light gray (#F7F7F7) | Dark gray (#333333) | 10.9:1 | Alternate row backgrounds |
| Dark blue (#1A365D) | White (#FFFFFF) | 11.4:1 | Slide headers, emphasis blocks |

### Color Usage Rules
- Never use color as the sole carrier of meaning (always pair with labels, patterns, or icons)
- In charts: use patterns/textures in addition to color; label data directly when possible
- Test all materials with a color blindness simulator (e.g., Coblis, Sim Daltonism)
- Provide a color legend with text labels for any color-coded content

### Contrast Checking Tools
- WebAIM Contrast Checker: webaim.org/resources/contrastchecker
- Colour Contrast Analyser (desktop app): TPGi
- Built-in: macOS Accessibility Inspector, Chrome DevTools

## Typography

### Recommended Accessible Fonts
| Font | Type | Why Accessible | Best For |
|---|---|---|---|
| **Atkinson Hyperlegible** | Sans-serif | Designed specifically for low vision; distinct letterforms (Il1, O0) | Handouts, worksheets |
| **Source Sans Pro** | Sans-serif | Open-source, excellent x-height, clear at small sizes | Digital materials, slides |
| **Open Sans** | Sans-serif | Wide letterforms, good screen rendering | Projected slides, handouts |

### Minimum Sizes by Context
| Context | Minimum Size | Recommended |
|---|---|---|
| Projected slides (body text) | 18pt | 24pt |
| Projected slides (titles) | 28pt | 36pt |
| Printed handouts (body text) | 12pt | 13-14pt |
| Printed handouts (headings) | 14pt | 16-18pt |
| Digital documents (body) | 12pt / 1rem | 14pt / 1.125rem |
| Captions/footnotes | 10pt | 11pt |

### Spacing & Layout
- **Line spacing:** 1.5 for body text (minimum 1.15 for dense reference materials)
- **Paragraph spacing:** At least 1.5x the line spacing
- **Line length:** 50-75 characters per line (prevents tracking errors)
- **Alignment:** Left-aligned (never justified — uneven word spacing impairs reading)
- **White space:** Generous margins (1 inch minimum for print)

## Document Accessibility Checklist

### Structure
- [ ] Heading hierarchy is logical (H1 → H2 → H3, no skipped levels)
- [ ] Headings describe content (not "Section 1" but "Learning Objectives")
- [ ] Lists use proper list markup (not manually typed bullets)
- [ ] Tables have header rows marked as headers
- [ ] Reading order matches visual layout (test by tabbing through)

### Images & Visual Content
- [ ] All images have alt text describing content and purpose
- [ ] Decorative images have empty alt text (alt="")
- [ ] Complex diagrams have long descriptions or text alternatives
- [ ] Charts include data tables as alternatives
- [ ] Screenshots include text descriptions of key elements

### Text Content
- [ ] Plain language used (8th-grade reading level for general audiences)
- [ ] Acronyms defined at first use
- [ ] Links are descriptive (not "click here" — use "download the worksheet")
- [ ] Instructions don't rely on sensory characteristics ("click the red button" → "click the Submit button")

### PDF Specific
- [ ] PDF is tagged (not scanned image)
- [ ] Reading order is correct (test with screen reader)
- [ ] Form fields have labels
- [ ] Document language is set
- [ ] Title is set in document properties

## Slide Accessibility Checklist

- [ ] Every slide has a unique, descriptive title
- [ ] Text is not embedded in images (use text boxes)
- [ ] Animations are minimal and non-essential (content accessible without animation)
- [ ] Alt text on all non-decorative images
- [ ] Slide reading order is set correctly (check in Accessibility Checker)
- [ ] Font size meets minimums (18pt+ body, 28pt+ title)
- [ ] High contrast between text and background
- [ ] Speaker notes contain full narrative (usable as transcript)
- [ ] No auto-advancing slides (participants control pace)

## Video & Audio Requirements

### Captions
- **Synchronized captions** required for all video content
- **Accuracy:** 99%+ (auto-generated captions must be edited)
- **Formatting:** Max 2 lines, 32 characters per line, 1-second minimum display
- **Speaker identification** when multiple speakers

### Transcripts
- **Full text transcript** for all audio and video content
- Include speaker identification, relevant sound effects, and visual descriptions
- Provide as separate downloadable document

### Audio Description
- **Audio description** for visual-only content (diagrams drawn on screen, physical demonstrations)
- Alternative: provide verbal narration of all visual content as standard practice

## Quick Compliance Check (5-Minute Pre-Delivery Audit)

Run through these 10 items before delivering any training materials:

1. [ ] Slide fonts are 18pt+ body, 28pt+ title
2. [ ] Handout fonts are 12pt+ with 1.5 line spacing
3. [ ] Color is never the only way information is conveyed
4. [ ] All images have alt text
5. [ ] Headings are used for structure (not just bold text)
6. [ ] Links are descriptive (no "click here")
7. [ ] Videos have captions
8. [ ] Materials available in digital format (not print-only)
9. [ ] Reading order makes sense when read linearly
10. [ ] Acronyms defined at first use

**Score:** 10/10 = ready. <8/10 = fix before delivery. <6/10 = significant accessibility barriers.
