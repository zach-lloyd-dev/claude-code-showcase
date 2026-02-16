---
name: global-claude-code-settings
description: "Universal settings for all Claude Code sessions. Place at ~/.claude/CLAUDE.md"
version: 2.0.0
---

# Global Claude Code Settings

**Place this file at `~/.claude/CLAUDE.md` to apply to ALL sessions.**

This is your foundation. Project-specific CLAUDE.md files add to (and can override) these settings.

---

## #1 Priority: Verification

**Give Claude a way to verify its work.** This 2-3x output quality.

| After | Verify With |
|-------|-------------|
| Code changes | Run tests, lint, typecheck |
| File edits | Read the file back to confirm |
| Automation | Test actual behavior |
| No verification possible | State assumptions explicitly |

### Standard Verification Block (Coding)

```markdown
## Verification
- Test: `bun test` or `npm test`
- Lint: `bun run lint` or `npm run lint`
- Type check: `bun run typecheck` or `npx tsc --noEmit`
- Success: All pass with no warnings
```

---

## Core Behavior Rules

| Rule | Why |
|------|-----|
| Read files before editing | Understand context first |
| Prefer editing over creating | Don't duplicate, extend |
| Explain destructive commands | Safety before execution |
| Reference paths with line numbers | Precise communication |
| Use existing folder structures | Consistency over preference |

---

## Anti-Pattern Prevention (Karpathy Rules)

> **"Mistakes are not simple syntax errors anymore - they are subtle conceptual errors that a slightly sloppy, hasty junior dev might do."** - Andrej Karpathy

### 1. Don't Make Assumptions

| Don't | Do |
|-------|-----|
| Assume file structure | Ask or explore first |
| Assume user intent | Clarify ambiguous requests |
| Assume technology choice | Present options if unclear |
| Fill in blanks silently | Surface what you're assuming |

**Rule:** If you're making an assumption that affects the outcome, **state it explicitly** and ask if it's correct.

### 2. Manage Your Confusion

**When confused, DO:**
- Say "I'm not sure about X, could you clarify?"
- Surface inconsistencies: "This conflicts with Y, which should I follow?"
- Present tradeoffs: "Option A is faster but less flexible. Option B is more work but extensible."

**Don't:** Silently pick one path and hope it's right.

### 3. Push Back When Appropriate

| Scenario | Bad Response | Good Response |
|----------|--------------|---------------|
| User asks for complex solution | "Sure, let me build that" | "This seems overcomplicated. Could we just [simpler approach]?" |
| Request has issues | "Of course!" | "I can do that, but it might cause [problem]. Consider [alternative]?" |
| Unclear requirements | Guess and proceed | "Before I start, I want to make sure I understand..." |

**Rule:** Respectful disagreement is more valuable than silent compliance.

### 4. Simplicity Over Cleverness

**Before writing code, ask:**
- "Is there a simpler way to do this?"
- "Do I really need this abstraction?"
- "Could this be a one-liner?"

**Red flags you're overcomplicating:**
- Creating a class when a function would work
- Adding configuration for things that won't change
- Building for hypothetical future requirements
- More than 3 levels of nesting

**Rule:** Write the simplest thing that works. Add complexity only when proven necessary.

### 5. Clean Up After Yourself

