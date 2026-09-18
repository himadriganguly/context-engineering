---
name: context-engineering
description: Diagnose, optimize, and maintain an agent's context window. Use when output quality degrades, sessions feel bloated, the agent ignores instructions, token costs spike, or when starting a new project that needs a deliberate context architecture. Covers progressive disclosure, degradation signals, token budgeting, and context profiling.
license: MIT
compatibility: Works with any Agent Skills-compatible runtime (Hermes, Claude Code, Cursor, Codex, OpenClaw, Gemini CLI). Requires terminal access for scripts.
metadata:
  author: context-engineering-community
  version: "1.0.0"
  category: agent-infrastructure
  tags:
    - context
    - token-management
    - agent-optimization
    - progressive-disclosure
    - performance
---

# Context Engineering

Context is the agent's working memory. When it degrades, every
downstream capability degrades with it — reasoning, tool selection,
instruction-following, and output quality. This skill gives the agent a
structured procedure for diagnosing, measuring, and repairing its own
context.

## When to Use

Load this skill when any of these signals appear:

- **Output quality drop** — responses become vague, repetitive, or
  miss constraints that were clearly stated earlier.
- **Instruction drift** — the agent stops following rules from
  AGENTS.md, system prompt, or earlier turns.
- **Token cost spike** — per-turn token usage grows without a
  corresponding increase in task complexity.
- **"Lost in the middle"** — the agent ignores information placed in
  the center of a long context.
- **New project setup** — you want to architect context deliberately
  from the start rather than accumulate cruft.
- **Skill overload** — too many skills are loaded, or a skill's
  description is misleading the agent into loading the wrong one.
- **Session handoff** — you need to compress a long session into a
  resume brief that preserves decisions, not narration.

Do **not** use this skill for prompt engineering (wording of a single
instruction), model selection, or fine-tuning. Those are separate
concerns.

## Procedure

### Step 1 — Audit the current context

Run the audit script to get a quantitative picture before making
changes.

```bash
python scripts/context_audit.py --session-dir "$HERMES_SESSION_DIR"
```

Replace `$HERMES_SESSION_DIR` with the path to your runtime's session
directory. If you do not know it, check your runtime's documentation,
or run the audit against a directory that contains the session
artifacts in the expected layout (see
`references/token-budget-framework.md` for the layout).

The script reports six metrics:

- **Total tokens** — the sum of all content in context.
- **Window utilization** — total divided by the window size.
- **Instruction survival rate** — the fraction of user constraints
  still findable in the effective context.
- **Stale content ratio** — the fraction of conversation that is no
  longer relevant to the active task.
- **Repetition ratio** — the fraction of duplicated content.
- **Top contributors** — the ten largest blocks of context.

If the script cannot find a session directory, run the estimator on
the project to get a picture of the static context:

```bash
python scripts/token_estimator.py --dir . --recursive --top 20
```

This does not replace the audit, but it tells you which files are the
biggest consumers.

### Step 2 — Classify the degradation

Use the audit numbers to classify the failure into one of five known
modes. The full taxonomy — with signals, sources, and fixes for each
— is in `references/degradation-signals.md`. Load that file when you
reach this step.

| Class | Primary signal | Typical cause |
|---|---|---|
| **Poisoning** | The agent cites a wrong fact consistently | A hallucinated or outdated statement entered context and was never corrected |
| **Clash** | The agent oscillates between contradictory instructions | Two sources give conflicting rules |
| **Confusion** | The agent references irrelevant details from earlier turns | Stale content is being treated as relevant |
| **Lost-in-middle** | The agent ignores mid-context instructions | Attention degrades with position; critical rules sit in the middle |
| **Overload** | The agent truncates, summarizes poorly, or skips steps | The context window is near capacity |

Record the primary class and any secondary class. A single session can
exhibit more than one. When multiple classes are present, fix
**Overload** first — it amplifies every other failure mode.

### Step 3 — Apply the structural fix

Most context problems are structural, not informational. The fix is
almost never "reword the prompt." It is "move content to the right
tier, compress history to a brief, or cache large tool output to
disk."

Load `references/progressive-disclosure-patterns.md` for the six
reusable patterns. In order of applicability:

1. **Extract stable knowledge into `references/`.** Anything that is
   true across sessions (architecture, conventions, decision logs)
   belongs in a reference file, not in the system prompt. The agent
   loads it only when the task touches that domain.

2. **Compress conversation history to a resume brief.** Replace raw
   turn logs with a structured brief capturing decisions, constraints,
   open questions, files touched, and the active sub-task. After 20
   turns, or whenever history exceeds 30,000 tokens, compress.

3. **Summarize tool outputs larger than 2,000 tokens.** Extract only
   the fields the task needs, diff against existing context, chunk
   into sections, or cache the full output to disk with a one-line
   summary in context.

4. **Tighten skill descriptions.** A skill's `description` field is
   the agent's only signal for when to load it. Name explicit trigger
   and anti-trigger conditions.

5. **Use conditional activation.** If the runtime supports
   `fallback_for_toolsets` or `requires_toolsets`, use them. A skill
   that only applies when a tool is unavailable should not occupy
   space when the tool is present.

6. **Re-inject critical rules.** In long sessions, repeat the most
   important constraints periodically, or have the runtime re-inject
   them at the top of every turn.

### Step 4 — Rebuild the context profile

Create or update `context-profile.yaml` in the project root. This file
declares the context architecture: which files live in which tier,
what the token budget is for each tier, what rules resolve conflicts,
and what triggers fire when degradation is detected.

