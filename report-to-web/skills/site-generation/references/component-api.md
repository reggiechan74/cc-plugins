# Component API Reference

All components use Tailwind CSS utility classes + shadcn/ui primitives. Import `cn` from `@/lib/utils` for conditional class merging. Import animation tokens from `../theme/motion`.

## TabbedLayout

Main navigation shell with animated tab indicator, glassmorphism header, and presentation mode. Uses shadcn `Button` for the presentation toggle.

```jsx
import { useState, useCallback } from 'react'

const [activeTab, setActiveTab] = useState(0)
const handleTabChange = useCallback((index) => setActiveTab(index), [])

<TabbedLayout
  title="Site Title"
  subtitle="Optional subtitle text"
  tabs={[
    { id: 'overview', label: 'Overview', content: <ReactNode /> },
    { id: 'details', label: 'Details', content: <ReactNode /> },
  ]}
  activeTab={activeTab}
  onTabChange={handleTabChange}
  isPresenting={false}
  setIsPresenting={setIsPresenting}
  progress={0}
/>
```

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | yes | Site title in the header |
| subtitle | string | no | Subtitle below the title |
| tabs | Tab[] | yes | Array of tab definitions |
| activeTab | number | yes | Currently active tab index (lifted state) |
| onTabChange | function | yes | `(index: number) => void` callback |
| isPresenting | boolean | no | Whether auto-advance is active |
| setIsPresenting | function | no | Toggle for presentation mode |
| progress | number | no | 0-100 progress for auto-advance timer |

Tab: `{ id: string, label: string, content: ReactNode }`

**shadcn components:** Button (presentation toggle)

**Features:**
- Animated tab indicator slides between tabs with spring physics (`layoutId="tab-indicator"`)
- Scroll-aware sticky header with `glass` utility on scroll
- Presentation mode toggle button (shadcn Button variant="outline") + progress bar
- Tab hover states with conditional Tailwind classes via `cn()`
- Hero title uses `bg-gradient-hero-text` with `bg-clip-text text-transparent`

## Calculator

Interactive formula calculator with input fields and live results. Uses shadcn Card, Input, Label, Separator.

```jsx
<Calculator
  title="Property Tax Calculator"
  formulaDisplay="Tax = Assessment x Rate"
  inputs={[
    { id: 'assessment', label: 'Assessed Value', defaultValue: 500000, prefix: '$' },
    { id: 'rate', label: 'Tax Rate', defaultValue: 0.754087, suffix: '%', step: 0.001 },
  ]}
  calculate={(values) => ({
    result: {
      label: 'Annual Property Tax',
      value: values.assessment * (values.rate / 100),
      formatted: `$${(values.assessment * (values.rate / 100)).toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    },
    breakdown: [
      { label: 'Municipal Tax', value: 2963.27, formatted: '$2,963.27' },
    ],
  })}
/>
```

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | yes | Calculator heading |
| formulaDisplay | string | no | Formula shown above inputs |
| inputs | Input[] | yes | Input field definitions |
| calculate | function | yes | `(values) => { result, breakdown? }` |

Input: `{ id, label, defaultValue, prefix?, suffix?, step? }`
Result: `{ label, value, formatted }`
Breakdown: `Array<{ label, value, formatted }>`

**shadcn components:** Card, CardContent, Input, Label, Separator

**Features:** Inputs use shadcn Input with `font-mono bg-bg-primary shadow-inset`. Result animates in with `transitions.spring`. Container uses `bg-gradient-gold-subtle` Card with gold left border.

## ComparisonTable

Interactive comparison table with column filtering and highlighting. Uses shadcn Table and Button.

```jsx
<ComparisonTable
  title="Appraiser Comparison"
  headers={['Dimension', 'Conventional', 'Assessment', 'Tax Appeal']}
  rows={[
    { dimension: 'Purpose', values: ['Market value', 'Current value', 'Challenge assessment'] },
  ]}
  highlightColumn={2}
  filters={true}
/>
```

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | yes | Table heading |
| headers | string[] | yes | Column headers (first is dimension column) |
| rows | Row[] | yes | Row data |
| highlightColumn | number | no | 0-based column index to highlight |
| filters | boolean | no | Show column toggle buttons |

Row: `{ dimension: string, values: string[] }`

**shadcn components:** Table, TableHeader, TableBody, TableHead, TableRow, TableCell, Button

**Features:** `bg-gradient-surface` header, sticky table header, filter Buttons with `whileTap` scale, highlighted column uses `text-accent-primary` + gradient background. Staggered row animation.

## TimelineView

Vertical timeline with expandable events and gradient line. Uses shadcn Badge.

```jsx
<TimelineView
  title="Assessment Cycle History"
  events={[
    { date: '2016', title: 'Valuation Date Set', status: 'completed', description: 'Details...' },
    { date: '2025', title: 'Still Frozen', status: 'active', badge: 'Year 10', description: '...' },
  ]}
