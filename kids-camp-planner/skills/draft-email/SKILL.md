---
name: Draft Camp Emails
description: This skill should be used when the user asks to "draft an email to a camp", "write an inquiry email", "email camp provider", "write registration email", "draft waitlist follow-up", "write cancellation email", "email about allergies", "contact camp about special needs", or needs help composing emails to camp providers for inquiries, registration, waitlist follow-ups, special needs requests, dietary accommodations, or cancellations. Provides email templates and personalization using the family profile.
version: 0.1.0
---

# Draft Camp Emails

## Overview

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`.

Draft professional, personalized emails to camp providers. Pull family details from the profile and provider details from research files to create complete, ready-to-send emails. Save drafts to `<research_dir>/drafts/` for review before sending.

## Email Drafting Workflow

### Step 1: Gather Context

Before drafting, read:
1. **Family profile** (`<research_dir>/family-profile.md`) for children's details, special needs, contact info
2. **Provider file** (`<research_dir>/providers/[provider].md`) for camp-specific details, contact email, program names

### Step 2: Determine Email Type

Identify the purpose and use the appropriate template structure:

| Email Type | When to Use |
|------------|-------------|
| **Inquiry** | Asking about program details, availability, pricing |
| **Registration** | Requesting enrollment or registration information |
| **Waitlist follow-up** | Following up on waitlist status |
| **Special needs / dietary** | Informing about allergies, medical needs, accommodations |
| **Schedule / logistics** | Questions about hours, pickup/dropoff, what to bring |
| **Cancellation** | Requesting cancellation or date change |

### Step 3: Draft the Email

**General email guidelines:**
- Friendly but professional tone (parent writing to a camp, not a business letter)
- Include child's name, age, and grade
- Reference specific program names and dates
- Be clear about what information or action is needed
- Include relevant medical/dietary info when appropriate
- Keep it concise - camp administrators handle hundreds of emails

**Save drafts to:** `<research_dir>/drafts/[type]-[provider].md`

## Email Templates

Six templates are available covering all common camp communication scenarios. The inquiry template is shown below as a representative example. For all other templates (registration, waitlist follow-up, special needs/dietary, cancellation, logistics inquiry), see `references/email-templates.md`.

### Inquiry Email (representative example)

```
Subject: Inquiry about [Program Name] for Summer [Year]

Hi [Camp Name] team,

I'm looking into summer camp options for my [son/daughter] [Child Name],
who is [age] years old (entering Grade [X] in September). We're interested
in the [Program Name] program.

I'd appreciate information on:
- Availability for the week(s) of [dates]
- Registration process and any deadlines
- Daily rates available? (for partial weeks or PA day drop-ins)
- [Any specific questions based on research gaps]

[If applicable: We're also considering enrollment for a second child,
[Child 2 Name], age [X]. Do you offer sibling discounts?]

Thank you for your time. Looking forward to hearing from you.

Best regards,
[Parent Name]
[Phone number - optional]
```

## Personalization Rules

When drafting emails, apply these personalization rules:

1. **Use the child's actual name** from the family profile, not "my child"
2. **Calculate current age** from DOB in profile
3. **Reference the specific program name** from the provider file
4. **Include relevant medical/allergy info** automatically if the email type warrants it (registration, inquiry about inclusion)
5. **Mention sibling context** when multiple children are being registered at the same provider
6. **Include pickup/dropoff questions** when parent schedules suggest tight timing

## Output Format

Save each draft as a markdown file:

```markdown
# Email Draft: [Type] - [Provider Name]

**To:** [Email address from provider file]
**Subject:** [Subject line]
**Date drafted:** [Today's date]
**Status:** Draft - ready for review

---

[Email body]

---

**Notes:**
- [Any context for the user about why certain details were included]
- [Reminders about attachments needed, e.g., allergy action plan]
```

## Additional Resources

### Reference Files

- **`references/email-templates.md`** - All email templates: registration, waitlist follow-up, special needs/dietary, cancellation, logistics inquiry

### Example Files

- **`examples/sample-inquiry-email.md`** - Complete personalized inquiry email example
