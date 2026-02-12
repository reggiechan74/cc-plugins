# Design Token Reference

Token definitions for the dark professional theme, implemented as Tailwind CSS v4 `@theme` tokens in `app.css`. These tokens are the source of truth — all component styling uses Tailwind utility classes that reference these values.

## Tailwind @theme Color Tokens

Defined in the `@theme` block of `app.css`. Use as Tailwind utilities (e.g., `bg-bg-primary`, `text-accent-primary`, `border-border-primary`).

### Backgrounds
```
--color-bg-primary: #0f1117      → bg-bg-primary     Deep space — main background
--color-bg-secondary: #161922    → bg-bg-secondary    Elevated surface — cards, panels
--color-bg-tertiary: #1c1f2e     → bg-bg-tertiary     Recessed areas — code blocks, inputs
--color-bg-hover: #232738        → bg-bg-hover         Hover state for interactive surfaces
```

### Text
```
--color-text-primary: #e8e6e1    → text-text-primary   Warm white — body text
--color-text-secondary: #9a9690  → text-text-secondary  Muted warm — secondary text, labels
--color-text-tertiary: #5e5a55   → text-text-tertiary   Dim — disabled text, timestamps
```

### Accents
```
--color-accent-primary: #d4a853    → text-accent-primary   Amber gold — primary actions
--color-accent-secondary: #2d9e8f  → text-accent-secondary  Teal — secondary interactive
--color-accent-tertiary: #6366f1   → text-accent-tertiary   Indigo — links, tertiary actions
```

### Borders
```
--color-border-primary: #2a2d3a              → border-border-primary
--color-border-accent: rgba(212, 168, 83, 0.2) → border-border-accent
```

### Semantic
```
--color-success: #34d399  → text-success, bg-success
--color-warning: #fbbf24  → text-warning, bg-warning
--color-error: #f87171    → text-error, bg-error
--color-info: #60a5fa     → text-info, bg-info
```

### shadcn Semantic Tokens
```
--color-background: #0f1117
--color-foreground: #e8e6e1
--color-card: #161922
--color-card-foreground: #e8e6e1
--color-primary: #d4a853
--color-primary-foreground: #0f1117
--color-secondary: #1c1f2e
--color-secondary-foreground: #e8e6e1
--color-muted: #1c1f2e
--color-muted-foreground: #9a9690
--color-accent: #232738
--color-accent-foreground: #e8e6e1
--color-destructive: #f87171
--color-border: #2a2d3a
--color-input: #2a2d3a
--color-ring: #d4a853
```

## Shadow / Elevation System

Defined in `@theme`. Use as Tailwind utilities (e.g., `shadow-sm`, `shadow-md`).

```
--shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.25)
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2)
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.35), 0 2px 4px rgba(0, 0, 0, 0.2)
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.4), 0 4px 8px rgba(0, 0, 0, 0.25)
--shadow-xl: 0 16px 48px rgba(0, 0, 0, 0.5), 0 8px 16px rgba(0, 0, 0, 0.3)
--shadow-glow-gold: 0 0 20px rgba(212, 168, 83, 0.15)    → shadow-glow-gold
--shadow-glow-teal: 0 0 20px rgba(45, 158, 143, 0.15)    → shadow-glow-teal
--shadow-glow-indigo: 0 0 20px rgba(99, 102, 241, 0.15)  → shadow-glow-indigo
--shadow-inset: inset 0 2px 4px rgba(0, 0, 0, 0.3)       → shadow-inset
```

**Usage pattern:** Cards at rest use `shadow-sm`, elevate to `shadow-md` on hover. Modals use `shadow-xl`. Input fields use `shadow-inset`.

## Gradient Library

Gradients cannot be defined in `@theme`, so they're CSS custom properties in `:root` with corresponding `@utility` blocks for Tailwind usage.

```css
/* Custom properties */
--gradient-surface         → bg-gradient-surface
--gradient-gold-subtle     → bg-gradient-gold-subtle
--gradient-teal-subtle     → bg-gradient-teal-subtle
--gradient-hero-text       → bg-gradient-hero-text
--gradient-tab-indicator   → bg-gradient-tab-indicator
--gradient-timeline-line   → bg-gradient-timeline
--gradient-noise           → (body::before overlay, not a utility)
```

