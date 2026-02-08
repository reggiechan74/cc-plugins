---
name: Camp Planning Knowledge
description: This skill should be used when the user asks to "evaluate a camp", "compare camps", "what to look for in a camp", "is this camp good", "camp safety standards", "camp certifications", "choosing a day camp", "questions to ask a camp", or needs guidance on assessing camp quality, safety, program structure, or suitability for their children. Provides Ontario-focused camp evaluation knowledge and best practices.
version: 0.1.0
---

# Camp Planning Knowledge

## Overview

Evaluate and compare kids' day camp programs in Ontario using established quality indicators, safety standards, and family-specific criteria. This knowledge applies to summer camps, March break programs, PA day programs, and other school-break childcare options.

## Ontario Camp Quality Indicators

### Certifications & Accreditation

**HIGH FIVE - Principles of Healthy Child Development:**
- Gold standard for quality children's programs in Ontario
- Ensures trained staff, age-appropriate programming, and safety protocols
- Look for HIGH FIVE registered or accredited status
- Website: highfive.org

**Ontario Camps Association (OCA):**
- Voluntary accreditation with rigorous safety and program standards
- Annual inspections covering 300+ standards
- Members must carry liability insurance
- Website: ontariocamps.ca

**Municipal Programs:**
- City-run programs (Parks & Recreation) follow municipal safety standards
- Often more affordable than private camps
- Registration typically opens in February/March

### Staff Qualifications

Evaluate staff quality by checking:
- Staff-to-child ratios (Ontario minimum varies by age; look for better than minimum)
  - Ages 4-5: 1:8 ratio
  - Ages 6-8: 1:10 ratio
  - Ages 9-12: 1:12 ratio
- Staff training requirements (First Aid, CPR, HIGH FIVE PHCD)
- Background checks (Vulnerable Sector Screening)
- Returning staff percentage (indicator of program stability)
- Counsellor-in-Training (CIT) policies (CITs should not count in ratios)

### Program Structure

Strong programs include:
- Balanced schedule (active play, creative activities, quiet time, free play)
- Age-appropriate groupings with separate programming
- Indoor and outdoor activity spaces
- Rainy day plans and alternative activities
- Swim instruction or water safety (if applicable)
- Inclusion policies for children with special needs

## Evaluation Criteria

### Must-Have Checklist

Before registering, confirm:
- [ ] Valid insurance coverage
- [ ] Staff background checks completed
- [ ] Written emergency procedures
- [ ] Nut-free or allergy-aware policies (if applicable)
- [ ] Clear pickup/dropoff procedures with ID verification
- [ ] Communication protocol for illness/injury
- [ ] Refund/cancellation policy documented

### Comparison Factors

When comparing camps, assess on these dimensions:

| Factor | What to Check |
|--------|---------------|
| **Cost** | Base fee, before/after care, lunch, materials, registration fees |
| **Location** | Distance from home/work, transit accessibility, parking |
| **Hours** | Core hours, extended care availability, flexibility |
| **Program** | Activity variety, specialization, outdoor time |
| **Meals** | Included/optional, nut-free, accommodation for dietary needs |
| **Flexibility** | Weekly vs. daily registration, cancellation terms |
| **Reputation** | Reviews, word of mouth, years in operation |
| **Sibling discount** | Multi-child pricing, family rates |
| **Inclusion** | Support for special needs, EAs available, accessibility |

### Age-Specific Considerations

**Ages 4-6 (JK-Grade 1):**
- Lower ratios essential, more structured supervision
- Rest/quiet time built into schedule
- Comfort with separation (half-day option if available)
- Washroom assistance policies

**Ages 7-9 (Grade 2-4):**
- Balance of structured activities and free choice
- Skill-building programs (swimming levels, sports skills)
- Social grouping considerations (friends attending)

**Ages 10-12 (Grade 5-7):**
- More independence and choice in activities
- Leadership development, CIT pathways
- Specialty camps aligned with interests (STEM, arts, sports)
- Appropriate challenge level to avoid boredom

## Registration Timing

Ontario camp registration follows a predictable cycle:

| Period | Registration Opens | Peak Demand |
|--------|-------------------|-------------|
| Summer camps | January-February | February-March |
| March break | November-December | January |
| PA day programs | Varies | 2-4 weeks before |

**Early bird discounts** are common for summer camps if registered by January/February. Popular programs fill quickly - waitlists are common for well-known providers.

## Questions to Ask Camp Providers

### Safety & Operations
1. What is the staff-to-child ratio for my child's age group?
2. What training do staff receive? Are background checks completed?
3. What is the procedure if my child is injured or becomes ill?
4. How do you handle allergies and medical conditions?
5. What is your severe weather policy?

### Program & Daily Life
6. What does a typical day look like?
7. How are children grouped (by age, grade, interest)?
8. What happens on rainy days?
9. Is there swimming? What are the water safety protocols?
10. How much screen time is included (if any)?

### Logistics
11. What are the exact pickup and dropoff times and procedures?
12. Is before-care/after-care available? What are the hours and cost?
13. What should my child bring each day?
14. Is lunch included or do we pack lunch?
15. What is the cancellation and refund policy?

### Inclusion
16. How do you support children with special needs or allergies?
17. Can you accommodate dietary restrictions?
18. What is the policy if my child is struggling to adjust?

## Private School Considerations

Private school families face unique planning challenges because the childcare provider market follows the public school board calendar. Key issues:

1. **PA day misalignment**: Private school PA days rarely overlap with the nearest public board's PA days, meaning dedicated PA day programs won't be running
2. **Extended March break**: Some private schools (e.g., German International School Toronto) have a 2-week March break vs. the public board's 1 week. Week 2 will have no March break-specific programs available
3. **Fall break**: Some private schools have a full week fall break (October/November) that public boards do not have. No "fall break camp" market exists
4. **Non-standard school start**: Some private schools start before Labour Day, shortening the summer camp window
5. **Early dismissal days**: Private schools may have early dismissal (e.g., 1:15pm) with no aftercare on certain dates

For detailed test cases and mitigation strategies, consult `references/private-school-test-cases.md`.

## Additional Resources

### Reference Files

For detailed Ontario-specific information:
- **`references/ontario-camp-resources.md`** - Ontario camp directories, subsidy programs, school board calendars, and useful links
- **`references/private-school-test-cases.md`** - Real-world calendar comparisons (GIST vs TDSB) demonstrating private school planning challenges and expected plugin behavior
- **`references/school-calendars/`** - Pre-saved school calendar data:
  - `public-boards/tdsb.md` - Toronto District School Board (2025-2026)
  - `private-schools/gist.md` - German International School Toronto (2025-2026, 2026-2027)
  - Check here first before web searching for a user's school calendar
