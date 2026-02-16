# Resume Session Skill

> **Context Loader** - Load saved session context and continue where you left off

## Purpose

Quickly resume a previous session without copy/pasting prompts. Reads the saved RESUME.md file from wherever the last session was working.

## Trigger Keywords

- `/resume`
- `/resume [location]`
- "resume session"
- "pick up where we left off"

## Process

### Step 1: Find RESUME.md

**Primary method:** Search for RESUME.md files in the project root and common locations.

```bash
# Find recent RESUME.md files
find . -name "RESUME.md" -maxdepth 3 -exec ls -lt {} +
```

**If argument provided**, check these paths directly:
- `projects/[argument]/RESUME.md` (e.g., `/resume my-app`)
- `[argument]/RESUME.md` (e.g., `/resume journal`)
- Use shorthand mapping if configured (see Customization below)

**Fallback:** Use Glob `**/RESUME.md` and show the user all matches to pick from.

### Step 2: Load Resume File

Read the found RESUME.md.

**If RESUME.md doesn't exist in that location**, fall back to:
1. `NEXT_STEPS.md` in same folder
2. `PROGRESS.md` in same folder (read last entry)
3. Ask user: "No resume file found. What were you working on?"

### Step 3: Display Context

Show the user:
- What was completed last session
- Current status
- Next steps
- Working pattern reminders

### Step 4: Read Critical Files

If RESUME.md has a "READ FIRST" section, read those files to load context.

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

## Customization

Add shorthand mappings to your project's CLAUDE.md for quick access:

```markdown
## Resume Shortcuts
| Shorthand | Path |
|-----------|------|
| api       | projects/api-server/ |
| web       | projects/web-app/ |
| docs      | projects/documentation/ |
```

Then use: `/resume api` to jump straight to that project's context.

## Quick Commands

After resuming, common next actions:
- "Let's do step 1"
- "What's blocking step 1?"
- "I want to work on something else"
- "Show me the full NEXT_STEPS.md"
