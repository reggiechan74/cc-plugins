# Parsing Example: Research Report to Data Structure

This worked example shows how a markdown research report maps to the `reportData.js` and `interactiveConfig.js` data structures, and how the site-builder agent scaffolds the project with Tailwind + shadcn.

## Input: Sample Report Structure

```markdown
# Ontario Property Tax Valuation

**Date:** 2026-02-10
**Prepared by:** Research Command

## Executive Summary
Ontario property tax valuation is governed by the Assessment Act...

## Part 1: How Ontario Property Tax Valuation Works

### 1.1 The Legislative Framework
Property assessment in Ontario is governed by the Assessment Act...

### 1.2 From Assessment to Tax Bill
> **Property Tax = CVA × (Municipal Rate + Education Rate + Special Levies)**

| Component | Rate | Amount |
|-----------|------|--------|
| Municipal | 0.592653% | $2,963.27 |
| Education | 0.153000% | $765.00 |
| **Total** | **0.754087%** | **$3,770.44** |

### 1.3 Valuation Dates and the Reassessment Freeze

| Cycle | Valuation Date | Status |
|-------|---------------|--------|
| 2017–2020 | January 1, 2016 | Completed |
| 2021–2024 | Should have been Jan 1, 2020 | **Postponed** |
| 2025–2026 | Still Jan 1, 2016 | **Frozen** |

## Part 2: Three Types of Appraisers Compared

### 2.1 Comprehensive Comparison Table

| Dimension | Conventional | MPAC Assessment | Tax Appeal |
|---|---|---|---|
| Purpose | Market value | Current value | Challenge assessment |
| Method | Individual | Mass appraisal | Individual |

## Sources Consulted

[^1]: Assessment Act, R.S.O. 1990, c. A.31; https://www.ontario.ca/laws/statute/90a31
[^2]: MPAC Fact Sheet; https://www.mpac.ca/en/News/FactSheet/MPACFactSheet
```

## Generation Workflow

### 1. User selects visual style

User chooses "Dark Professional" (default) when prompted in Step 2 of the generate command.

### 2. Scaffold and install

```bash
# Copy templates to output directory
# Then install shadcn UI components:
npx shadcn@latest add card input label table badge accordion collapsible slider button separator

# No theme CSS import needed for default dark professional
```

### 3. main.jsx

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './app.css'
// For non-default themes, add: import './themes/blue.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

## Output: reportData.js

```js
export const reportData = {
  meta: {
    title: 'Ontario Property Tax Valuation',
    date: '2026-02-10',
    author: 'Research Command',
    query: null,
  },
  tabs: [
    {
      id: 'overview',
      label: 'Overview',
      sections: [
        {
          id: 'executive-summary',
          heading: 'Executive Summary',
          content: 'Ontario property tax valuation is governed by the Assessment Act...',
          interactive: [],
        },
      ],
    },
    {
      id: 'part-1',
      label: 'How It Works',
      sections: [
        {
          id: 'legislative-framework',
          heading: '1.1 The Legislative Framework',
          content: 'Property assessment in Ontario is governed by the Assessment Act...',
          interactive: [],
        },
        {
          id: 'assessment-to-tax-bill',
          heading: '1.2 From Assessment to Tax Bill',
          content: '> **Property Tax = CVA × (Municipal Rate + Education Rate + Special Levies)**\n\n| Component | Rate | Amount |...',
          interactive: ['calculator-tax'],  // AI-detected: formula + numerical table
        },
        {
          id: 'valuation-dates',
          heading: '1.3 Valuation Dates and the Reassessment Freeze',
          content: '| Cycle | Valuation Date | Status |...',
          interactive: ['timeline-reassessment'],  // AI-detected: chronological data with status
        },
      ],
    },
    {
      id: 'part-2',
      label: 'Appraisers Compared',
      sections: [
        {
          id: 'comparison-table',
          heading: '2.1 Comprehensive Comparison Table',
          content: '| Dimension | Conventional | MPAC Assessment | Tax Appeal |...',
          interactive: ['comparison-appraisers'],  // AI-detected: 3+ comparison columns
        },
      ],
    },
    {
      id: 'vault',
      label: 'Knowledge Vault',
      sections: [], // All sections rendered via KnowledgeVault component
    },
    {
      id: 'sources',
      label: 'Sources',
      sections: [], // Citations rendered via CitationCard components
    },
  ],
  citations: [
    {
      number: 1,
      title: 'Assessment Act, R.S.O. 1990, c. A.31',
      content: 'Defines current value standard for Ontario property assessment.',
      links: [
        { label: 'ontario.ca/laws/statute/90a31', url: 'https://www.ontario.ca/laws/statute/90a31' },
      ],
    },
    {
      number: 2,
      title: 'MPAC Fact Sheet',
      content: 'Key statistics about MPAC operations and coverage.',
      links: [
        { label: 'mpac.ca/en/News/FactSheet', url: 'https://www.mpac.ca/en/News/FactSheet/MPACFactSheet' },
      ],
    },
  ],
  externalLinks: [
    { label: 'Assessment Act', url: 'https://www.ontario.ca/laws/statute/90a31', category: 'legislation' },
    { label: 'MPAC Fact Sheet', url: 'https://www.mpac.ca/en/News/FactSheet/MPACFactSheet', category: 'official' },
  ],
}
```

