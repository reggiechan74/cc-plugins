---
name: Budget Optimization
description: This skill should be used when the user asks to "create a camp budget", "generate budget spreadsheet", "calculate camp costs", "compare camp prices", "optimize camp spending", "track camp expenses", "how much will camps cost", "budget for summer camps", "camp cost breakdown", or needs help analyzing, comparing, or managing camp-related expenses across children and time periods. Provides budget calculation tools and cost optimization strategies for Ontario families.
version: 0.1.0
---

# Budget Optimization

## Overview

Calculate, compare, and optimize camp costs across children, time periods, and providers. Generate budget summaries as markdown tables (default) or Excel spreadsheets (requires anthropic spreadsheet plugin). Apply Ontario-specific cost-saving strategies including tax deductions, subsidies, and discount timing.

## Budget Generation Workflow

### Step 1: Gather Cost Data

Read the family profile from `.claude/kids-camp-planner.local.md` for budget constraints. Collect per-provider costs from `camp-research/providers/*.md` files if they exist. For each camp option, ensure the following cost components are captured:

| Component | Example |
|-----------|---------|
| Base weekly fee | $300/week |
| Before-care (if needed) | $50/week |
| After-care (if needed) | $50/week |
| Lunch program (if not packing) | $35/week |
| Materials/equipment fee | $25 one-time |
| Registration fee | $50 one-time |
| Sibling discount | -10% second child |
| Early-bird discount | -$25/week if registered by deadline |
| Multi-week discount | -5% for 4+ weeks |

### Step 2: Calculate Using Budget Script

Run the budget calculator script to compute totals:

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

The script supports multiple scenarios for comparison. Pass `--format csv` to generate CSV output or `--format markdown` for a markdown table.

For complex multi-provider budgets, prepare a JSON input file and pass it with `--input budget-input.json`. See the script's `--help` for the JSON schema.

### Step 3: Generate Budget Document

Create the budget file at the appropriate location:
- Summer: `camp-research/summer-YYYY/budget.md`
- March break: `camp-research/march-break-YYYY/budget.md`
- PA days: `camp-research/pa-days-YYYY-YYYY/budget.md`

**Markdown budget format (default):**

```markdown
# Camp Budget - Summer 2025

## Summary
| | Child 1 | Child 2 | Total |
|---|---------|---------|-------|
| Camp fees | $2,400 | $2,160 | $4,560 |
| Before/after care | $800 | $800 | $1,600 |
| Lunch | $0 | $0 | $0 |
| Registration | $50 | $50 | $100 |
| **Subtotal** | **$3,250** | **$3,010** | **$6,260** |
| Sibling discount | - | -$216 | -$216 |
| Early bird discount | -$200 | -$200 | -$400 |
| **Total** | **$3,050** | **$2,594** | **$5,644** |

## Tax Recovery Estimate
- Child care deduction (Line 21400): ~$X estimated tax savings
- Ontario Child Care Tax Credit: ~$X estimated

## Weekly Breakdown
[Week-by-week table with provider, child, and cost per week]

## Budget vs. Target
- Budget limit: $5,000
- Projected spend: $5,644
- Over/under: $644 over budget
- Recommendations: [suggestions to reduce costs]
```

**Excel format:** If the user requests Excel output, inform them that generating `.xlsx` files requires the Anthropic xlsx skill (https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md). Offer markdown + CSV as alternatives, or proceed with Excel if the skill is installed.

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

- **`scripts/budget_calculator.py`** - Calculate camp costs across multiple children, providers, and weeks with discount application and tax estimates
