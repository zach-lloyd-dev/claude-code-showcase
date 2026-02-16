# Claude Code Showcase

Architecture patterns, agentic workflows, and real-world production examples built with Claude Code.

> Built by someone who uses Claude Code daily to run an AI automation consulting business. These aren't toy examples. They're extracted from systems serving real clients.

---

## Open Source Skills & Templates

Grab these and drop them into your Claude Code setup:

| Asset | What It Does | Get It |
|-------|-------------|--------|
| **Session Handoff** | Saves context before resetting. Updates PROGRESS.md, NEXT_STEPS.md, writes RESUME.md | [`skills/session-handoff/`](skills/session-handoff/SKILL.md) |
| **Resume Session** | Loads saved context and gets you back to work in seconds | [`skills/resume/`](skills/resume/SKILL.md) |
| **Global Settings Template** | Production-ready `~/.claude/CLAUDE.md` with verification rules, anti-patterns, security defaults | [`templates/global-settings.md`](templates/global-settings.md) |

**Installation:** Copy the skill folders to `~/.claude/skills/` and the template to `~/.claude/CLAUDE.md`. Customize for your projects.

---

## What's Here

### 1. Agentic Workflow Patterns

Patterns for building autonomous multi-step workflows with Claude Code.

**Skill-based architecture:** Modular skills that compose into complex pipelines. Each skill is a self-contained SKILL.md with trigger keywords, process steps, and context loading:

```markdown
# Session Handoff Skill

> Context Reset Helper - Capture learnings, update progress files, generate resume prompt

## Trigger Keywords
- "session handoff"
- "context reset"
- "prepare handoff"

## Process

### Step 0: Capture Learnings (ADHD-Friendly)
Before doing file updates, ask:

> "Quick check before we wrap up:
> 1. Did we discover any new patterns about how you work best?
> 2. Any communication preferences I should remember?
> 3. Anything that got you unstuck that's worth documenting?"

### Step 1: Update PROGRESS.md
### Step 2: Update NEXT_STEPS.md
### Step 3: Generate Resume Prompt
```

Skills compose naturally. `/resume` reads the handoff that `/session-handoff` wrote. No orchestration framework needed.

---

### 2. Context Engineering Patterns

Real-world context engineering techniques for maximizing Claude's performance.

**CLAUDE.md hierarchy:** A three-tier system where global settings cascade into project-specific instructions:

```
~/.claude/CLAUDE.md          ← Global: verification rules, ADHD defaults, code style
└── project/CLAUDE.md        ← Project: git protocol, tech stack, deployment rules
    └── project/CLAUDE.local.md  ← Private: API keys, credentials (gitignored)
```

The global layer encodes hard-won operational rules:

```markdown
## #1 Priority: Verification
**Give Claude a way to verify its work.** This 2-3x output quality.
- After code changes: run tests, lint, typecheck
- After file edits: read the file back to confirm
- After automation: test the actual behavior
- If no verification possible: state assumptions explicitly

## Honesty Rule
| Don't Say                          | Say Instead                              |
|------------------------------------|------------------------------------------|
| "Fixed the bug" (tests failing)    | "Attempted fix, still failing on X"      |
| "Implemented feature" (partial)    | "Core logic done, UI pending"            |
```

**Dynamic context loading:** Skills load relevant context based on task type. The `/resume` skill uses shorthand mapping to find the right project:

```markdown
| Shorthand | Path                            |
|-----------|---------------------------------|
| bss       | projects/black-sheep-systems/   |
| j, journal| journal/                        |
| n8n       | projects/n8n-automations/       |
```

---

### 3. Browser Automation with Claude Code

Production patterns for browser automation using Playwright orchestrated by Claude Code.

**Persistent profile pattern:** Log in once manually, reuse the session forever. No credential storage, no OAuth flows:

```typescript
import { chromium } from 'playwright';
import * as path from 'path';

const PROFILE_DIR = path.join(process.env.HOME || '', '.x-playwright-profile');

async function launchWithProfile() {
  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false,
    viewport: { width: 1280, height: 800 },
  });
  const page = context.pages()[0] || await context.newPage();
  return { context, page };
}
```

**Self-healing selectors:** Multiple selector strategies with fallback chains, because platforms change their DOM constantly:

```typescript
async function typeContent(page: Page, content: string) {
  const composeSelectors = [
    '[data-testid="tweetTextarea_0"]',
    '[role="textbox"][data-testid="tweetTextarea_0"]',
    'div[role="textbox"]',
    '.public-DraftEditor-content',
  ];

  for (const selector of composeSelectors) {
    const el = await page.$(selector);
    if (el) {
      await el.click();
      await page.waitForTimeout(300);
      await page.keyboard.type(content, { delay: 10 });
      return;
    }
  }
  throw new Error('Could not find compose textarea');
}
```

**Screenshot verification loops:** Every action gets a screenshot for debugging. When Claude orchestrates the browser, it can read the screenshots to verify state.

---

### 4. Claude Code + n8n Integration

Connecting Claude Code's agentic capabilities with n8n's workflow orchestration:

- Webhook-triggered Claude Code sessions
- API-driven content processing pipelines
- Automated quality checks with Claude as evaluator
- Error handling and retry patterns for production reliability

---

### 5. Production Deployment Patterns

Taking Claude Code projects from prototype to production.

