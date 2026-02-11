---
name: Budget Optimization
description: This skill should be used when the user asks to "create a camp budget", "generate budget spreadsheet", "calculate camp costs", "compare camp prices", "optimize camp spending", "track camp expenses", "how much will camps cost", "budget for summer camps", "camp cost breakdown", or needs help analyzing, comparing, or managing camp-related expenses across children and time periods. Provides budget calculation tools and cost optimization strategies for Ontario families.
version: 0.1.0
---

# Budget Optimization

## Overview

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`.

Calculate, compare, and optimize camp costs across children, time periods, and providers. Generate budget summaries as markdown tables (default) or Excel spreadsheets. Apply Ontario-specific cost-saving strategies including tax deductions, subsidies, and discount timing.

## Budget Generation Workflow

### Step 1: Gather Cost Data

Read the family profile from `<research_dir>/family-profile.md` for budget constraints. Collect per-provider costs from `<research_dir>/providers/*.md` files if they exist. For each camp option, ensure the following cost components are captured:

| Component | Weekly Rate | Daily Rate |
|-----------|-------------|------------|
| Base camp fee | $300/week | $60/day |
| Before-care (if needed) | $50/week | $10/day |
| After-care (if needed) | $50/week | $10/day |
| Lunch program (if not packing) | $35/week | $7/day |
| Materials/equipment fee | $25 one-time | $25 one-time |
| Registration fee | $50 one-time | $50 one-time |
| Sibling discount | -10% second child | -10% second child |
| Early-bird discount | -$25/week if registered by deadline | -$25/week equivalent |
| Multi-week discount | -5% for 4+ weeks | -5% for 20+ days |

### Step 2: Calculate Using Budget Script

Run the budget calculator script to compute totals:

**Weekly rate mode:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/budget-optimization/scripts/budget_calculator.py \
  --kids 2 \
  --weeks 8 \
  --base-cost 300 \
  --before-care 50 \
  --after-care 50 \
  --lunch 35 \
  --sibling-discount 10 \
  --format markdown
```

**Daily rate mode:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/budget-optimization/scripts/budget_calculator.py \
  --kids 2 \
  --days 40 \
  --daily-rate 60 \
  --before-care-daily 10 \
  --after-care-daily 10 \
  --lunch-daily 7 \
  --sibling-discount 10 \
  --format markdown
```

The script supports both weekly and daily rate calculations. Use `--days` and `--daily-rate` for day-level pricing (takes precedence over `--weeks`/`--base-cost` if both provided). Pass `--format csv` to generate CSV output or `--format markdown` for a markdown table.

For complex multi-provider budgets, prepare a JSON input file and pass it with `--input budget-input.json`. The JSON format supports both `"weeks"` and `"days"` arrays (days takes precedence). See the script's `--help` for the JSON schema.

### Step 3: Generate Budget Document

Create the budget file at the appropriate location:
- Summer: `<research_dir>/summer-YYYY/budget.md`
- March break: `<research_dir>/march-break-YYYY/budget.md`
- PA days: `<research_dir>/pa-days-YYYY-YYYY/budget.md`

**Markdown budget format (default):**

```markdown
# Camp Budget - Summer 2025

## Summary
| | Child 1 | Child 2 | Total |
|---|---------|---------|-------|
| Camp fees | $2,350 | $2,200 | $4,550 |
| Before/after care | $800 | $800 | $1,600 |
| Lunch | $280 | $280 | $560 |
| Registration | $50 | $50 | $100 |
| **Subtotal** | **$3,480** | **$3,330** | **$6,810** |
| Sibling discount | - | -$240 | -$240 |
| Early bird discount | -$200 | -$200 | -$400 |
| **Total** | **$3,280** | **$2,890** | **$6,170** |

## Cost by Camp Provider
| Provider | Child 1 | Child 2 | Total |
|----------|---------|---------|-------|
| YMCA Cedar Glen | $1,800 | $1,800 | $3,600 |
| City of Toronto | $200 | $400 | $600 |
| Science Camp TO | $350 | $0 | $350 |
| **Total Camp Fees** | **$2,350** | **$2,200** | **$4,550** |

## Tax Recovery Estimate
- Child care deduction (Line 21400): ~$X estimated tax savings
- Ontario Child Care Tax Credit: ~$X estimated

## Weekly Breakdown
[Week-by-week table with provider, child, and cost per week]

## Budget vs. Target
- Budget limit: $7,000
- Projected spend: $6,170
- Over/under: $830 under budget
- Recommendations: [suggestions to reduce costs]
```

**Excel format:** See `${CLAUDE_PLUGIN_ROOT}/examples/sample-budget.xlsx` for the reference Excel budget template. The spreadsheet has four tabs:
- **Provider Comparison**: Camp rates including both daily and weekly columns with Total/Day and Total/Week formulas. Supports per-period rate columns (Summer, PA Day, Break) — when PA Day or Break columns are empty, summer rates are used as fallback.
- **Daily Schedule**: Day-by-day assignments (source of truth) with VLOOKUP formulas referencing Provider Comparison. Dynamic column layout supports 1-4 children: 3 prefix cols + 6 cols per child + 1 daily total.
- **Weekly Schedule**: Derived from Daily Schedule via SUMIF formulas
- **Budget Summary**: All cost totals derived from Daily Schedule via SUM/SUMIF formulas

When generating Excel output, use openpyxl with formulas rather than hardcoded values. The Daily Schedule tab is the primary input surface — users only fill in the date, week number, and camp name per child per day.

### Step 4: Provide Optimization Recommendations

When the budget exceeds constraints, suggest cost reductions in priority order:

1. **Switch to municipal programs** for some weeks (typically 30-40% cheaper)
2. **Apply early-bird discounts** if registration deadlines haven't passed
3. **Use multi-week discounts** by consolidating weeks with one provider
4. **Pack lunches** instead of buying ($25-50/week savings per child)
5. **Reduce before/after care** on days when parent schedules allow
6. **Mix half-day and full-day** programs for younger children
7. **Check subsidy eligibility** through municipal children's services
8. **Stagger specialty camps** - alternate with lower-cost general camps

## Cost-Saving Strategies

### Tax Deductions (Canada)

Camp fees qualify as child care expenses on Line 21400:
- Under 7: up to $8,000/year deductible
- Ages 7-16: up to $5,000/year deductible
- Must be claimed by the lower-income spouse
- Keep all receipts; request tax receipts from providers
- Effective tax savings: typically 20-30% of eligible amount depending on marginal rate

### Ontario-Specific Programs

- **Municipal fee subsidies**: Income-tested, apply through local children's services
- **Ontario Child Care Tax Credit**: Provincial credit, income-tested
- **CWELCC**: Some licensed camp programs may qualify for reduced fees

### Timing Strategies

- Register in January/February for best early-bird pricing
- Municipal programs often have lowest cost-per-day
- March break programs at community centres are significantly cheaper than private
- PA day drop-in programs exist at many community centres

## Additional Resources

### Scripts

- **`scripts/budget_calculator.py`** - Calculate camp costs across multiple children, providers, and weeks/days with discount application and tax estimates. Supports both `--base-cost`/`--weeks` (weekly) and `--daily-rate`/`--days` (daily) modes.
