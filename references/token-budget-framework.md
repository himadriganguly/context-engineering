# Token Budget Framework

Every context window has a fixed size. Every piece of content in that
window costs tokens. A token budget is a plan for how to spend them.

Without a budget, context grows by accumulation — every tool output,
every reference file, every skill gets added and nothing is ever
removed. The window fills up, and quality degrades.

With a budget, context grows by design. Each tier has a target, each
target has an enforcement rule, and the agent knows when to stop and
compress.

---

## Measuring

Before you can budget, you must measure. Use the token estimator to
find the cost of any text, file, or directory.

### Single string

```bash
python scripts/token_estimator.py --text "your string here"
```

Output:

```
42 tokens
```

### Single file

```bash
python scripts/token_estimator.py --file references/architecture.md
```

Output:

```
3,247 tokens  (references/architecture.md)
```

### Directory scan

```bash
python scripts/token_estimator.py --dir . --recursive --top 20
```

Output:

```
Total: 87,432 tokens across 156 files

    Tokens  File
    ------  --------------------------------------------------
    12,481  conversation_history.jsonl
     8,203  tool_outputs/large-log.txt
     6,942  references/architecture.md
     5,118  references/api-conventions.md
     ...
```

### Calibration

The estimator uses a character-based heuristic: approximately 3.8
characters per token for blended English prose and code. This is
calibrated to common tokenizers (GPT-4, Claude, Llama) and is accurate
to within ±10% for typical content.

It is **not** exact. It is **consistent.** Use it for relative
comparison — "is this file bigger than that one?" — not for
billing-grade accounting.

If you need exact counts, replace `CHARS_PER_TOKEN` in the script
with the value for your specific tokenizer, or pipe the text through
a real tokenizer library.

### When to measure

- **At session start** — get a baseline. What is the current
  utilization?
- **Every 10 turns** — has anything grown beyond its tier?
- **Before loading a large file** — will this push utilization over
  80%?
- **After any compression** — did the fix actually reduce tokens?

---

## Allocating the Budget

The following budget is calibrated for a **128k-token context window**,
which is common for 2026 frontier models. Adjust proportionally for
smaller or larger windows.

| Tier | Budget | Purpose |
|---|---|---|
| System prompt | 4k | Identity, rules, tool schemas |
| Skill index | 3k | Names and descriptions of available skills |
| Always-on context | 6k | AGENTS.md, active task, constraints |
| On-demand references | 40k | Loaded only when relevant |
| Conversation history | 20k | Compressed to resume brief after 20 turns |
| Tool outputs | 25k | Summarized if >2k per output |
| **Headroom** | **30k** | **Model reasoning, unexpected loads** |

**Total: 128k**

### Why these proportions

- **Headroom is 23% of the window.** Non-negotiable. A context that is
  100% full performs worse than one that is 70% full, because the
  model has no room to reason. Never allocate the last 20% of the
  window.
- **On-demand references are the largest single tier.** This is where
  the project's deep knowledge lives. It can be large because it is
  not all loaded at once — only the relevant portion.
- **Conversation history is capped at 20k.** Beyond that, compress to
  a resume brief. Raw history is the worst use of tokens because it
  contains mostly narration, not decisions.
- **Tool outputs are capped at 25k.** Any single output larger than
  2k must be summarized before entering context.

### Smaller windows

For a 32k-token window (common for smaller or older models):

| Tier | Budget |
|---|---|
| System prompt | 2k |
| Skill index | 1k |
| Always-on context | 2k |
| On-demand references | 8k |
| Conversation history | 6k |
| Tool outputs | 5k |
| Headroom | 8k |

The proportions are similar. The absolute numbers scale down.

For an 8k-token window, context engineering is not optional — it is
the entire game. Every token must be justified. Use the resume brief
pattern aggressively, cache all tool outputs to disk, and load
reference files by section rather than whole.

---

## Enforcement Rules

A budget that is not enforced is not a budget. These rules are the
enforcement mechanism.

### Rule 1 — Skill index

> **If the skill index exceeds 5k tokens, you have too many skills
> installed.**

Each skill's description is a fixed cost that is paid on every turn.
A 12-skill setup with 400-token descriptions each costs 4.8k tokens
of every context, just to advertise availability.

**Fix:** Use conditional activation (`fallback_for_toolsets`,
`requires_toolsets`, or `auto_load: false`). Skills that do not apply
to every session should not be in the always-on index.

