# Example: Financial Calculation Verification

## Scenario

User requests: "Create a compound interest calculator for investment portfolio"

## Execution Trace

### Phase 1: Planning

```
EXECUTION PLAN

Scope: Compound interest calculation function
Files: src/finance/compound-interest.ts (new file)

SUCCESS CRITERIA:
✓ Uses Decimal type (not float) for precision
✓ Applies banker's rounding (round half to even)
✓ Logs all calculations to audit trail
✓ Handles edge cases (negative rates, zero principal)
✓ Returns results to 2 decimal places
✓ Unit tests with known values pass

CRITICS:
- Code Critic: Syntax, logic, edge cases, tests
- Security Critic: Input validation (not financial exposure)
- Domain Critic (Financial): Precision, rounding, audit, compliance

RETRY BUDGET: 6
```

### Phase 2: Execution - Iteration 1

Code Critic: **VETO**

```
❌ FLOATING POINT PRECISION ERROR

Code generated:
  const result = principal * Math.pow(1 + rate, periods);

Issue: Using JavaScript float (Number type) causes precision errors
Example: 1000.00 * 1.05^10 = 1628.894626777441 (incorrect)
Expected: 1628.89 (with proper decimal handling)

Fix required: Import and use Decimal.js library
```

### Phase 3: Execution - Iteration 2

Security Critic: **APPROVE** ✓
Code Critic: **APPROVE** ✓
Domain Critic: **VETO**

```
❌ INCORRECT ROUNDING METHOD

Code generated:
  return result.toFixed(2); // Standard JavaScript rounding

Issue: Uses "round half up" instead of banker's rounding
Example: 2.5 rounds to 3, should round to 2 (nearest even)
Regulation: Financial calculations must use banker's rounding (IEEE 754)

Fix required: Implement banker's rounding explicitly
```

### Phase 4: Execution - Iteration 3

Security Critic: **APPROVE** ✓
Code Critic: **APPROVE** ✓
Domain Critic: **VETO**

```
❌ MISSING AUDIT TRAIL

Code generated:
  return roundedResult; // Returns value without logging

Issue: No audit trail of calculation
Requirement: All financial operations must be logged
Compliance: SOX requires audit trail for financial calculations

Fix required: Log inputs, calculation steps, output to audit table
```

### Phase 5: Execution - Iteration 4

All Critics: **UNANIMOUS APPROVAL** ✓

```
✓ Code Critic: All checks passed
  - Decimal.js used correctly
  - Edge cases handled (negative rate → error, zero principal → zero)
  - Unit tests pass (10/10)
  - Code coverage: 100%

✓ Security Critic: Input validation present
  - Principal range validated (positive number)
  - Rate range validated (-100% to +1000%)
  - Periods validated (positive integer)

✓ Domain Critic (Financial): All compliance requirements met
  - Decimal precision maintained throughout
  - Banker's rounding applied correctly
  - Audit trail logs: user_id, timestamp, inputs, output
  - Results formatted to 2 decimal places
```

## Final Implementation

```typescript
import Decimal from 'decimal.js';
import { auditLog } from './audit';

interface CompoundInterestParams {
  principal: number;
  annualRate: number;
  periodsPerYear: number;
  years: number;
}

export function calculateCompoundInterest(
  params: CompoundInterestParams,
  userId: string
): string {
  // Validation
  if (params.principal <= 0) throw new Error('Principal must be positive');
  if (params.annualRate < -1 || params.annualRate > 10) {
    throw new Error('Rate must be between -100% and +1000%');
  }
  if (params.periodsPerYear <= 0 || !Number.isInteger(params.periodsPerYear)) {
    throw new Error('Periods must be positive integer');
  }
  if (params.years <= 0) throw new Error('Years must be positive');

  // Use Decimal for precision
  const principal = new Decimal(params.principal);
  const ratePerPeriod = new Decimal(params.annualRate).div(params.periodsPerYear);
  const totalPeriods = params.periodsPerYear * params.years;

  // Calculate compound interest
  const growthFactor = ratePerPeriod.plus(1);
  const result = principal.times(growthFactor.pow(totalPeriods));

  // Banker's rounding to 2 decimal places
  const rounded = result.toDecimalPlaces(2, Decimal.ROUND_HALF_EVEN);

  // Audit trail
  auditLog.create({
    user_id: userId,
    operation: 'compound_interest',
    inputs: params,
    output: rounded.toString(),
    timestamp: new Date()
  });

  return rounded.toString();
}
```

## Summary

**Iterations**: 4 (budget: 2 remaining)
**Time**: 3.8 minutes
**Cost**: +41% tokens
**Result**: 90% accuracy (caught 3 critical errors before user exposure)

### Errors Caught

1. **Floating-point precision** (Code Critic) - Would cause incorrect results
2. **Wrong rounding method** (Domain Critic) - Regulatory non-compliance
3. **Missing audit trail** (Domain Critic) - SOX violation

### Comparison with Single-Agent

Single-agent baseline (10 trials):
- 6 trials: Correct $40 discrepancy identification
- 3 trials: Incorrect discrepancy amounts
- 1 trial: "No discrepancy found"
- All trials: High confidence (no error signal)
- Time: 1-2 minutes

**Multi-agent saved**: 3 production errors that would require manual correction and potential compliance penalties.
