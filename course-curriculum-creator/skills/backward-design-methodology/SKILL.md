---
name: Backward Design Methodology
description: This skill should be used when the user asks to "use backward design", "create curriculum using UbD", "design learning outcomes first", "start with desired results", "plan assessments before activities", "design assessments first", "create outcomes-based curriculum", or references Understanding by Design framework. Also applies when user mentions aligning outcomes with assessments or avoiding activity-first planning. Provides comprehensive guidance on applying backward design methodology to create effective curricula for 1-2 day intensive workshops.
version: 0.1.0
---

# Backward Design Methodology

## Overview

Backward design (Understanding by Design/UbD) is a curriculum planning framework that starts with the end in mind. Instead of beginning with content or activities, design courses by first identifying desired learning outcomes, then determining assessment evidence, and finally planning learning experiences. This approach ensures every workshop component serves a clear purpose and students achieve measurable results.

For 1-2 day intensive workshops, backward design prevents common pitfalls: content overload, misaligned assessments, and activities that don't advance learning objectives. The framework creates focused, achievable curricula that maximize learning in compressed timeframes.

## The Three Stages of Backward Design

### Stage 1: Identify Desired Results

Start by answering: "What should students be able to do by the end of this workshop?"

**Define learning outcomes:**
- Use measurable, observable action verbs (see blooms-taxonomy skill)
- Focus on 3-5 core outcomes for 1-day workshops, 5-8 for 2-day workshops
- Align outcomes with student needs and market positioning
- Ensure outcomes are achievable within the timeframe

**Distinguish between:**
- **Worth being familiar with**: Background knowledge, context, nice-to-know information
- **Important to know**: Key concepts, fundamental principles, essential vocabulary
- **Enduring understanding**: Core insights students will retain long-term, transferable skills

**For intensive workshops, prioritize enduring understanding.** Avoid the coverage trap—don't try to teach everything. Select the most impactful outcomes students can reasonably achieve in 1-2 days.