### Rule 2 — Always-on context

> **If the always-on context exceeds 10k tokens, you are putting
> reference material in the system prompt.**

The always-on tier is for identity, active task, and hard constraints.
Anything else belongs in `on_demand`. A 15k always-on tier means
10k tokens of context are being paid on every turn for content that
is only relevant sometimes.

**Fix:** Move stable knowledge into `references/`. Keep the always-on
tier lean: project name, active task, hard constraints, and nothing
else.

### Rule 3 — Single tool output

> **If a single tool output exceeds 5k tokens, summarize it before it
> enters context.**

A 50,000-line log file is not context — it is a haystack. Pasting it
into the window consumes 13% of a 128k budget and provides almost no
useful signal. The useful information is 200 tokens of summary:
timestamp range, error counts, unique signatures.

**Fix:** Apply the tool output summarization pattern. Extract, diff,
chunk, or cache. Never paste the raw output of a large file read.

### Rule 4 — Conversation history

> **If conversation history exceeds 30k tokens, compress to a resume
> brief.**

Raw conversation history is the fastest-growing tier and the least
efficient. Most turns are narration ("I read the file, then I...")
that will never be referenced again. Compressed into a resume brief,
the same decisions and constraints fit in 1,000–2,000 tokens.

**Fix:** After 20 turns, or whenever history exceeds 30k, replace the
raw log with a structured resume brief. Include decisions,
constraints, open questions, files touched, and the active sub-task.
Exclude narration and raw tool output.

### Rule 5 — Total utilization

> **If total context exceeds 80% of the window, stop and compress
> before continuing.**

This is the hard ceiling. At 80% utilization, the model still has
headroom to reason. Above 80%, quality degrades non-linearly: the
model starts dropping information to fit, and the dropped information
is often the most important (the constraints, the corrections, the
rules).

**Fix:** Stop the current task. Run the audit. Apply compression
before continuing. Do not push through at 90% utilization and hope
for the best — the degradation compounds.

---

## Healthy vs. Unhealthy Profiles

Two audit reports, side by side. The difference is stark.

### Healthy profile

```json
{
  "total_tokens": 42000,
  "window_size": 128000,
  "utilization": 0.33,
  "instruction_survival_rate": 0.92,
  "stale_content_ratio": 0.08,
  "repetition_ratio": 0.04,
  "top_contributors": [
    {"source": "conversation", "tokens": 14000},
    {"source": "tool_output", "tokens": 12000},
    {"source": "skill_index", "tokens": 2800}
  ]
}
```

**Why it is healthy:**

- Utilization is 33%. There is ample headroom.
- Instruction survival is 92%. Almost all constraints are still
  findable.
- Stale content is 8%. Very little dead weight.
- Repetition is 4%. Almost no duplication.
- No single contributor dominates. The context is balanced.

### Unhealthy profile

```json
{
  "total_tokens": 112000,
  "window_size": 128000,
  "utilization": 0.875,
  "instruction_survival_rate": 0.54,
  "stale_content_ratio": 0.42,
  "repetition_ratio": 0.31,
  "top_contributors": [
    {"source": "conversation", "tokens": 58000},
    {"source": "tool_output", "tokens": 34000},
    {"source": "system_prompt", "tokens": 9200}
  ]
}
```

**Why it is unhealthy:**

- Utilization is 87.5%. Above the 80% ceiling.
- Instruction survival is 54%. Nearly half the constraints are lost.
- Stale content is 42%. Almost half the context is dead weight.
- Repetition is 31%. The agent is repeating itself.
- The conversation is 58k tokens — nearly double the 30k cap.
- The system prompt is 9.2k — above the 4k budget, meaning
  reference material has leaked into it.

Every one of these is a signal. Every one is fixable with the
procedures in this skill.

### Reading a profile at a glance

| Metric | Healthy | Warning | Critical |
|---|---|---|---|
| Utilization | < 0.5 | 0.5–0.8 | > 0.8 |
| Instruction survival | > 0.9 | 0.7–0.9 | < 0.7 |
| Stale content | < 0.15 | 0.15–0.4 | > 0.4 |
| Repetition | < 0.1 | 0.1–0.3 | > 0.3 |

If any metric is in the "critical" column, apply the corresponding
fix immediately. If two or more are critical, the session is in
trouble — compress aggressively before continuing.

---

## Monitoring Over Time

