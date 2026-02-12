# Registry Selection Guide

## Overview

The report-to-web plugin supports three visual style options:

1. **Dark Professional** (default) — The signature gold/teal/indigo dark theme
2. **shadcn Built-in Color Presets** — 7 color themes adapted for dark mode
3. **Community Registries** — Third-party component registries from the shadcn ecosystem

Visual style is selected at generation time (not runtime) because different registries produce different component source files.

## Built-in Color Presets

These presets override only color tokens in `app.css`. Layout, typography, spacing, and animation remain unchanged.

| Preset | Primary | Secondary | Tertiary |
|---|---|---|---|
| Dark Professional | `#d4a853` (gold) | `#2d9e8f` (teal) | `#6366f1` (indigo) |
| Blue | `#3b82f6` (blue) | `#06b6d4` (cyan) | `#8b5cf6` (violet) |
| Green | `#22c55e` (green) | `#14b8a6` (teal) | `#6366f1` (indigo) |
| Orange | `#f97316` (orange) | `#f59e0b` (amber) | `#6366f1` (indigo) |
| Red | `#ef4444` (red) | `#f97316` (orange) | `#8b5cf6` (violet) |
| Rose | `#f43f5e` (rose) | `#ec4899` (pink) | `#8b5cf6` (violet) |
| Violet | `#8b5cf6` (violet) | `#6366f1` (indigo) | `#3b82f6` (blue) |
| Yellow | `#eab308` (yellow) | `#f59e0b` (amber) | `#6366f1` (indigo) |

### Applying a Preset

1. Copy the theme CSS file to the generated project's `src/themes/` directory
2. Import it after `app.css` in `main.jsx`:
   ```jsx
   import './app.css'
   import './themes/blue.css'
   ```
3. The `:root` overrides in the theme file take precedence over app.css defaults

### What Each Preset Overrides

- `--color-accent-primary`, `--color-accent-secondary`, `--color-accent-tertiary`
- `--color-border-accent`
- `--color-primary`, `--color-ring` (shadcn semantic tokens)
- Gradient custom properties (hero text, tab indicator, timeline, subtle backgrounds)
- Shadow glow custom properties

## Community Registries

Community registries provide alternative component implementations with different visual styles — from brutalist to retro to animated.

### Browsing Available Registries

- **Themes gallery**: https://ui.shadcn.com/themes — Preview and customize shadcn's built-in color palettes
- **Registry directory**: https://ui.shadcn.com/registry — Browse community-contributed component registries with live previews
- **Popular registries to explore**:
  - `@neobrutalism` — Bold borders, shadows, and bright colors with a hand-crafted feel
  - `@retroui` — Retro/vintage UI with nostalgic design elements
  - `@magicui` — Animated components with particle effects and transitions
  - `@animata` — Motion-first components with rich entrance/exit animations
  - `@jolly-ui` — Playful, rounded components with soft shadows
  - `@cult-ui` — Opinionated minimal design with sharp typography

Not every registry implements all components. Check the registry's page on ui.shadcn.com for its component list before selecting it.

### Installation Pattern

```bash
# Default shadcn components
npx shadcn@latest add card input label table badge accordion collapsible slider button separator

# Community registry components (replace @registry with actual name)
npx shadcn@latest add @registry/card @registry/input @registry/label @registry/table @registry/badge @registry/accordion @registry/collapsible @registry/slider @registry/button @registry/separator
```

### Required Components

Every generated site needs these 10 shadcn components:

| Component | Used by | Critical? |
|---|---|---|
| `card` | Calculator, ScenarioSlider | Yes |
| `input` | Calculator, KnowledgeVault | Yes |
| `label` | Calculator, ScenarioSlider | Yes |
| `table` | ComparisonTable | Yes |
| `badge` | SectionRenderer, TimelineView, CitationCard | Yes |
| `accordion` | KnowledgeVault | Yes |
| `collapsible` | CitationCard | Yes |
| `slider` | ScenarioSlider (optional, uses native range by default) | No |
| `button` | ComparisonTable, KnowledgeVault, TabbedLayout | Yes |
| `separator` | Calculator, ScenarioSlider | Yes |

### Fallback Strategy

If a community registry doesn't provide a required component:
1. Install the missing component from default shadcn: `npx shadcn@latest add <component>`
2. The default component will be styled by the theme's CSS variables, so it blends in reasonably well
3. Document any missing components in the generated site's README

### Tested Community Registries

Always verify component availability before generation — registries update frequently.

| Registry | Coverage | Notes |
|---|---|---|
| **Default shadcn** | 10/10 | Reference implementation, always works |
| `@neobrutalism` | High | Bold visual style, good component coverage |
| `@magicui` | Partial | Strong on animated/decorative components, may need fallbacks for form primitives |

Check https://ui.shadcn.com/registry for the latest registry listings and their component inventories.

### Testing a New Registry

To verify compatibility with a new community registry:

1. Create a temp directory and scaffold with templates
2. Run `npx shadcn@latest add @registry/card` to test if the registry resolves
3. Install all 10 required components
4. Run `npm run build` — verify no import errors
5. Run `npm run dev` — visually verify components render correctly
6. Check that the registry's styling doesn't conflict with app.css base styles

### Theme Interaction

- Community registries may bring their own color system
- The app.css base styles (typography, spacing, animations) still apply
- If the registry's colors conflict, the user can still apply a built-in preset on top
- The `cn()` utility from `@/lib/utils` ensures Tailwind class merging works correctly with any registry