Additional inline gradient:
```css
bg-gradient-accent-line    → linear-gradient(90deg, accent-primary, accent-secondary)
```

## Glass Effects

CSS custom properties for glassmorphism:
```css
--glass-bg: rgba(22, 25, 34, 0.8)
--glass-border: rgba(42, 45, 58, 0.6)
--glass-blur: blur(12px)
```

Applied via the `glass` utility class defined in app.css. Used for scroll-aware sticky tab bar.

## CSS Transition Tokens

```css
--transition-fast: 0.1s ease
--transition-base: 0.2s ease
--transition-slow: 0.35s ease
```

## Framer-Motion Tokens

Defined in `src/theme/motion.js`. Import as:
```js
import { transitions, animation } from '../theme/motion'
```

```js
transitions.fast       → { duration: 0.1, ease: 'easeOut' }
transitions.base       → { duration: 0.2, ease: 'easeOut' }
transitions.slow       → { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] }
transitions.spring     → { type: 'spring', stiffness: 400, damping: 30 }
transitions.springGentle → { type: 'spring', stiffness: 300, damping: 25 }

animation.tabTransition    → { duration: 0.3 }
animation.contentReveal    → { duration: 0.4 }
animation.staggerChildren  → 0.05
animation.hoverLift        → { y: -2 }
animation.pressScale       → { scale: 0.98 }
animation.fadeInUp.initial  → { opacity: 0, y: 12 }
animation.fadeInUp.animate  → { opacity: 1, y: 0 }
```

## Border Radius Tokens

```
--radius-sm: 4px   → rounded-sm
--radius-md: 8px   → rounded-md
--radius-lg: 12px  → rounded-lg
--radius-xl: 16px  → rounded-xl
```

## Typography Tokens

### Font Stacks
```
--font-display → font-display   "DM Serif Display", Georgia, serif
--font-body    → font-body      "IBM Plex Sans", "Helvetica Neue", sans-serif
--font-mono    → font-mono      "IBM Plex Mono", Consolas, monospace
```

### Hero Font Size
```
--font-size-hero: 3.5rem  → text-[length:var(--font-size-hero)]
```

### Google Fonts Import
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet" />
```

## Layout Tokens

```
--max-content-width: 1200px  → max-w-[var(--max-content-width)]
--tab-bar-height: 4rem       → (used in sticky positioning calculations)
```

## Keyframe Animations

Defined in `@theme`:

```
--animate-pulse-dot      → pulse-dot 2s ease-in-out infinite (timeline dots)
--animate-shimmer        → shimmer 2s linear infinite (loading states)
--animate-float          → float 3s ease-in-out infinite (decorative float)
--animate-accordion-down → accordion-down 0.2s ease-out (shadcn accordion)
--animate-accordion-up   → accordion-up 0.2s ease-out (shadcn accordion)
```

## Responsive Overrides

### Mobile (< 768px)
```css
--font-size-hero: 2.5rem
```

### Reduced Motion
All animations and transitions set to 0.01ms via `@media (prefers-reduced-motion: reduce)`.

## Contrast Ratios

All primary text combinations meet WCAG AA (4.5:1 minimum):

| Foreground | Background | Ratio | Pass |
|---|---|---|---|
| text-primary (#e8e6e1) | bg-primary (#0f1117) | 14.2:1 | AAA |
| text-secondary (#9a9690) | bg-primary (#0f1117) | 6.8:1 | AA |
| accent-primary (#d4a853) | bg-primary (#0f1117) | 8.4:1 | AAA |
| accent-secondary (#2d9e8f) | bg-primary (#0f1117) | 6.2:1 | AA |
| accent-tertiary (#6366f1) | bg-primary (#0f1117) | 4.6:1 | AA |
| text-primary (#e8e6e1) | bg-secondary (#161922) | 12.5:1 | AAA |
| text-primary (#e8e6e1) | bg-tertiary (#1c1f2e) | 10.8:1 | AAA |