## Output: interactiveConfig.js

```js
export const interactives = [
  {
    id: 'calculator-tax',
    type: 'calculator',
    tabId: 'part-1',
    sectionId: 'assessment-to-tax-bill',
    config: {
      title: 'Property Tax Calculator',
      formulaDisplay: 'Tax = Assessment × (Municipal + Education + Special)',
      inputs: [
        { id: 'assessment', label: 'Assessed Value (CVA)', defaultValue: 500000, prefix: '$' },
        { id: 'municipalRate', label: 'Municipal Rate', defaultValue: 0.592653, suffix: '%', step: 0.001 },
        { id: 'educationRate', label: 'Education Rate', defaultValue: 0.153, suffix: '%', step: 0.001 },
        { id: 'specialRate', label: 'Special Levies', defaultValue: 0.008434, suffix: '%', step: 0.001 },
      ],
      // calculate function defined in the page component
    },
  },
  {
    id: 'timeline-reassessment',
    type: 'timeline',
    tabId: 'part-1',
    sectionId: 'valuation-dates',
    config: {
      title: 'Ontario Assessment Cycle History',
      events: [
        { date: '2017–2020', title: 'Assessment Cycle (Jan 1, 2016)', status: 'completed', badge: 'Completed' },
        { date: '2021–2024', title: 'Reassessment Postponed', status: 'warning', badge: 'COVID-19', description: 'Should have used Jan 1, 2020 values. Postponed due to COVID-19, then extended.' },
        { date: '2025–2026', title: 'Assessment Frozen at 2016 Values', status: 'active', badge: 'Year 10', description: 'Ontario is now in year 10 of what was originally a four-year cycle.' },
      ],
    },
  },
  {
    id: 'comparison-appraisers',
    type: 'comparison',
    tabId: 'part-2',
    sectionId: 'comparison-table',
    config: {
      title: 'Appraiser Comparison',
      headers: ['Dimension', 'Conventional', 'MPAC Assessment', 'Tax Appeal'],
      rows: [
        { dimension: 'Purpose', values: ['Market value for client', 'Current value for taxation', 'Challenge assessment at ARB'] },
        { dimension: 'Method', values: ['Individual appraisal', 'Mass appraisal', 'Individual appraisal'] },
      ],
      highlightColumn: null,
      filters: true,
    },
  },
]
```

## Example Page Component (Tailwind + shadcn)

```jsx
// src/pages/HowItWorksTab.jsx
import SectionRenderer from '../components/SectionRenderer'
import Calculator from '../components/Calculator'
import TimelineView from '../components/TimelineView'
import { reportData } from '../data/reportData'
import { interactives } from '../data/interactiveConfig'

export default function HowItWorksTab() {
  const tab = reportData.tabs.find(t => t.id === 'part-1')
  const calcConfig = interactives.find(i => i.id === 'calculator-tax').config
  const timelineConfig = interactives.find(i => i.id === 'timeline-reassessment').config

  return (
    <div>
      {tab.sections.map((section, index) => (
        <SectionRenderer
          key={section.id}
          id={section.id}
          title={section.heading}
          content={section.content}
          level={3}
          index={index}
        >
          {section.id === 'assessment-to-tax-bill' && (
            <Calculator
              title={calcConfig.title}
              formulaDisplay={calcConfig.formulaDisplay}
              inputs={calcConfig.inputs}
              calculate={(values) => {
                const totalRate = values.municipalRate + values.educationRate + values.specialRate
                const tax = values.assessment * (totalRate / 100)
                return {
                  result: { label: 'Annual Property Tax', formatted: `$${tax.toLocaleString('en-CA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` },
                  breakdown: [
                    { label: 'Municipal', formatted: `$${(values.assessment * values.municipalRate / 100).toFixed(2)}` },
                    { label: 'Education', formatted: `$${(values.assessment * values.educationRate / 100).toFixed(2)}` },
                  ],
                }
              }}
            />
          )}
          {section.id === 'valuation-dates' && (
            <TimelineView
              title={timelineConfig.title}
              events={timelineConfig.events}
            />
          )}
        </SectionRenderer>
      ))}
    </div>
  )
}
```

## Detection Rules Applied

1. **Calculator** detected from:
   - Formula in blockquote: `Tax = CVA × (Municipal Rate + Education Rate + Special Levies)`
   - Numerical table with `$` values and `%` rates
   - "Total" summary row

2. **Timeline** detected from:
   - Date ranges in first column (`2017–2020`, `2021–2024`)
   - Status column with progression (Completed → Postponed → Frozen)
   - Chronological ordering

3. **ComparisonTable** detected from:
   - 4 columns (dimension + 3 comparison subjects)
   - First column contains shared attributes
   - Remaining columns compare same dimensions across different entities
