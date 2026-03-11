# Session Handoff Skill

> **Context Reset Helper** - Capture learnings, update progress files, and generate resume prompt

## Purpose
When you need to reset context (context window full, switching tasks, ending session), this skill:
1. **Captures learnings** - What did we discover about working together?
2. Updates PROGRESS.md with what was accomplished
3. Updates NEXT_STEPS.md with current status and next actions
4. Generates a comprehensive resume file for the next context window

**Important**: Context reset does not mean end of day. This runs anytime context needs to reset.

## Trigger Keywords
- "session handoff"
- "context reset"
- "end session"
- "progress next"

## Process

### Step 0: Capture Learnings
Before doing file updates, ask:

> "Quick check before we wrap up:
> 1. Did we discover any new patterns about how you work best?
> 2. Any communication preferences I should remember?
> 3. Anything that got you unstuck that's worth documenting?"

If yes to any, offer to save those notes in the project folder or a preferences file.

Keep this FAST - don't let it become a blocker. If nothing to add, move on.

### Step 1: Gather Session Summary
Ask or infer:
- What project are we working on?
- What was accomplished this session?
- What's the current status?
- What are the immediate next steps?
- Any critical context the next session needs?

### Step 2: Update PROGRESS.md
Find the project's PROGRESS.md file (in the current working directory or project folder) and append:

```markdown
---

### [DATE] - [Session Description]
**Status:** [Current status]

**Completed:**
- [x] Task 1
- [x] Task 2
- [x] Task 3

**Key Decisions/Discoveries:**
- [Important finding 1]
- [Important finding 2]

**Files Created/Modified:**
- `path/to/file1` (description)
- `path/to/file2` (description)

---

## CURRENT STATUS ([Date])

**What's Built:**
- [Summary of what exists]

**What's Next:**
- [Immediate next steps]

---

*Last updated: [Date] ([Session description])*
```

If PROGRESS.md doesn't exist, create it.

### Step 3: Update NEXT_STEPS.md
Update the header and current status section:

```markdown
# [Project] - Next Steps

**Updated:** [Date] ([Session description])
**Current Phase:** [Phase name]
**Status:** [One-line status]

---

## SESSION STATUS - [Status Header]

### Completed ([Date]):
1. [x] Task 1
2. [x] Task 2

### Next Actions:
1. [ ] Immediate task 1
2. [ ] Immediate task 2

---

## [Rest of existing content...]
```

If NEXT_STEPS.md doesn't exist, skip this step.

### Step 4: Write RESUME.md
Save the resume file in the same folder as the project. This is the file that `/resume` will read next session.

```markdown
# [PROJECT] - Resume Session

**Last Updated:** [Date] ([Session description])

---

## CONTEXT

**WORKING DIRECTORY:** [path]

**OBJECTIVE:** [Clear statement of what needs to happen next]

## WHAT WAS JUST COMPLETED
- [Completed item 1]
- [Completed item 2]
- [Completed item 3]

## CURRENT STATUS
- [Key status point 1]
- [Key status point 2]

## PRIORITIES
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

## NEXT STEPS
1. [ ] [Step 1]
2. [ ] [Step 2]
3. [ ] [Step 3]

## READ FIRST
- [Path to NEXT_STEPS.md]
- [Path to PROGRESS.md]
- [Any other critical files the next session should read]

## WORKING PATTERN REMINDERS
- [Key reminder 1]
- [Key reminder 2]

---

**WHAT TO DO:** Pick ONE next step and execute it. Don't plan - just start.
```

### Step 5: Confirm Handoff

After writing all files, confirm:

```
Session handoff complete!

Files updated:
- PROGRESS.md - Session summary added
- NEXT_STEPS.md - Status updated
- RESUME.md - Resume prompt saved

To resume next session: Type /resume or "pick up where I left off"

Ready to reset context.
```

## Important Rules

1. **Always save RESUME.md** - This is the minimum requirement
2. **Update PROGRESS.md and NEXT_STEPS.md if they exist** - Don't skip these
3. **Include specific file paths** - The next session needs concrete data, not abstractions
4. **Be comprehensive but concise** - Include everything needed, nothing extra
5. **Use the existing format** - Match the style already in the files
6. **Include READ FIRST section** - Tell next session exactly what to read first
