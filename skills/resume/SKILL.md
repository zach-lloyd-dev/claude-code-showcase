# Resume Session Skill

> **Context Loader** - Load saved session context and continue where you left off

## Purpose
Quickly resume a previous session without copy/pasting prompts. Reads the saved RESUME.md file from wherever the last session was working.

## Trigger Keywords
- `/resume`
- `/resume [project-name]`
- "resume session"
- "pick up where I left off"
- "where did we leave off?"

## Process

### Step 1: Find RESUME.md

Search for RESUME.md files in the current directory and subdirectories.

**If an argument is provided** (like `/resume my-project`):
- Check `[argument]/RESUME.md` first
- Then search for any RESUME.md in folders matching that name

**If no argument:**
- Search for all RESUME.md files in the working directory and subfolders
- Show the user all options found, sorted by most recently modified
- Let them pick which one to load

**If no RESUME.md files found**, fall back to:
1. Look for NEXT_STEPS.md in the current directory
2. Look for PROGRESS.md (read the last entry)
3. Ask the user: "No resume file found. What were you working on?"

### Step 2: Load Resume File
Read the found RESUME.md file completely.

### Step 3: Display Context
Show the user:
- What was completed last session
- Current status
- Next steps
- Working pattern reminders (if any)

### Step 4: Read Critical Files
If the RESUME.md has a "READ FIRST" section listing file paths, read those files to load full context. This gets Claude up to speed on the actual code/content, not just the summary.

### Step 5: Start Working
Ask: "Ready to continue. What's the ONE thing to tackle first?"

## Output Format

```
---
## Resuming [PROJECT NAME]

**Last Session:** [Date] - [Description]

**Status:** [Current status summary]

**Next Steps:**
1. [ ] [Step 1]
2. [ ] [Step 2]
3. [ ] [Step 3]

---

Ready to continue. What's the ONE thing to tackle first?
```

## Quick Commands

After resuming, common next actions:
- "Let's do step 1"
- "What's blocking step 1?"
- "I want to work on something else"
- "Show me the full PROGRESS.md"
