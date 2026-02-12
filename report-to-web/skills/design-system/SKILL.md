---
name: design-system
description: This skill should be used when the user asks about "dark theme for report site",
  "presentation website styling", "report-to-web design system", "professional dark theme",
  "site theme tokens", "interactive component styling", "customize report website colors",
  "report site accessibility", "shadcn theme", "tailwind tokens", or needs guidance on the
  dark professional visual design system used by report-to-web generated sites, including
  color palettes, typography, spacing, animation patterns, responsive design, accessibility,
  component styling, and theme/registry selection.
version: 2.0.0
---

# Dark Professional Design System for Report Websites

Apply a distinctive dark professional visual identity to generated research report websites using Tailwind CSS v4 + shadcn/ui. This design system creates sites that feel like a premium data terminal crossed with a high-end law publication — dense with information yet elegant and readable.

## Design Philosophy

**Tone**: Sophisticated, authoritative, data-rich. Think Bloomberg Terminal meets The Economist's digital edition.

**Differentiation**: The signature element is the warm amber accent system against deep cool backgrounds — every interactive element glows with intention. Typography pairs a refined serif display face with a crisp humanist sans-serif body, creating tension between editorial authority and modern clarity.

**Theme System**: Color accents are swappable via theme presets (8 built-in options) or community registries, while layout, typography, and animations remain consistent.

## Color System

Colors are defined as Tailwind `@theme` tokens in `app.css` and can be overridden by theme preset CSS files. Use Tailwind utility classes for all color references — never hardcode color values.

### Core Palette

```
bg-bg-primary       → #0f1117   Deep space — main background
bg-bg-secondary     → #161922   Elevated surface — cards, panels
bg-bg-tertiary      → #1c1f2e   Recessed areas — code blocks, inputs
bg-bg-hover         → #232738   Hover state for interactive surfaces

text-text-primary    → #e8e6e1   Warm white — body text
text-text-secondary  → #9a9690   Muted warm — secondary text, labels
text-text-tertiary   → #5e5a55   Dim — disabled text, timestamps

text-accent-primary  → #d4a853   Amber gold — primary actions, highlights
text-accent-secondary → #2d9e8f  Teal — secondary interactive elements
text-accent-tertiary → #6366f1   Indigo — links, tertiary actions

border-border-primary → #2a2d3a  Subtle borders between sections
border-border-accent  → rgba(212, 168, 83, 0.2)  Amber border at 20% opacity
```

### shadcn Semantic Tokens

These map to the dark theme by default and are overridden by theme presets:

```
--color-primary          → accent-primary (gold by default)
--color-primary-foreground → bg-primary
--color-secondary        → bg-tertiary
--color-muted            → bg-tertiary
--color-muted-foreground → text-secondary
--color-destructive      → error
--color-border           → border-primary
--color-ring             → accent-primary
```

## Typography

### Font Stack

Load from Google Fonts:
- **Display/Headings**: `font-display` → `"DM Serif Display", Georgia, serif` — Elegant, authoritative serif
- **Body/UI**: `font-body` → `"IBM Plex Sans", "Helvetica Neue", sans-serif` — Crisp, professional
- **Code/Data**: `font-mono` → `"IBM Plex Mono", "Consolas", monospace` — Clean monospace for numbers

### Type Treatments

- **Headings**: `font-display text-text-primary` with tracking-tight
- **Body**: `font-body text-text-primary` with `leading-[1.7] max-w-[72ch]`
- **Labels/Captions**: `text-xs uppercase tracking-wide text-text-secondary`
- **Data/Numbers**: `font-mono text-accent-primary tabular-nums`
- **Blockquotes**: `italic text-text-secondary border-l-3 border-l-accent-primary bg-bg-secondary`

## Spacing

Use Tailwind's spacing scale. Key layout patterns:
- Between sections (H3): `mb-16`
- Inside cards/panels: `p-5` or `space-y-5`
- Tab bar height: `py-4` (maps to `--tab-bar-height: 4rem`)
- Page horizontal padding: `px-6`
- Max content width: `max-w-[var(--max-content-width)]` (1200px), centered with `mx-auto`

## Component Styling

All components use Tailwind utility classes + shadcn UI primitives. Import `cn` from `@/lib/utils` for conditional class merging.

### Tabbed Navigation (TabbedLayout)

- Background: `bg-bg-secondary`
- Bottom border: `border-b border-border-primary`
- Active tab: `text-accent-primary` + animated indicator via `bg-gradient-tab-indicator`
- Inactive tab: `text-text-tertiary hover:text-text-secondary`
- Glassmorphism on scroll: `glass shadow-lg` utility class
- Tab labels: `text-sm font-medium uppercase tracking-[0.08em]`
- Presentation toggle: shadcn `Button` variant="outline"

### Cards and Panels

- Use shadcn `Card` / `CardContent` components
- Calculator: `border-l-3 border-l-accent-primary bg-gradient-gold-subtle shadow-md`
- Scenario slider: `border-l-3 border-l-accent-secondary bg-gradient-teal-subtle shadow-md`
- Hover lift: framer-motion `whileHover={{ y: -2 }}`

### Interactive Elements (Calculators, Sliders)

- Input fields: shadcn `Input` with `font-mono bg-bg-primary border-border-primary shadow-inset`
- Focus: `focus-visible:border-accent-primary focus-visible:ring-[rgba(212,168,83,0.15)]`
- Labels: shadcn `Label` with `text-xs uppercase tracking-wide text-text-secondary`
- Dividers: shadcn `Separator` with `bg-border-primary`
- Result display: `font-mono text-[length:var(--font-size-hero)] text-accent-primary tabular-nums`
- Range slider: Native `<input type="range">` with `.scenario-slider` CSS class (custom styling in app.css)