**Example outcomes for 2-day PropTech workshop:**
1. Analyze PropTech use cases using established frameworks (Porter's Five Forces, value chain analysis)
2. Evaluate PropTech solutions for specific real estate challenges with defined criteria
3. Create implementation roadmaps for PropTech adoption in traditional real estate contexts

**Course positioning connection:**
Learning outcomes directly inform course positioning. The outcomes define:
- **Target audience**: Who needs these specific capabilities?
- **Value proposition**: What problem do these outcomes solve?
- **Market differentiation**: What makes this approach unique?

Write outcomes in `01-planning/learning-objectives.md` and reference them in `01-planning/course-positioning.md`.

### Stage 2: Determine Acceptable Evidence

Before planning activities, establish how to measure whether students achieved the outcomes. Ask: "What evidence proves students can do what the outcomes specify?"

**Assessment types for intensive workshops:**

**Performance tasks** (most suitable for 1-2 day formats):
- Hands-on demonstrations of skill application
- Case study analysis and solution design
- Real-world problem-solving exercises
- Group projects with deliverables
- Simulations and role-plays

**Other evidence:**
- Pre/post knowledge checks (for foundation concepts)
- Self-assessments and peer reviews
- Exit tickets and reflection prompts
- Portfolio pieces or work samples

**Alignment principle (CRITICAL):**
Each learning outcome must have corresponding assessment evidence. Use this validation matrix:

| Learning Outcome | Assessment Method | Timing | Success Criteria |
|------------------|-------------------|--------|------------------|
| [Outcome 1] | [How measured] | [When] | [What constitutes success] |

**For intensive workshops:**
- Integrate assessments into activities (embedded assessment)
- Use formative assessment throughout (check understanding frequently)
- Make summative assessments practical and immediately applicable
- Avoid high-stakes testing; focus on performance demonstration

**Example assessments for PropTech workshop:**
- Outcome 1 (Analyze use cases): Given PropTech scenario, apply Porter's Five Forces in 45-minute analysis exercise
- Outcome 2 (Evaluate solutions): Rank three PropTech tools using evaluation rubric in group activity
- Outcome 3 (Create roadmaps): Develop 90-day implementation plan for selected PropTech solution

Document assessments in `03-assessment/rubrics.md` with detailed evaluation criteria (see assessment design guidance in references/assessment-design.md).

### Stage 3: Plan Learning Experiences and Instruction

Only after defining outcomes (Stage 1) and assessments (Stage 2), design the learning activities. Ask: "What experiences will equip students to perform well on the assessments?"

**Principles for intensive workshop activities:**

**1. Alignment**: Every activity must directly support outcomes and prepare for assessments
- Avoid "interesting but tangential" content
- Cut activities that don't advance learning objectives
- Ensure activities scaffold toward assessment tasks

**2. Active learning bias**: Minimize passive lectures in favor of hands-on practice
- Aim for 70/30 or 60/40 practice-to-instruction ratio for lab-heavy workshops
- Use "I do, we do, you do" progression within modules
- Incorporate frequent practice opportunities

**3. Scaffolding**: Progress from simple to complex across the workshop timeline
- Day 1 morning: Foundation concepts (Remember/Understand level)
- Day 1 afternoon: Application and analysis (Apply/Analyze level)
- Day 2: Synthesis and creation (Evaluate/Create level)
- Build each module on previous learning

**4. Contextualization**: Ground all activities in real-world scenarios
- Use authentic problems from students' domains
- Provide industry-specific examples and case studies
- Enable immediate application to participants' work

**5. Formative feedback loops**: Check understanding continuously
- Module check-ins (exit tickets, quick polls)
- Peer review and discussion
- Instructor observation and corrective guidance
- Adjust pacing based on student progress

**Activity planning workflow:**

1. **Map outcomes to timeline**: Distribute outcomes across workshop days/modules based on cognitive complexity
2. **Design anchor activities**: Create 2-3 major activities per outcome that mirror assessments
3. **Add bridging activities**: Fill gaps with mini-exercises that build required sub-skills
4. **Incorporate instruction**: Add targeted teaching moments right before practice
5. **Build in breaks**: Account for cognitive load—include breaks, meals, transition time
6. **Validate alignment**: Confirm every activity connects to outcomes and assessments

**Module structure template for intensive workshops:**

```
Module Title [Timing: 90-120 minutes]

Learning Objective: [From Stage 1]
Assessment: [From Stage 2]

Instruction (15-20 minutes):
- Key concepts introduction
- Framework/tool explanation
- Worked example demonstration

Guided Practice (25-35 minutes):
- Structured exercise with support
- Instructor circulates and assists
- Debrief and address misconceptions

Independent Practice (40-50 minutes):
- Authentic application task
- Individual or small group work
- Mimics assessment format

Formative Check (10-15 minutes):
- Exit ticket or group share-out
- Gauge readiness for next module
- Address remaining questions
```

Document detailed lesson plans in `02-design/lesson-plans.md` following this structure for each module.

## Intensive Workshop Considerations

**Timeframe constraints:**
- Compress coverage to what's essential and achievable
- Focus on skills students can apply immediately
- Eliminate theory-heavy content without practical application
- Plan for 5-6 hours of instruction per day (account for breaks)

**Energy management:**
- Start each day with engaging, lower-stakes activities (warm-up)
- Place cognitively demanding work mid-morning and mid-afternoon
- Use post-lunch activities strategically (pair work, movement-based)
- End with synthesis and reflection to consolidate learning

**Adult learner principles:**
- Make relevance explicit—connect to students' professional contexts
- Honor prior experience through discussion and peer learning
- Provide autonomy in practice activities (choice, flexibility)
- Create psychologically safe environment for risk-taking

**Practical logistics:**
- Include buffer time (10-15% of schedule) for overruns
- Plan for technical difficulties if using tools/software
- Prepare materials in advance (handouts, slides, supplies)
- Test activities with realistic timing before workshop

## Backward Design Workflow for This Plugin

When creating a course using this plugin, apply backward design systematically:

**Step 1: Define outcomes** (`/generate-objectives`)
- Use blooms-taxonomy skill to craft measurable objectives
- Prioritize 3-8 outcomes based on workshop duration
- Validate outcomes are achievable in timeframe

**Step 2: Design assessments** (`/generate-rubrics`)
- Create performance tasks aligned to each outcome
- Develop evaluation criteria (1-5 scale analytical rubrics)
- Ensure assessments are embedded in workshop activities

**Step 3: Plan activities** (`/generate-lesson-plans`)
- Design modules that prepare students for assessments
- Structure activities using "I do, we do, you do" progression
- Validate alignment: outcomes → assessments → activities

**Step 4: Validate alignment** (`/review-curriculum` or quality-reviewer agent)
- Check every outcome has corresponding assessment
- Confirm activities support outcomes and assessments
- Verify timing is realistic for intensive format

**Throughout:** Reference course positioning to ensure outcomes serve target audience needs.

## Validation Checklist

Use this checklist to validate backward design alignment:

**Stage 1 (Outcomes):**
- [ ] Outcomes use measurable action verbs (Bloom's taxonomy)
- [ ] Outcome count is appropriate (3-5 for 1-day, 5-8 for 2-day)
- [ ] Outcomes are achievable within workshop timeframe
- [ ] Outcomes progress from lower to higher cognitive levels across workshop
- [ ] Outcomes align with course positioning and audience needs

**Stage 2 (Assessments):**
- [ ] Each outcome has at least one corresponding assessment
- [ ] Assessments are performance-based (hands-on, applicable)
- [ ] Assessment methods match cognitive level of outcomes
- [ ] Success criteria are clear and measurable (rubrics)
- [ ] Assessments are embedded in workshop activities

**Stage 3 (Activities):**
- [ ] Every activity connects to at least one learning outcome
- [ ] Activities prepare students for assessment tasks
- [ ] Activity sequence progresses from simple to complex
- [ ] Practice-to-instruction ratio is appropriate (60/40 or 70/30 for lab-heavy)
- [ ] Activities include formative feedback opportunities
- [ ] Total activity time plus breaks fits within workshop duration
- [ ] Activities are contextualized to real-world scenarios

**Overall Coherence:**
- [ ] Clear line of sight: positioning → outcomes → assessments → activities
- [ ] No orphaned activities (activities without outcome connection)
- [ ] No untested outcomes (outcomes without assessment evidence)
- [ ] No misaligned assessments (assessments that don't measure outcomes)

## Common Pitfalls to Avoid

**Pitfall 1: Activity-first planning**
❌ "I'll teach Porter's Five Forces, then value chain analysis, then..."
✅ "Students need to analyze PropTech use cases strategically (outcome). Porter's Five Forces is one tool to support that outcome."

**Pitfall 2: Coverage obsession**
❌ "I need to cover all 12 PropTech categories in 2 days."
✅ "I'll focus on 3 high-impact categories students can deeply understand and apply."

**Pitfall 3: Assessment afterthought**
❌ Plan all activities, then add assessment at the end.
✅ Define assessments before activities, then design activities that prepare for assessments.

**Pitfall 4: Misaligned assessments**
❌ Outcome: "Evaluate PropTech solutions." Assessment: Multiple-choice quiz on PropTech definitions.
✅ Outcome: "Evaluate PropTech solutions." Assessment: Rank three solutions using evaluation rubric with justification.

**Pitfall 5: Underestimating time**
❌ Plan 8 hours of content for a 6-hour workshop day.
✅ Plan 5 hours of instruction plus breaks, discussions, transitions, buffer time.

**Pitfall 6: Passive learning dominance**
❌ 4 hours of lecture, 1 hour of practice per day.
✅ 2 hours of instruction, 3 hours of practice per day (or 60/40 ratio).

## Additional Resources

### Reference Files

For detailed guidance on specific aspects of backward design:
- **`references/assessment-design.md`** - Comprehensive assessment planning strategies

_Additional reference files for activity patterns and timing guidelines are under development._

### Related Skills

- **blooms-taxonomy** skill: Use for selecting action verbs and cognitive levels for learning outcomes
- Load when writing Stage 1 outcomes to ensure measurable, appropriately-leveled objectives

---

Apply backward design rigorously to create focused, effective curricula where every element serves clear learning outcomes. Start with the end in mind, plan assessments before activities, and validate alignment continuously throughout the design process.
