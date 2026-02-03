# Claude Code Showcase

Architecture patterns, agentic workflows, and real-world production examples built with Claude Code.

> Built by someone who uses Claude Code daily to run an AI automation consulting business. These aren't toy examples — they're extracted from systems serving real clients.

## What's Here

### 1. Agentic Workflow Patterns

Patterns for building autonomous multi-step workflows with Claude Code:

- **Skill-based architecture** — Modular Claude Code skills that compose into complex pipelines
- **Browser automation agents** — Playwright + Claude Code for authenticated web workflows
- **Content generation pipelines** — One input → structured outputs across multiple platforms
- **Evaluation-driven development** — Building evals into agentic workflows for quality control

### 2. Claude Code + n8n Integration

Connecting Claude Code's agentic capabilities with n8n's workflow orchestration:

- Webhook-triggered Claude Code sessions
- API-driven content processing pipelines
- Automated quality checks with Claude as evaluator
- Error handling and retry patterns for production reliability

### 3. Context Engineering Patterns

Real-world context engineering techniques for maximizing Claude's performance:

- **CLAUDE.md architecture** — Hierarchical project instructions that scale across teams
- **Skill composition** — Breaking complex tasks into focused, reusable skill files
- **Dynamic context loading** — Loading relevant context based on task type
- **Structured output schemas** — Ensuring consistent, parseable outputs from Claude

### 4. Browser Automation with Claude Code

Production patterns for browser automation using Playwright orchestrated by Claude Code:

- Persistent browser profiles for authenticated sessions
- Self-healing selectors with AI-powered fallbacks
- Multi-step form submission and data extraction
- Screenshot verification loops

### 5. Production Deployment Patterns

Taking Claude Code projects from prototype to production:

- CI/CD integration with Vercel
- Environment variable management
- Pre-commit hooks for security scanning (gitleaks)
- Git workflow automation

---

## Architecture Philosophy

**Simple beats clever.** Every pattern here follows three rules:

1. **It solves a real problem** — extracted from production use, not imagined scenarios
2. **It's the simplest version that works** — no premature abstraction
3. **It fails gracefully** — explicit error handling, not silent failures

This comes from 5 years of coaching people through behavior change: the best system is the one people actually use. Complex systems get abandoned. Simple systems compound.

---

## Tech Stack

| Tool | Role |
|------|------|
| **Claude Code** | Primary development environment, agentic orchestration |
| **Claude API** | Programmatic access for content generation and evaluation |
| **n8n** | Workflow automation and API orchestration |
| **Playwright** | Browser automation for web workflows |
| **Python** | Scripting, API integrations, data processing |
| **TypeScript** | Web applications, tooling |
| **Astro + Vercel** | Web deployment |

---

## Related Projects

- **[AAA Authority Acceleration](https://github.com/zach-lloyd-dev/aaa-authority-acceleration)** — 23 modular Claude Code skills for content automation. 13 stars, MIT licensed.
- **[Gym Lead Chatbot](https://github.com/zach-lloyd-dev/gym-lead-chatbot)** — AI-powered lead qualification widget built with Claude.

---

## About

I'm Zach Lloyd — founder of [Black Sheep Systems](https://zach-lloyd.com), an AI automation consultancy. I build autonomous systems for small business owners using Claude Code, n8n, Playwright, and Python.

Previously: 5 years as a fitness coach and gym owner, where I learned that sustainable systems beat flashy solutions every time. That philosophy drives everything I build.

[![YouTube](https://img.shields.io/badge/YouTube-@blacksheepsystems-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://youtube.com/@blacksheepsystems)
[![X](https://img.shields.io/badge/X-@zachlloydai-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/zachlloydai)
