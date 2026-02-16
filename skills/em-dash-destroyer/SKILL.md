---
name: em-dash-destroyer
description: "Remove em dashes from written content and replace with better punctuation. Use when: done writing, cleanup pass, remove em dashes, fix dashes, polish content, edit content, content review, post-writing cleanup, AI writing cleanup"
version: 1.0.0
---

# Em Dash Destroyer

## Why This Exists

AI-generated writing overuses em dashes. They become a crutch that makes every piece of content sound the same. Real writers use periods, commas, colons, and spaces. This skill runs after writing is done and replaces every em dash with the right alternative.

## When to Use

- After finishing a draft (blog post, guide page, email, social copy)
- After Claude generates any written content
- When editing existing content that feels "AI-ish"
- As a final cleanup pass before publishing

Trigger phrases: `/em-dash-destroyer`, "remove em dashes", "cleanup dashes", "destroy em dashes", "polish this content"

## When NOT to Use

- Mid-draft (finish writing first, clean up after)
- On code files (em dashes don't appear in code)
- On content where em dashes are intentionally used for brand voice

## Installation

**Claude Code:** Copy this folder to `~/.claude/skills/em-dash-destroyer/` and it activates automatically via trigger phrases.

**ChatGPT, Gemini, or any other LLM:** See [`UNIVERSAL.md`](UNIVERSAL.md) for a copy-paste prompt version that works everywhere.

## Process

### Step 1: Identify the Target

Ask if not obvious:
```
What content should I clean up?
- A specific file? (provide path)
- The content I just wrote?
- A block of text you'll paste?
```

### Step 2: Find All Em Dashes

Scan the content for:
- `—` (em dash, U+2014)
- ` — ` (em dash with spaces)
- `--` (double hyphen used as em dash)

Report count:
```
Found [X] em dashes in [file/content]. Processing...
```

### Step 3: Replace Each One

For EACH em dash, determine the best replacement based on context:

**Rule 1: Parenthetical aside -> use commas**
```
Before: The contractor — who had 40 tools — only needed a drill.
After:  The contractor, who had 40 tools, only needed a drill.
```

**Rule 2: Introducing a list or explanation -> use a colon**
```
Before: He brought everything — jackhammers, welding rigs, scaffolding.
After:  He brought everything: jackhammers, welding rigs, scaffolding.
```

**Rule 3: Dramatic pause or emphasis -> use a period (split into two sentences)**
```
Before: The truck blocks your driveway — wasted context.
After:  The truck blocks your driveway. Wasted context.
```

**Rule 4: Contrast or pivot -> use a period or semicolon**
```
Before: The API way is slow — the CLI way is fast.
After:  The API way is slow. The CLI way is fast.
```

**Rule 5: Simple aside that doesn't need punctuation -> just parentheses or rewrite**
```
Before: Claude Code — the CLI tool — runs bash natively.
After:  Claude Code (the CLI tool) runs bash natively.
```
Or better yet, rewrite:
```
After:  Claude Code runs bash natively.
```
(If the aside isn't adding value, cut it entirely.)

### Step 4: Verify No Orphans

After all replacements:
- Re-scan for any remaining `—`, ` — `, or `--`
- Confirm zero em dashes remain
- Read back the full content to verify it flows naturally

### Step 5: Show the Diff

Present changes as a before/after:
```
Replaced [X] em dashes:
1. "tools — jackhammers" -> "tools: jackhammers" (colon, introduces list)
2. "slow — the CLI" -> "slow. The CLI" (period, contrast)
3. "Code — the CLI tool —" -> "Code (the CLI tool)" (parenthetical)
...

[Show full updated content]
```

## Guardrails

| Rule | Why |
|------|-----|
| Never add em dashes back | Defeats the purpose |
| Don't change meaning | Replacement must preserve the original intent |
| Prefer simpler punctuation | Period > semicolon > colon > comma > parentheses |
| Rewrite when possible | Sometimes the best fix is cutting the aside entirely |
| Don't touch hyphens | Regular hyphens (-) in compound words are fine |
| Report the count | User should see how many were found and fixed |

## Priority Order for Replacements

When multiple replacements would work, prefer in this order:
1. **Period** (strongest, cleanest)
2. **Comma** (for true parentheticals)
3. **Colon** (for lists/explanations)
4. **Parentheses** (for brief clarifications)
5. **Semicolon** (rarely, for closely related clauses)
6. **Just a space** (last resort)

## Example: Full Cleanup

**Before:**
> Anthropic released three features — Tool Search, Programmatic Calling, and Examples — that solve the biggest pain points. The first feature — Tool Search — reduces token usage by 85%. Instead of loading everything upfront — which wastes context — Claude discovers tools on demand.

**After:**
> Anthropic released three features (Tool Search, Programmatic Calling, and Examples) that solve the biggest pain points. The first feature, Tool Search, reduces token usage by 85%. Instead of loading everything upfront, which wastes context, Claude discovers tools on demand.

Three em dashes removed. Zero meaning lost. Reads like a human wrote it.