### Tables (ComparisonTable)

- Use shadcn `Table`, `TableHeader`, `TableBody`, `TableHead`, `TableRow`, `TableCell`
- Header row: `bg-bg-tertiary text-xs uppercase tracking-wide font-semibold`
- Hover row: inline style `background: var(--color-bg-hover)`
- Filter buttons: shadcn `Button` with variant toggling
- Highlighted column: `text-accent-primary` + subtle gradient background

### Citations (CitationCard)

- Use shadcn `Collapsible` + `Badge`
- Number badge: `font-mono text-xs text-accent-tertiary` in a shadcn Badge variant="outline"
- Left border: `border-l-3 border-l-accent-tertiary`
- Links: `text-accent-tertiary text-xs font-mono bg-bg-tertiary` with hover lift

### Knowledge Vault (KnowledgeVault)

- Use shadcn `Accordion`, `AccordionItem`, `AccordionTrigger`, `AccordionContent`
- Search input: shadcn `Input` with `pl-12 font-mono shadow-inset`
- Expand all: shadcn `Button` variant="outline"
- Section items: AccordionItem with conditional border/shadow classes

### Badges (SectionRenderer)

- Use shadcn `Badge` variant="outline" with semantic color classes
- VERIFIED: `text-success border-[rgba(52,211,153,0.25)]`
- ESTIMATE: `text-warning border-[rgba(251,191,36,0.25)]`
- ILLUSTRATIVE: `text-info border-[rgba(96,165,250,0.25)]`

## Animation Patterns

Use framer-motion for React. Animation tokens are in `src/theme/motion.js`. Keep animations purposeful and restrained.

### Tab Transitions

- Content fade + slide: 300ms, `opacity: 0 → 1`, `y: 8 → 0`
- Use `AnimatePresence` with `mode="wait"` for clean tab switches

### Content Reveals

- Sections animate in on first view with `useInView` and staggered delays (50ms between siblings)
- Cards: `opacity: 0 → 1`, `y: 16 → 0`, 400ms
- Tables: rows stagger in at 30ms intervals
- Numbers/stats: count-up animation over 600ms

### Interactive Feedback

- Calculator results: brief scale pulse (1.0 → 1.02 → 1.0) on value change
- Slider: real-time update, no animation delay
- Hover on cards: framer-motion `whileHover={{ y: -2 }}`
- Button press: framer-motion `whileTap={{ scale: 0.95 }}`

### Presentation Mode (if enabled)

- Auto-advance tabs every 8 seconds
- Progress bar under tabs shows timing
- Section content types in with stagger

## Custom Tailwind Utilities

Defined in `app.css` via `@utility` blocks:

```
bg-gradient-surface       — Surface gradient (secondary → tertiary)
bg-gradient-gold-subtle   — Calculator background tint
bg-gradient-teal-subtle   — Scenario slider background tint
bg-gradient-timeline      — Timeline line gradient (gold → teal → indigo)
bg-gradient-tab-indicator — Tab underline gradient (gold → teal)
bg-gradient-hero-text     — Hero title text gradient
bg-gradient-accent-line   — 60px heading accent line
glass                     — Glassmorphism (bg + backdrop-filter)
scrollbar-none            — Hide scrollbar
```

## Responsive Design

### Breakpoints

```
Mobile: < 768px
Tablet: 768px - 1023px
Desktop: >= 1024px
```

### Mobile Adaptations

- Tabs become a horizontal scrollable row (`overflow-x-auto scrollbar-none`)
- Tables use horizontal scroll
- Calculator inputs stack vertically
- Font sizes reduce: `--font-size-hero: 2.5rem` on mobile
- Page padding: `px-4`

### Desktop Enhancements

- Tabs are full-width with even spacing
- Comparison tables show all columns
- Page padding: `px-6`

## Accessibility

- All color combinations meet WCAG AA contrast ratios (4.5:1 for text, 3:1 for large text)
- Tab navigation is keyboard accessible (arrow keys, Enter, Tab) via `role="tablist"` and `role="tab"`
- Interactive elements have visible focus indicators (`focus-visible:` with accent-primary outline)
- Animations respect `prefers-reduced-motion` — all durations reduced to 0.01ms
- All icons have `aria-hidden="true"` with descriptive text nearby
- Semantic HTML: `<nav>`, `<main>`, `<header>`, `<section>`
- shadcn components include built-in ARIA attributes (Accordion, Collapsible, etc.)

**Note:** This design system is dark-mode only by design. Light mode is not supported. The dark professional aesthetic is core to the brand identity of generated report sites.

## Theme Presets

8 built-in color presets are available in `${CLAUDE_PLUGIN_ROOT}/templates/src/themes/`. Each overrides only semantic color tokens, leaving layout and animation intact. See `${CLAUDE_PLUGIN_ROOT}/skills/design-system/references/registry-guide.md` for details.

## Reference Files

For framer-motion animation tokens, see `${CLAUDE_PLUGIN_ROOT}/templates/src/theme/motion.js`.
For the Tailwind v4 stylesheet with all tokens, see `${CLAUDE_PLUGIN_ROOT}/templates/src/app.css`.
For the full token definitions, see `${CLAUDE_PLUGIN_ROOT}/skills/design-system/references/tokens-reference.md`.
For registry/theme selection, see `${CLAUDE_PLUGIN_ROOT}/skills/design-system/references/registry-guide.md`.