**Security scanning with gitleaks:** Custom rules that catch what the defaults miss:

```toml
# ~/.gitleaks.toml — extends default rules
[[rules]]
id = "hardcoded-password-assignment"
description = "Hardcoded password in code"
regex = '''password\s*[=:]\s*["'][^"']{4,}["']'''
keywords = ["password"]

[[rules]]
id = "hardcoded-api-key-assignment"
description = "Hardcoded API key in code"
regex = '''api[_-]?key\s*[=:]\s*["'][^"']{8,}["']'''
keywords = ["api_key", "apikey", "api-key"]

[allowlist]
description = "Allow placeholder credential values"
regexes = [
    '''password\s*=\s*["'](?:CHANGE_ME|placeholder|xxx+)["']''',
]
```

**Environment variable discipline.** Credentials never touch shell config. Everything lives in `~/.env.local`, sourced by `.zshrc`, referenced by `${ENV_VAR}` in code.

**CI/CD with Vercel.** Git push for staging, `vercel --prod` for production. Always verify the live deployment after shipping.

---

## Featured Pattern: CLI-First Service Integration

> The "Steinberger Pattern": CLI wrappers over raw API calls, every time.

**The problem:** MCP tool declarations eat tokens on every call, even when unused. Raw API calls with `curl` are fragile and context-heavy. You need a way for Claude to interact with external services that's token-efficient, self-documenting, and composable.

**The solution:** Thin bash wrappers with three output modes:

```bash
#!/usr/bin/env bash
# bss-kit — CLI wrapper for Kit (ConvertKit) API
set -euo pipefail

API_KEY="${KIT_API_KEY:-}"
if [ -z "$API_KEY" ]; then
  echo "Error: KIT_API_KEY not set" >&2
  echo "Set it in ~/.env.local: export KIT_API_KEY=\"your-key\"" >&2
  exit 1
fi

# Output mode: human (default), --json (agent), --plain (piping)
OUTPUT="human"
for arg in "$@"; do
  case "$arg" in
    --json)  OUTPUT="json" ;;
    --plain) OUTPUT="plain" ;;
  esac
done

# Auto-detect non-TTY → plain (pipes just work)
if [ ! -t 1 ] && [ "$OUTPUT" = "human" ]; then
  OUTPUT="plain"
fi
```

Every command supports all three modes:

```bash
$ bss-kit subscribers count
Active Subscribers: 67

$ bss-kit subscribers count --json
{"count": 67, "status": "active", "as_of": "2026-02-14T12:00:00Z"}

$ bss-kit subscribers count --plain
67
```

**The result:**
- Zero tokens for unused tools (vs MCP declarations every call)
- Claude discovers capabilities via `--help` (self-documenting)
- Composable with pipes: `bss-kit subscribers count --plain | xargs echo "We have" {} "subscribers"`
- Works headless in CI with env var auth
- Active wrappers: `bss-kit` (email), `bss-x` (Twitter/X), posting scripts for X and LinkedIn

---

## Architecture Philosophy

**Simple beats clever.** Every pattern here follows three rules:

1. **It solves a real problem.** Extracted from production use, not imagined scenarios.
2. **It's the simplest version that works.** No premature abstraction.
3. **It fails gracefully.** Explicit error handling, not silent failures.

This comes from 5 years of coaching people through behavior change: the best system is the one people actually use. Complex systems get abandoned. Simple systems compound.

---

## Tech Stack

| Tool | Role |
|------|------|
| **Claude Code** | Primary development environment, agentic orchestration |
| **Claude API** | Programmatic access for content generation and evaluation |
| **n8n** | Workflow automation and API orchestration |
| **Playwright** | Browser automation for authenticated web workflows |
| **Bun + TypeScript** | Web applications, posting scripts, tooling |
| **Bash + jq** | CLI wrappers, service integrations |
| **Astro + Starlight** | Documentation sites with React islands and glass UI |
| **Vercel** | Web deployment and hosting |

---

## Learn These Patterns

**[Claude Code Starter Kit](https://zach-lloyd.kit.com/ddc15304ae):** Battle-tested CLAUDE.md templates, pre-built skills, folder blueprints, and best practices documentation. Everything in this showcase, packaged for you to copy-customize-ship.

---

## Related Projects

- **[AAA Authority Acceleration](https://github.com/zach-lloyd-dev/aaa-authority-acceleration):** 23 modular Claude Code skills for content automation. 13 stars, MIT licensed.
- **[Gym Lead Chatbot](https://github.com/zach-lloyd-dev/gym-lead-chatbot):** AI-powered lead qualification widget built with Claude.

---

## About

I'm Zach Lloyd, founder of [Black Sheep Systems](https://zach-lloyd.com), an AI automation consultancy. I build autonomous systems for small business owners using Claude Code, n8n, Playwright, and TypeScript.

Previously: 5 years as a fitness coach and gym owner, where I learned that sustainable systems beat flashy solutions every time. That philosophy drives everything I build.

I also host the **Zach Stack** podcast. Deep dives on building with AI tools as a non-traditional developer.

[![YouTube](https://img.shields.io/badge/YouTube-@blacksheepsystems-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://youtube.com/@blacksheepsystems)
[![X](https://img.shields.io/badge/X-@zachlloydai-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/zachlloydai)