A single audit is a snapshot. A series of audits is a trend. Trends
catch problems that snapshots miss.

The audit script writes each report to `~/.hermes/context-audit/`
with a timestamp in the filename:

```
~/.hermes/context-audit/
├── audit-20260115-093000.json
├── audit-20260115-110000.json
├── audit-20260115-133000.json
└── audit-20260115-150000.json
```

Run with `--compare` to see the delta between the two most recent
reports:

```bash
python scripts/context_audit.py --session-dir . --compare
```

Output:

```
=== Context Audit Comparison ===

  total_tokens: 112400 → 38200  (↓ 74200.000)
  utilization: 0.878 → 0.298  (↓ 0.580)
  instruction_survival_rate: 0.54 → 0.96  (↑ 0.420)
  stale_content_ratio: 0.42 → 0.07  (↓ 0.350)
  repetition_ratio: 0.31 → 0.04  (↓ 0.270)
```

The arrows make the direction of improvement obvious. For
`instruction_survival_rate`, higher is better (↑). For the other
four, lower is better (↓).

### What to watch for

- **A rising utilization trend.** Even if utilization is currently
  fine, a steady upward trend means the session is accumulating
  content faster than it is being cleaned. Intervene before the
  trend crosses 80%.
- **A falling instruction survival trend.** This is the earliest
  warning sign. By the time the agent visibly ignores instructions,
  survival has usually been dropping for several turns.
- **A rising repetition trend.** Repetition usually indicates that
  content is being loaded from multiple sources (duplication) or that
  the agent is looping. Either way, intervene.

### Frequency

- **At session start** — always. Establishes the baseline.
- **Every 10 turns** — during long sessions. Catches drift early.
- **Before any large load** — reading a big file, loading a
  reference, adding a skill. Prevents overload before it happens.
- **After any compression** — verify the fix worked.

---

## Applying the Budget to a New Project

When starting a new project, build the budget first, then populate it.

### Step 1 — Declare the profile

Copy `templates/context-profile.yaml` into the project root. Fill in
the tier definitions:

```yaml
version: 1

project:
  name: "my-project"
  description: "One-line description."

tiers:
  always_on:
    files:
      - AGENTS.md
      - context/task.md
    budget_tokens: 6000

  on_demand:
    files:
      - references/architecture.md
      - references/api-conventions.md
      - references/decision-log.md
    budget_tokens: 40000

  ephemeral:
    budget_tokens: 20000
```

### Step 2 — Populate each tier

- **Always-on** — write `AGENTS.md` and `context/task.md`. Keep
  them short. If either exceeds 3k tokens, split it.
- **On-demand** — write the reference files. Apply the reference
  file structure pattern (Quick Reference at top).
- **Ephemeral** — nothing to write. This tier is filled at runtime
  by tool output and recent turns.

### Step 3 — Verify

Run the estimator against the project:

```bash
python scripts/token_estimator.py --dir . --recursive --top 20
```

Check that:

- `AGENTS.md` and `context/task.md` together are under 6k.
- No single reference file exceeds 5k.
- The sum of `always_on` + a typical `on_demand` load is under 50k.

### Step 4 — Add degradation triggers

Add rules to the profile that fire when budgets are exceeded:

```yaml
degradation_triggers:
  - signal: "instruction_survival_rate < 0.7"
    action: "Compress history. Re-state constraints."
  - signal: "stale_content_ratio > 0.4"
    action: "Drop tool outputs older than 10 turns."
  - signal: "repetition_ratio > 0.3"
    action: "Deduplicate reference files."
  - signal: "utilization > 0.8"
    action: "Stop. Compress before continuing."
```

### Step 5 — Commit the profile

The `context-profile.yaml` is part of the project. It goes into
version control. It is reviewed like code. When the budget changes,
the change is a commit, with a rationale.

This is what makes the budget enforceable: it is a declared,
versioned artifact, not a vague intention.

---

## Summary

| Concept | Rule |
|---|---|
| **Measure** | Run `token_estimator.py` before loading anything large |
| **Allocate** | Follow the tier table; never allocate the last 20% |
| **Enforce** | 5 rules — skill index, always-on, tool output, history, utilization |
| **Monitor** | Audit at session start, every 10 turns, after compression |
| **Apply** | Build the budget first, then populate it |

The token budget is the structural fix for Overload. The other
patterns in this skill are the structural fixes for the other four
degradation classes. Together they form a complete context
architecture.