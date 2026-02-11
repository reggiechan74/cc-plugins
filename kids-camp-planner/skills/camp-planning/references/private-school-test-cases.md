# Private School Test Cases

## Reference: German International School Toronto (GIST) vs TDSB

These real-world calendar comparisons demonstrate the challenges private school families face when planning camp coverage. Use these as test cases for validating the plugin's handling of calendar mismatches.

### Sources
- GIST 2025-2026: Parents Calendar (gistonline.ca)
- GIST 2026-2027: Parents Calendar (gistonline.ca)
- TDSB 2025-2026: Key Dates - School Year Calendar (tdsb.on.ca)

---

## Test Case 1: PA Day Misalignment (2025-2026)

### GIST PA Days
| Date | Day | Notes |
|------|-----|-------|
| Oct 24, 2025 | Friday | Kindergarten only |
| Nov 21, 2025 | Friday | Learning Development Meetings (all grades) |
| Jan 30, 2026 | Friday | All elementary and high school |
| May 29, 2026 | Friday | All kindergarten, elementary, and high school |

### TDSB Elementary PA Days
| Date | Day | Notes |
|------|-----|-------|
| Sep 26, 2025 | Friday | Professional Development |
| Oct 10, 2025 | Friday | Professional Development |
| Nov 14, 2025 | Friday | Parent Teacher Conferences |
| Jan 16, 2026 | Friday | Assessment and Reporting |
| Feb 13, 2026 | Friday | Parent Teacher Conferences |
| Jun 5, 2026 | Friday | Assessment and Reporting |
| Jun 26, 2026 | Friday | Professional Development |

### Alignment Analysis
**Overlapping PA days: ZERO**

Every single GIST PA day falls on a date when TDSB schools are in session. This means:
- Municipal PA day programs (which follow TDSB schedule) will NOT be running
- YMCA/community PA day programs will NOT be running
- Parents must find alternative single-day coverage (drop-in programs, family, work-from-home)

### Expected Plugin Behavior
When processing GIST PA days, the plan-pa-days skill should:
1. Cross-reference against TDSB (nearest public board) calendar
2. Flag ALL GIST PA days as "misaligned" with public board
3. Recommend alternative coverage strategies (not PA day-specific programs)
4. Suggest: before/after school care drop-in, parent WFH, family member, general day camp operators

---

## Test Case 2: Extended March Break (2025-2026)

### Dates
- **GIST March Break**: March 16-27, 2026 (2 full weeks, 10 weekdays)
- **TDSB Mid-Winter Break**: March 16-20, 2026 (1 week, 5 weekdays)

### Overlap Analysis
- **Week 1 (Mar 16-20)**: Both GIST and TDSB are off. All March break camp programs available.
- **Week 2 (Mar 23-27)**: Only GIST is off. TDSB back in session. March break programs NOT running.

### Expected Plugin Behavior
The plan-march-break skill should:
1. Detect the 2-week break from the family profile
2. Split planning into Week 1 (full provider availability) and Week 2 (limited)
3. For Week 2, recommend: general day camp operators with weekly registration, before/after care drop-in, parent coverage
4. Budget separately for each week (Week 2 may cost more per day due to fewer options)
5. Note that Good Friday (Apr 3) and Easter Monday (Apr 6) follow shortly after

---

## Test Case 3: Fall Break (2025-2026 and 2026-2027)

### GIST Fall Breaks
- **2025-2026**: November 3-7, 2025 (full week, Mon-Fri)
- **2026-2027**: October 31 - November 8, 2026 (extended, Sat-Sun inclusive, ~6 weekdays)

### TDSB Fall Break
- **None.** TDSB does not have a fall break.

### Coverage Challenge
This is a full week where:
- No public school is off, so no "fall break camp" programs exist
- Municipal recreation will NOT be running special week-long programs
- This is functionally equivalent to 5 consecutive "misaligned PA days"

### Expected Plugin Behavior
The plugin should:
1. Detect fall break in the school calendar
2. Treat it as a coverage period similar to summer/March break but with different provider landscape
3. Search for: general day camp operators accepting weekly drop-ins, sports clubs with weekly programs, before/after school care that operates regardless of school schedule
4. Consider: parent vacation time, family member coverage, work-from-home arrangements
5. Note this is a recurring annual pattern (GIST has fall break every year)

---

## Test Case 4: Early School Start (2026-2027)

### Dates
- **GIST first day 2026-2027**: August 31, 2026 (Monday)
- **Labour Day 2026**: September 7, 2026
- **TDSB first day**: After Labour Day (estimated September 8, 2026)

### Impact on Summer Coverage
- GIST summer ends August 28, 2026 (last weekday before Aug 31 school start)
- TDSB summer ends September 4, 2026 (last weekday before September 8)
- **GIST summer is ~6 business days shorter** than TDSB summer

### Expected Plugin Behavior
The plan-summer skill should:
1. Use the actual GIST school start date (Aug 31), NOT Labour Day + 1
2. Calculate a shorter summer coverage window
3. Note that the last week of "summer" (Aug 31 - Sep 4) is a normal school week for GIST kids, even though summer camp programs may still be running (since public schools haven't started)
4. Pass `--first-fall-day 2026-08-31` to the summer_dates.py script

---

## Test Case 5: Christmas Break Differences (2025-2026)

### Dates
- **GIST**: Dec 22, 2025 - Jan 2, 2026 (last school day Dec 19, early dismissal 1:15pm)
- **TDSB**: Dec 22, 2025 - Jan 2, 2026

### Analysis
Christmas breaks align in this case. However, note:
- GIST has early dismissal (1:15pm) on Dec 19 with no aftercare
- This creates a half-day coverage need on Dec 19

### Expected Plugin Behavior
- Flag early dismissal days that need afternoon coverage
- Check if before/after care provider operates on early dismissal days

---

## Summary: Private School Planning Challenges

| Challenge | Frequency | Severity | Mitigation |
|-----------|-----------|----------|------------|
| PA day misalignment | 3-4x/year | Medium | WFH, family, drop-in programs |
| Extended March break | Annual | High | Week 2 needs creative solutions |
| Fall break (no public equivalent) | Annual | High | Full week with minimal provider options |
| Early school start | Varies | Low | Shorter summer, fewer camps needed |
| Early dismissal days | 2-3x/year | Low | Afternoon coverage only |

### Key Principle
For private school families, the nearest public school board calendar must always be cross-referenced because **the provider market follows the public board schedule**. Any date where the private school is off but the public board is in session will have significantly fewer childcare options available.