/>
```

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| title | string | no | Timeline heading |
| events | Event[] | yes | Timeline events |

Event: `{ date, title, description?, status?: 'completed'|'active'|'warning'|'pending', badge?: string }`

**shadcn components:** Badge (for status pills)

**Features:** Timeline line uses `bg-gradient-timeline` (gold -> teal -> indigo). Active-status dots have CSS `pulse-dot` animation. Badges use `Badge variant="outline"` with status-colored classes. Expanded content has `bg-gradient-surface` + `shadow-sm`.

## CitationCard / InlineCitation

Expandable citation cards using shadcn Collapsible + Badge. Chevron rotation preserved.

```jsx
<CitationCard
  number={1}
  title="Assessment Act, R.S.O. 1990, c. A.31"
  content="Defines current value as the amount of money..."
  links={[
    { label: 'ontario.ca/laws/statute/90a31', url: 'https://www.ontario.ca/laws/statute/90a31' },
  ]}
/>
```

**shadcn components:** Collapsible, CollapsibleTrigger, CollapsibleContent, Badge

**Features:** Number badge is pill-shaped Badge with indigo border. Card transitions `shadow-xs` → `shadow-md` when expanded. Chevron rotates via `motion.div`. Source links use `motion.a` with hover lift.

## KnowledgeVault

Searchable full-text report content using shadcn Accordion, Input, Button.

```jsx
<KnowledgeVault
  sections={[
    { id: 'section-1', title: 'Section Title', content: 'Full text content...' },
  ]}
/>
```

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| sections | Section[] | yes | Report sections |

Section: `{ id: string, title: string, content: string }`

**shadcn components:** Accordion, AccordionItem, AccordionTrigger, AccordionContent, Input, Button

**Features:** Search Input with icon overlay and `shadow-inset`. Empty state with styled icon. AccordionItem cards elevate on expand with conditional `border-border-accent shadow-md` classes. Expand-all Button variant="outline".

## ScenarioSlider

What-if scenario explorer with sliders and live results. Uses shadcn Card, Label, Separator.

```jsx
<ScenarioSlider
  title="What If Reassessment Happened?"
  description="Explore how different valuation dates affect your property tax"
  variables={[
    { id: 'newValue', label: 'Updated Assessment', min: 300000, max: 1200000, step: 10000, defaultValue: 750000, format: (v) => `$${v.toLocaleString()}` },
  ]}
  calculate={(values) => [
    { label: 'New Tax', formatted: `$${(values.newValue * 0.754 / 100).toFixed(2)}`, color: 'var(--color-accent-primary)' },
  ]}
/>
```

**shadcn components:** Card, CardContent, Label, Separator

**Features:** Container uses `bg-gradient-teal-subtle` Card with teal left border. Slider uses native `<input type="range">` with `.scenario-slider` CSS class (custom thumb/track styling in app.css). Result cards have `bg-gradient-surface shadow-sm` with hover lift. Slider value display animates color teal → gold.

## SectionRenderer

Renders markdown content with scroll-triggered reveal animation and gradient heading accent. Uses shadcn Badge.

```jsx
<SectionRenderer
  id="section-1"
  title="Section Title"
  content="Markdown content here..."
  level={3}
  index={0}
>
  <Calculator ... />  {/* Optional interactive element after content */}
</SectionRenderer>
```

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| id | string | yes | Section anchor ID |
| title | string | no | Section heading text |
| content | string | yes | Markdown content |
| level | number | no | Heading level (default 3) |
| index | number | no | Section index — odd-numbered sections get `bg-gradient-gold-subtle` background |
| children | ReactNode | no | Interactive elements after content |

**shadcn components:** Badge (for VERIFIED/ESTIMATE/ILLUSTRATIVE markers)

**Features:** Heading accent is a 60px `bg-gradient-accent-line`. Badges use `Badge variant="outline"` with semantic color classes. Alternating sections use `bg-gradient-gold-subtle`. Scroll-triggered reveal via framer-motion `useInView`.
