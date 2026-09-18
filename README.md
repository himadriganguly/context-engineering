# Context Engineering — An Agent Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blue)](https://agentskills.io)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](CHANGELOG.md)
[![Validate skill](https://github.com/himadriganguly/context-engineering/workflows/Validate%20skill/badge.svg)](https://github.com/himadriganguly/context-engineering/actions/workflows/validate.yml)

**The missing meta-skill for AI agents.** Teaches any Agent
Skills–compatible agent how to diagnose, optimize, and maintain its own
context window — the working memory that determines whether every other
skill works or fails.

---

## The Problem

AI agents have a fixed-size working memory called a **context window**.
As a session grows — more turns, more file reads, more tool output,
more loaded skills — that memory fills up.

When it does, the agent does not crash. It quietly gets worse:

- It forgets your instructions.
- It mixes up details from three tasks ago.
- It ignores rules buried in the middle of the conversation.
- It repeats itself.
- It invents facts when it cannot find the real ones.

Industry reports in 2026 consistently name **context engineering** as
the number-one unmet skill for people building AI agents. Every team
hits the same wall. Almost nobody has a systematic way to fix it.

This project fills that gap. It is a complete, open-source,
MIT-licensed toolkit — not a blog post, not a set of tips, but a
working skill that any agent can load and apply.

## What You Get

| Component | Purpose |
|---|---|
| `SKILL.md` | The core procedure — a five-step workflow the agent follows |
| `scripts/context_audit.py` | Measures token usage, instruction survival, staleness, repetition |
| `scripts/token_estimator.py` | Predicts token cost of any text, file, or directory |
| `references/degradation-signals.md` | Full taxonomy of the five context failure modes |
| `references/progressive-disclosure-patterns.md` | Six reusable patterns for keeping context small |
| `references/token-budget-framework.md` | Budget allocation and enforcement rules |
| `templates/context-profile.yaml` | Declarative context architecture for any project |
| `EXAMPLES.md` | Five real-world case studies with measurable outcomes |
| `INSTALL.md` | Step-by-step installation for seven runtimes |

Everything is plain Markdown and standalone Python. No external
dependencies. No lock-in. No telemetry. No paywall.

---

## The Five-Step Procedure

The skill teaches the agent to:

1. **Audit** — run a script that measures six metrics about the current
   session: total tokens, window utilization, instruction survival
   rate, stale content ratio, repetition ratio, and top contributors.

2. **Classify** — match the numbers to one of five known failure modes:
   poisoning, clash, confusion, lost-in-middle, or overload.

3. **Fix** — apply the structural fix for that failure mode. The fix
   is almost never "reword the prompt." It is "move content to the
   right tier, compress history to a brief, or cache large tool
   output to disk."

4. **Rebuild** — write the fix into `context-profile.yaml` so it
   persists across sessions. The fix becomes part of the project's
   architecture, not a one-time bandage.

5. **Verify** — re-run the audit and confirm the numbers improved
   without task quality regressing.

This is the same procedure whether you are debugging a three-hour
coding session, a 30-turn customer support conversation, or a
five-day product spec.

---

## Quick Install

### Hermes Agent

```bash
mkdir -p ~/.hermes/skills
cp -r context-engineering ~/.hermes/skills/
```

Restart the agent. The skill is now available.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r context-engineering ~/.claude/skills/
```

### Cursor

```bash
mkdir -p ~/.cursor/skills
cp -r context-engineering ~/.cursor/skills/
```

### Everything else

Any runtime that follows the [Agent Skills specification](https://agentskills.io)
uses the same idea: copy the `context-engineering/` directory into
the runtime's skills path. Full instructions for seven runtimes —
including Codex, Gemini CLI, OpenClaw, and generic fallbacks — are in
[INSTALL.md](INSTALL.md).

---

## Try It

Once installed, trigger the skill by asking your agent something like:

> "My session feels bloated and you're ignoring my earlier
> instructions. Use the context-engineering skill to diagnose and fix
> it."

The agent will:

1. Run the audit script against the current session.
2. Read the numbers.
3. Classify the failure mode.
4. Apply the structural fix.
5. Verify the fix worked.

You can also invoke the scripts directly, without involving the agent:

```bash
# Audit the current session
python3 scripts/context_audit.py --session-dir ~/.hermes/sessions/current

# Estimate the token cost of a file before loading it
python3 scripts/token_estimator.py --file references/architecture.md

# Find the largest files in a project
python3 scripts/token_estimator.py --dir . --recursive --top 20
```

The scripts are useful on their own, even if you never load the skill
into an agent.

---

## Why This Exists

The idea for this skill came from a specific observation:

**Every agent developer hits the same wall at roughly the same point.**

The wall looks like this: the agent works fine for 20 turns, then
starts to drift. By turn 50, it is missing constraints it followed
perfectly at turn 5. By turn 100, it is inventing facts.

The wall is not a bug in any particular runtime. It is a fundamental
property of how attention works in transformer models. The context
window is not a database. It is a working memory with known
limitations: attention degrades with position, information gets
crowded out, and quality drops non-linearly as the window fills.

The fix is not a better model. It is **context engineering** — a
discipline of deliberately curating what goes into the window, when,
and in what form.

This skill packages that discipline into something an agent can apply
to itself.

---

## What Makes This Different

Several projects address pieces of the problem. Most fall into one of
three categories:

- **Blog posts and papers** — describe the problem well but do not
  provide a tool an agent can use.
- **Framework-specific features** — locked to one runtime, not
  portable.
- **Partial solutions** — cover one technique (summarization,
  retrieval, compression) but not the whole lifecycle.

This project is different in four ways:

### 1. It is a complete lifecycle

Not just compression, not just measurement, not just a taxonomy.
Diagnosis, classification, fix, prevention, and verification — the
whole cycle, in a single skill.

### 2. It is runtime-agnostic

Pure Markdown plus standalone Python. No frameworks, no dependencies,
no lock-in. Works on Hermes, Claude Code, Cursor, Codex, Gemini CLI,
OpenClaw, and anything else that implements the Agent Skills
specification.

### 3. It is measurable

The skill does not say "the agent will be more reliable." It says "the
audit will show instruction survival above 0.9 and utilization below
0.5." Every claim is backed by a metric the user can verify.

### 4. It is recursive

The skill uses the techniques it teaches. `SKILL.md` is a compact
quick reference; the deep knowledge lives in `references/` and is
loaded on demand. The structure of the skill is itself a demonstration
of progressive disclosure.

---

## Who This Is For

- **Agent developers** who want their agents to stay sharp across
  long sessions.
- **Prompt engineers** moving from "write better prompts" to
  "architect context."
- **Teams** running agents in production where token cost and quality
  both matter.
- **Researchers** who need their agents to cite sources correctly.
- **Anyone** building on the Agent Skills standard who wants a
  foundation skill.

You do not need to be an expert in transformers or attention
mechanisms. The skill is written in plain language. The scripts run
with a single command. The concepts — window, tier, budget, brief —
are intuitive.

---

## Compatibility

| Runtime | Status | Skills path |
|---|---|---|
| Hermes Agent (Nous Research) | ✅ Tested | `~/.hermes/skills/` |
| Claude Code | ✅ Tested | `~/.claude/skills/` |
| Cursor | ✅ Tested | `~/.cursor/skills/` |
| OpenAI Codex | ✅ Expected | `~/.codex/skills/` |
| Gemini CLI | ✅ Expected | `~/.gemini/skills/` |
| OpenClaw | ✅ Expected | `~/.agent-skills/` |
| Custom runtime | ✅ Expected | Any path the runtime scans |

Requirements:

- **Python 3.9 or later** for the scripts. No `pip install` step.
- **Any Agent Skills–compatible runtime** for the skill itself.

The skill has been tested against Hermes, Claude Code, and Cursor.
The other runtimes are expected to work but have not been formally
validated. If you test on a runtime that is not listed, please open
an issue with the result.

---

## Principles

Four beliefs that shape every decision in this project.

### 1. Measure before fixing

An audit without numbers is an opinion. The scripts produce numbers.
Every claim about improvement is backed by a before/after comparison.

### 2. Structure beats tricks

No single prompt hack fixes context problems. The fix is architectural
— moving content to the right tier, compressing it into a brief,
caching it to disk. Structure scales. Tricks do not.

### 3. Headroom is sacred

A context that is 100% full performs worse than one that is 70% full.
The last 20% of the window is not waste — it is the space the model
uses to reason. Never allocate it.

### 4. Skills are context too

Every loaded skill costs tokens. A session with 12 skills loaded has
less room for the actual task. Load only what the task needs. Unload
what it does not.

---

## Examples

Five real-world case studies in [EXAMPLES.md](EXAMPLES.md). A quick
preview:

| Example | Primary failure | Key fix | Before → After |
|---|---|---|---|
| Long coding session | Overload + lost-in-middle | Resume brief | 112k → 38k tokens |
| Customer support drift | Lost-in-middle | Policy re-injection | 12 → 0 violations |
| Research assistant | Confusion | Paper index | 4 → 0 hallucinations |
| DevOps incident | Overload | Emergency compression | 45 min → 12 min |
| Multi-day project | Confusion across sessions | Session bookends | 15 min → 30 sec |

Each case study includes the symptom, the actual audit output, the
fix applied, and before/after metrics.

---

## Project Structure

```
context-engineering-skill/
├── .github/
│   └── workflows/
│       └── validate.yml                    # CI: validates frontmatter + runs scripts
├── examples/
│   └── README.md                           # Index for the case studies
├── references/
│   ├── degradation-signals.md              # Taxonomy of the 5 failure modes
│   ├── progressive-disclosure-patterns.md  # 6 patterns for keeping context small
│   └── token-budget-framework.md           # Budget allocation + enforcement
├── scripts/
│   ├── context_audit.py                    # Produces the quantitative audit
│   └── token_estimator.py                  # Pre-flight cost estimator
├── templates/
│   └── context-profile.yaml                # Declarative context architecture
├── .gitignore
├── CHANGELOG.md                            # Version history
├── CONTRIBUTING.md                         # Contribution guide
├── EXAMPLES.md                             # 5 real-world case studies
├── INSTALL.md                              # Install for 7 runtimes
├── LICENSE                                 # MIT
├── README.md                               # This file
├── SKILL.md                                # The core procedure
└── UPLOAD.md                               # How to publish to GitHub
```

The agent only ever loads `SKILL.md` up front. Everything else in
`references/` loads on demand. The scripts execute rather than load.
This is progressive disclosure applied to the skill's own structure.

---

## Roadmap

Features under consideration for future releases. Not commitments —
directions the project could grow in.

- A web-based viewer that renders `audit-*.json` reports as charts
  over time.
- A `--watch` mode for `context_audit.py` that re-runs automatically
  when the session directory changes.
- Reference file templates for common domains (API, database, ML,
  frontend).
- Translations of `SKILL.md` into Spanish, French, German, Japanese,
  and Mandarin.
- A `context-profile.schema.json` for editor autocomplete and
  validation.
- Direct API integrations with Hermes, Claude Code, and Cursor to read
  session state without requiring a session directory.

If any of these interest you, open an issue to discuss the approach
before writing code.

---

## Contributing

Contributions are welcome. The most valuable ones are:

- **New degradation patterns** — a failure mode not covered by the
  existing five.
- **Real-world case studies** — concrete numbers beat abstract advice.
- **New runtime support** — install instructions for a runtime not yet
  listed.
- **Translations** — the skill is used worldwide.

See [CONTRIBUTING.md](CONTRIBUTING.md) for what we want, what we do not
want, and how to submit.

A few non-obvious constraints:

- No external Python dependencies. The scripts must run on a bare
  Python 3.9+ install.
- No runtime-specific hacks in `SKILL.md`. Runtime-specific behavior
  goes in `metadata` or in a reference file.
- Any change that increases the always-on cost of the skill must
  justify the increase. That cost is multiplied by every session of
  every user.

---

## License

MIT. Use it, fork it, ship it, sell it, embed it in your product.
Attribution is appreciated but not required.

See [LICENSE](LICENSE) for the full text.

---

## Acknowledgments

This skill was created in response to a widely observed gap in the
2026 agent ecosystem. It draws on:

- The [Agent Skills specification](https://agentskills.io) for the
  file format and loading semantics.
- The Hermes Agent skills documentation for runtime conventions.
- Public discussions of context window degradation across the
  agent-development community.
- The [Keep a Changelog](https://keepachangelog.com/) and
  [Semantic Versioning](https://semver.org/) projects, whose formats
  this repository follows.

Thanks to everyone who has contributed failure modes, case studies,
and corrections. The project is better because of you.

---

## Related Reading

If you want to understand the underlying problem more deeply:

- **"Lost in the Middle: How Language Models Use Long Contexts"** —
  the paper that named the attention-degradation pattern this skill
  addresses.
- **The Agent Skills specification** —
  https://agentskills.io — the standard this skill conforms to.
- **The Hermes Agent documentation** —
  https://hermes-agent.nousresearch.com/docs — for runtime-specific
  details on skill loading.

The skill is not a substitute for understanding the underlying
mechanisms. It is a working tool that encodes the current best
practices for dealing with them. When the understanding improves, the
tool should too.

---

**Status:** v1.0.0 — stable, tested on three runtimes, used in
production by the maintainers. Issues and pull requests welcome.