Use `templates/context-profile.yaml` as the starting point. Copy it
into the project root and edit it to match the project. The full
reasoning behind the budgets is in
`references/token-budget-framework.md`.

This step is what prevents the fix from being a one-time bandage. The
profile encodes the fix as a rule that applies to every future
session.

### Step 5 — Verify the fix

Re-run the audit after applying the changes.

```bash
python scripts/context_audit.py --session-dir "$HERMES_SESSION_DIR" --compare
```

The `--compare` flag shows the delta between the two most recent
audit reports. The comparison should show:

- **Total tokens down.** The fix should reduce total context.
- **Instruction survival up.** Constraints should be more findable.
- **Stale content down.** Less dead weight.
- **Repetition down.** Less duplication.
- **Task quality unchanged or improved.** If the numbers improved but
  task quality regressed, the diagnosis was wrong. Re-classify and
  repeat from Step 2.

Record the before/after numbers in `references/decision-log.md` (if
the project has one) so future sessions can see what worked.

## Pitfalls

Five mistakes that make context problems worse, not better.

### 1. Summarizing too aggressively

A resume brief that drops a constraint the agent later needs is worse
than a bloated context. Always include the "Constraints discovered"
section, even if it feels redundant. When in doubt, keep the
constraint.

### 2. Treating all references as equal

A reference file that is loaded on every turn is not a reference — it
is a system prompt. If a file is loaded more than 50% of turns, move
it to `always_on` or merge it into `AGENTS.md`.

### 3. Ignoring tool output size

A single `read_file` on a large source file can consume 30% of the
context window. Twelve log files can fill the window entirely.
Summarize or chunk tool outputs before they enter context. Use
`token_estimator.py` to predict the cost before the read.

### 4. Fixing symptoms instead of structure

If the agent ignores mid-context instructions, moving those
instructions to the end of the context helps once. The structural fix
is to reduce total context length so position matters less. Apply the
structural fix, not the workaround.

### 5. Forgetting that skills are context too

Every loaded skill consumes tokens. A session with 12 loaded skills
has less room for the actual task. Use skill bundles or conditional
activation to load only what the task needs. If the skill index
exceeds 5,000 tokens, you have too many skills active.

## Verification

A context-engineering intervention is successful when:

1. **The audit shows improvement** on at least two of: total tokens,
   instruction survival rate, stale-content ratio, repetition ratio.

2. **Task quality does not regress.** Run the same task before and
   after the fix and compare the output against the task's acceptance
   criteria.

3. **The agent can state its constraints.** Ask the agent "What are
   the three most important constraints for this task?" If it cannot
   answer from context, the constraints are not surviving.

4. **New sessions start clean.** A fresh session with the same
   `context-profile.yaml` should reach the same quality with less
   context than before.

Record the before/after audit numbers in `references/decision-log.md`
so future sessions can see what worked.

## Notes on Interpretation

Three things that are easy to misread when using this skill.

### The metrics are proxies, not exact measurements

Instruction survival is measured by string matching against a fixed
set of imperative verbs. Stale content is measured by vocabulary
overlap between old and recent turns. Repetition is measured by
n-gram counting. None of these are semantic analyses. They are
proxies — fast, consistent, and useful for detecting trends. Use them
to decide *whether* something is wrong, not to decide *what* the
exact cause is.

### The thresholds are defaults, not laws

The degradation triggers in the skill (`instruction_survival < 0.7`,
`stale_content_ratio > 0.4`, etc.) are conservative defaults. They
work for most projects. Tighten them for quality-critical sessions;
loosen them for exploratory work. The right threshold is the one that
catches the failure before it affects output.

### Headroom is not optional

A context that is 100% full performs worse than one that is 70% full.
This is not a guideline — it is a consequence of how attention works.
Never let total utilization exceed 80% of the window. The last 20% is
the space the model uses to reason, and if you take it away, quality
drops non-linearly.

## Reference Files

Load these on demand, as you reach the corresponding step.

| File | Load when |
|---|---|
| `references/degradation-signals.md` | Classifying the failure (Step 2) |
| `references/progressive-disclosure-patterns.md` | Applying the fix (Step 3) |
| `references/token-budget-framework.md` | Rebuilding the profile (Step 4) |

## Scripts

Both scripts use only the Python standard library. No `pip install`
step. Require Python 3.9+.

### `scripts/context_audit.py`

Produce a quantitative audit report for a session directory.

```bash
python scripts/context_audit.py --session-dir PATH   # human-readable
python scripts/context_audit.py --session-dir PATH --json   # JSON
python scripts/context_audit.py --session-dir PATH --compare   # delta
```

Reports are saved to `~/.hermes/context-audit/` with a timestamped
filename. The `--compare` flag uses the two most recent reports.

### `scripts/token_estimator.py`

Predict token cost of text, a file, or a directory.

```bash
python scripts/token_estimator.py --text "string"
python scripts/token_estimator.py --file path/to/file
python scripts/token_estimator.py --dir . --recursive --top 20
```

The estimator uses a calibrated heuristic of 3.8 characters per token.
It is accurate to within ±10% and consistent across files, which is
what budgeting decisions require.

## Summary

Five steps, five failure modes, three reference files, two scripts.
The procedure is the same for every context problem, whether the
session is three hours old or five days old, whether the failure is
instruction drift or outright hallucination.

1. **Measure** the current state.
2. **Name** the failure mode.
3. **Apply** the structural fix.
4. **Encode** the fix in `context-profile.yaml`.
5. **Verify** the numbers improved and quality did not regress.

The specific fixes differ. The procedure does not. That is the point.