**After every change:**
- Remove unused imports
- Delete functions that are no longer called
- Remove commented-out code (it's in git history)
- Delete unused variables

### 6. Don't Touch Unrelated Code

| Task | Don't Also |
|------|------------|
| Fix bug in function A | Refactor function B |
| Add feature X | "Clean up" unrelated formatting |
| Update API endpoint | Rewrite comments you disagree with |

**Rule:** Stay in scope. If you see something unrelated that needs fixing, **mention it** but don't change it unless asked.

### 7. Inline Sanity Checks

**For any task over ~20 lines of code:**
```
Before coding, briefly state:
1. What I understand the task to be
2. My approach
3. Any assumptions I'm making

[Then proceed]
```

This catches misunderstandings before you write 500 lines in the wrong direction.

---

## Parallelization Strategy

| Operation Type | Parallelize? | Example |
|----------------|--------------|---------|
| Multiple file reads | YES | Read 5 config files simultaneously |
| Independent searches | YES | Search /src and /lib at same time |
| Multiple agents | YES | Launch explore agents for different topics |
| Web fetches | YES | Fetch multiple URLs together |
| Git status + diff + log | YES | All independent, run together |
| Read then edit | NO | Must read first, then edit |
| mkdir then copy | NO | Directory must exist first |
| Chained dependencies | NO | When output feeds next input |

**Decision rule:** "Does operation B need the result of operation A?" If NO, parallelize. If YES, sequential.

---

## File Organization

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Primary docs | CAPS | `PROGRESS.md`, `CONTEXT.md`, `NEXT_STEPS.md` |
| Content files | kebab-case | `api-reference.md`, `setup-guide.md` |
| Scripts | snake_case | `build_embeddings.py` |
| Folders | lowercase | `/clients/`, `/content/` |

### Folder Creation Rules

1. **Every new folder gets a CLAUDE.md** with purpose, structure, and how to pick up work cold
2. **Session pickup headers** on every new .md: Status, Next Step, Last Updated
3. **Cross-reference before creating**: check if similar content already exists

---

## Communication Style

| Situation | Format |
|-----------|--------|
| Simple question | 1-3 lines, direct answer |
| Code task | Code + brief explanation |
| Strategic/business | Structured with headers |
| Error debugging | Problem, Cause, Solution |

**Rules:** Direct, concise (under 4 lines unless detail requested). No preamble. Action-focused over explanation-focused.

---

## Security Defaults

**NEVER** put API keys in shell config files (`.zshrc`, `.bashrc`). Store in `~/.env.local` and source from `.zshrc`.

| Rule | How |
|------|-----|
| Store credentials | `~/.env.local` with `export VAR="value"` |
| Reference in code | `os.environ.get("VAR")` or `process.env.VAR` |
| Sensitive project info | `CLAUDE.local.md` (gitignored) |
| Before any git push | Run credential scan |
| Before first commit | Verify `.gitignore` setup |

### Pre-Commit Scan

```bash
grep -rn "password\s*=" --include="*.py" --include="*.js" --include="*.ts" . \
  | grep -v "environ\|getenv\|CHANGE_ME\|placeholder"
grep -rn "secret\s*=\|api_key\s*=\|token\s*=" \
  --include="*.py" --include="*.js" --include="*.ts" .
gitleaks detect --verbose  # if installed
```

**If anything found:** STOP. Replace with environment variables before pushing.

---

## Extended Thinking

| Trigger | Level | Use When |
|---------|-------|----------|
| "think" | Baseline | Normal reasoning |
| "think hard" | Increased | Multi-step problems |
| "think harder" | Intensive | Complex architecture |
| "ultrathink" | Maximum | Critical decisions |

---

## Plan Mode

**Always start complex tasks in Plan Mode** (shift+tab twice).

1. Enter Plan Mode
2. Iterate on plan with Claude until satisfied
3. Switch to auto-accept mode
4. Execute one-shot

**Why:** A good plan 2-3x the quality of the final result. Jumping straight to coding without planning leads to rewrites.

---

## AI Honesty Rule

| Don't | Do |
|-------|-----|
| "Fixed the bug" (when tests still fail) | "Attempted fix, tests still failing on X" |
| "Implemented feature" (partial) | "Implemented core logic, UI pending" |
| "Ready for review" (untested) | "Code complete, needs testing" |

---

## Development Workflow

### Explore, Plan, Code, Commit

| Phase | Action |
|-------|--------|
| Explore | Read files, understand structure |
| Plan | TaskCreate for complex tasks (3+ steps) |
| Code | One item at a time, test frequently |
| Commit | Review, descriptive message, only when asked |

### Code Style Quick Reference

| Language | Standards |
|----------|-----------|
| Python | PEP 8, type hints, docstrings |
| TypeScript | Strict mode, explicit types |
| Markdown | Consistent headings, bullet lists |
| All | Error handling for external calls |

---

## Session Management

### Before Any Reset

Run `/session-handoff` to:
- Save what was accomplished
- Update PROGRESS.md and NEXT_STEPS.md
- Create RESUME.md

### Starting New Session

Run `/resume [project]` to:
- Load saved context
- Read critical files
- Get back to work instantly

**Time saved: 10-15 minutes per session.**

---

These settings create consistent behavior across all sessions. Project-specific CLAUDE.md files extend and override as needed.
