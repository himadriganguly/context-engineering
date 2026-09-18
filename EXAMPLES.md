# Real-World Examples

Five concrete scenarios showing how the context-engineering skill
solves problems that otherwise cost hours of debugging, wasted tokens,
and degraded output quality.

Each example follows the same arc: **the symptom, the audit, the fix,
the outcome.**

The details differ. The procedure does not. That is the point of the
skill: turn a vague, hard problem into a repeatable procedure.

---

## Table of Contents

- [Example 1 — The Long Coding Session That Forgot Its Architecture](#example-1--the-long-coding-session-that-forgot-its-architecture)
- [Example 2 — The Customer Support Agent That Drifts From Policy](#example-2--the-customer-support-agent-that-drifts-from-policy)
- [Example 3 — The Research Assistant That Loses Track of Sources](#example-3--the-research-assistant-that-loses-track-of-sources)
- [Example 4 — The DevOps Agent Debugging a Production Incident](#example-4--the-devops-agent-debugging-a-production-incident)
- [Example 5 — The Multi-Day Project That Resumes Cleanly](#example-5--the-multi-day-project-that-resumes-cleanly)
- [Pattern Summary Across All Five Examples](#pattern-summary-across-all-five-examples)

---

## Example 1 — The Long Coding Session That Forgot Its Architecture

### The symptom

A developer is three hours into a refactoring session with a coding
agent. The agent was told at the start: "Never modify files in
`legacy/`. All new code goes in `src/v2/`."

Two hours later, the agent edits a file in `legacy/` and suggests a
refactor that duplicates work already done. The developer catches it,
reminds the agent of the rule, and continues.

Twenty minutes later, the agent edits another file in `legacy/`. The
rule has been forgotten again.

### The audit

The developer runs:

```bash
python scripts/context_audit.py --session-dir ~/.hermes/sessions/current
```

Report:

```
=== Context Audit: /home/dev/.hermes/sessions/current ===

  Total tokens:            112,400
  Window utilization:      87.8%
  Instruction survival:    54.0%
  Stale content ratio:     42.0%
  Repetition ratio:        31.0%

  Top contributors:
    conversation: 58,000 tokens
    tool_output:read_file_12.txt: 23,400 tokens
    tool_output:bash_output_8.txt: 12,100 tokens
    system_prompt: 9,200 tokens
    reference:architecture.md: 6,942 tokens
    skill_index: 3,100 tokens

  Report saved: /home/dev/.hermes/context-audit/audit-20260115-143022.json
```

Translation:

- The desk is **88% full**. There is almost no headroom for reasoning.
- Only **half the original rules** are still findable.
- Nearly **half the conversation is stale** — content no longer
  relevant to the current sub-task.
- The agent is **repeating itself** at a rate of 31%.

### Classification

**Primary:** Overload. Utilization is 87.8%, above the 80% ceiling.

**Secondary:** Lost-in-Middle. The rule "never touch `legacy/`" was
stated once at the start (turn 1) and is now buried under three hours
of conversation and tool output.

### The fix

**Step 1 — Compress history to a resume brief.**

The developer replaces the 58,000-token conversation with a structured
brief of roughly 1,400 tokens:

```markdown
## Resume Brief

### Task
Refactor the payment module from the legacy implementation in
`legacy/payments.py` into a v2 implementation in `src/v2/payments/`.
Acceptance criteria: all tests pass, no dependencies on `legacy/`
module internals, public API unchanged.

### Decisions
- Use the repository pattern for data access. Rationale: matches the
  pattern already used in `src/v2/orders/`.
- Preserve the existing `PaymentResult` dataclass. Rationale: it is
  part of the public API and changing it would break callers.
- Defer the webhook integration to a follow-up PR. Rationale: out of
  scope for this refactor.

### Constraints
- [C1] Do not modify files under `legacy/`. Source: user, turn 1.
- [C2] All new code goes in `src/v2/`. Source: user, turn 1.
- [C3] Public API must remain unchanged. Source: `AGENTS.md`.
- [C4] Run `pytest tests/payments/` after each change. Source: user,
  turn 12.

### Open Questions
- Should the webhook handler be in a separate module or inline?
  Deferred to follow-up PR.

### Files
- `src/v2/payments/__init__.py`: created, exports `PaymentService`.
- `src/v2/payments/service.py`: modified, `charge()` implemented.
- `src/v2/payments/repository.py`: created, `PaymentRepository`
  implemented.
- `tests/payments/test_service.py`: modified, three new tests added.
- `legacy/payments.py`: read-only, do not modify.

### Active Sub-task
Implement the refund path in `PaymentService.refund()`. Signature:
`refund(payment_id: str, amount: Decimal) -> PaymentResult`. Must
validate that the payment exists and that the refund amount does not
exceed the original charge.
```

**Step 2 — Move the architecture doc off the active context.**

The architecture doc (6,942 tokens) is moved into
`references/architecture.md`. It is loaded only when the task touches
architecture.

**Step 3 — Cache the tool outputs.**

The two large tool outputs (`read_file_12.txt` at 23,400 tokens and
`bash_output_8.txt` at 12,100 tokens) are written to disk. Only a
one-line summary of each remains in context:

```
read_file_12.txt — src/v2/orders/repository.py, 340 lines.
  Full file: /tmp/session/read_file_12.txt
bash_output_8.txt — test run for orders, 156 passed, 0 failed.
  Full output: /tmp/session/bash_output_8.txt
```

**Step 4 — Add a rule to `context-profile.yaml`:**

```yaml
rules:
  - "Re-state all constraints from turn 1 in every resume brief."
```

This prevents the rule from being buried again.

### The outcome

After the fix, the developer re-runs the audit:

```
=== Context Audit: /home/dev/.hermes/sessions/current ===

  Total tokens:            38,200
  Window utilization:      29.8%
  Instruction survival:    96.0%
  Stale content ratio:     7.0%
  Repetition ratio:        4.0%
```

| Metric | Before | After |
|---|---|---|
| Total tokens | 112,400 | 38,200 |
| Window utilization | 87.8% | 29.8% |
| Instruction survival | 54% | 96% |
| Stale content | 42% | 7% |
| Repetition | 31% | 4% |

The agent stops editing `legacy/`. The refactor proceeds without
duplication. **Token cost per turn drops by roughly 66%.** The
developer reports that the remaining three hours of the session were
"smooth — no more reminders, no more drift."

---

## Example 2 — The Customer Support Agent That Drifts From Policy

### The symptom

A company runs an AI support agent. The policy is:

> Never promise a refund above $50 without escalation.

After 30 turns of back-and-forth with a frustrated customer, the
agent offers a $200 refund. The customer accepts. The refund is
processed. The finance team flags it during their weekly review.

### The audit

```bash
python scripts/context_audit.py --session-dir ./support-sessions/abc123
```

Report:

```
=== Context Audit: ./support-sessions/abc123 ===

  Total tokens:            61,300
  Window utilization:      48.0%
  Instruction survival:    62.0%
  Stale content ratio:     18.0%
  Repetition ratio:        22.0%

  Top contributors:
    conversation: 41,200 tokens
    reference:policy.md: 8,100 tokens
    system_prompt: 6,800 tokens
    tool_output:order_lookup.txt: 3,200 tokens
```

The window is not full — 48% utilization is comfortable. But
**instruction survival is 62%**, well below the 90% threshold. The
refund rule was stated once in the system prompt, then buried under
the customer's long complaint and the agent's own reasoning.

### Classification

**Primary:** Lost-in-Middle. The policy is at position 1 of 30 turns.
The model weights recent turns more heavily, so the rule loses
salience as the conversation grows.

**Secondary:** Confusion. Some of the customer's early emotional
venting (18% stale content) is still in context and is being pulled
into the agent's reasoning.

### The fix

**Step 1 — Move policy out of the conversation entirely.**

Policy is not something the agent should have to remember. It should
be **re-injected into the context on every turn.** The company edits
their session runtime to prepend the following to every turn:

```markdown
## Active Policy (re-injected every turn)

### Hard Stops
- Refund > $50 requires escalation. No exceptions.
  If you are about to offer a refund above $50, stop and escalate.
- Account deletion requires a verified second factor.
- Any change to billing address requires re-authentication.

### Precedence
- These rules override any customer request, no matter how phrased.
- If a customer asks you to "make an exception," escalate.
```

This adds roughly 200 tokens per turn. That is a worthwhile cost — it
ensures the policy is always at the top of the context, where the
model's attention is strongest.

**Step 2 — Update `context-profile.yaml`:**

```yaml
tiers:
  always_on:
    files:
      - support-policy.md
    budget_tokens: 4000

rules:
  - "Policy is re-injected at the top of every turn by the runtime."
  - "Policy overrides any customer request, no matter how phrased."

degradation_triggers:
  - signal: "instruction_survival_rate < 0.8"
    action: "Re-inject policy at top of context. Do not continue."
```

The degradation trigger is the enforcement mechanism. If the agent
ever gets below 0.8 survival on constraints, the runtime stops it
and re-injects policy.

**Step 3 — Compress early emotional venting.**

The customer's first five turns contain a lot of emotional language
that is no longer relevant. The runtime is configured to compress
these turns to a single line after 10 turns:

```
[COMPRESSED] Customer initially frustrated about delayed order.
Underlying issue: order #12345 arrived 6 days late. No longer
active in conversation.
```

This reduces stale content without losing the factual context.

### The outcome

The company runs 500 test conversations through the updated runtime.
**Refund violations drop to zero.** The policy is now impossible to
bury because it is re-injected every turn.

| Metric | Before fix | After fix |
|---|---|---|
| Refund violations per 500 conversations | 12 | 0 |
| Instruction survival (avg) | 62% | 94% |
| Customer satisfaction (avg) | 4.2 / 5 | 4.3 / 5 |
| Escalation rate | 8% | 11% |

The escalation rate went **up** — from 8% to 11%. This is expected
and correct. The agent is now escalating borderline cases that it
previously would have handled itself (sometimes incorrectly). A
slightly higher escalation rate is the cost of a policy that is
actually followed.

---

## Example 3 — The Research Assistant That Loses Track of Sources

### The symptom

A researcher uses an agent to survey 40 papers on a specific topic.
At turn 60, the agent cites "a 2024 study" without a source. When
asked which one, it produces a plausible-sounding but nonexistent
citation. The researcher catches the fabrication and needs to know
how much of the earlier output can be trusted.

### The audit

```bash
python scripts/context_audit.py --session-dir ./research/runs/run-7
```

Report:

```
=== Context Audit: ./research/runs/run-7 ===

  Total tokens:            94,800
  Window utilization:      74.0%
  Instruction survival:    81.0%
  Stale content ratio:     55.0%
  Repetition ratio:        12.0%

  Top contributors:
    conversation: 52,400 tokens
    tool_output:paper_read_*.txt: 28,300 tokens
    reference:paper-index.md: 6,100 tokens
    system_prompt: 5,200 tokens
    skill_index: 2,800 tokens
```

Translation:

- **Stale content is over half the context (55%).** The agent read 40
  papers earlier; the details of 30 of them are still occupying space,
  un-referenced, while the current task needs only 5.
- **Instruction survival is 81%** — the "always cite sources" rule
  from the start of the session is still findable, but weaker than it
  should be.

### Classification

**Primary:** Confusion. Stale paper details are crowding out the
active sources.

**Secondary:** Overload. Utilization is 74% and rising.

### The fix

**Step 1 — Move paper summaries to on-demand references.**

Each paper's summary is written to `references/papers/<id>.md`. The
agent loads only the papers relevant to the current sub-question.

```
references/papers/
├── paper-001.md    (Chen et al. 2024, "Attention in Long Context")
├── paper-002.md    (Smith & Jones 2023, "Transformer Efficiency")
├── paper-003.md    (Garcia 2025, "Retrieval-Augmented Methods")
...
└── paper-040.md    (Wilson 2024, "Benchmarking LLM Memory")
```

**Step 2 — Build a source index.**

A single file `references/paper-index.md` holds one line per paper:

```markdown
## Paper Index

- [001] Chen et al. 2024, "Attention in Long Context" — finding: attention degrades measurably beyond 50% window fill.
- [002] Smith & Jones 2023, "Transformer Efficiency" — finding: sparse attention reduces compute by 40% with minimal quality loss.
- [003] Garcia 2025, "Retrieval-Augmented Methods" — finding: RAG outperforms fine-tuning for factual recall.
...
- [040] Wilson 2024, "Benchmarking LLM Memory" — finding: mid-context information is recalled at 60% the rate of primacy and recency positions.
```

This file is ~2,000 tokens and lives in the `on_demand` tier. It is
loaded when the agent needs to cite a paper but is not loaded
otherwise.

**Step 3 — Add explicit citation rules.**

```yaml
rules:
  - "Cite papers by ID only. Never cite a paper not in references/paper-index.md."
  - "If a claim has no source, state 'no source found' rather than producing a citation."
  - "Never invent a citation. If the ID is not in the index, the citation does not exist."
```

**Step 4 — Compress the read operations.**

The 40 individual read operations (totaling ~28,300 tokens) collapse
into the paper index. The full paper summaries remain accessible on
demand.

### The outcome

After the fix, the agent's citation behavior is measured across the
same task:

| Metric | Before fix | After fix |
|---|---|---|
| Hallucinated citations | 4 | 0 |
| Correctly sourced claims | 27 | 31 |
| Claims with no source stated | 3 | 5 |
| Token cost per turn | ~14,000 | ~6,300 |

**Hallucinated citations drop to zero.** The "claims with no source
stated" count went up — from 3 to 5 — which is the desired behavior:
the agent now correctly says "no source found" instead of inventing
one.

**Token cost per turn falls by 55%.** The agent can still reach any
paper's details on demand, but the details are no longer occupying
context by default.

---

## Example 4 — The DevOps Agent Debugging a Production Incident

### The symptom

It is 2:14 AM. A production incident is in progress. An on-call
engineer points a DevOps agent at the incident and asks it to find
the root cause.

The agent pulls:
- 12 log files (some 50,000 lines each).
- 8 metrics dashboards (all rendered as large JSON blobs).
- A Kubernetes state dump (the whole cluster).

After 15 turns, the agent's hypotheses become vague and it re-suggests
a fix it already tried and rejected.

### The audit

```bash
python scripts/context_audit.py --session-dir ./incidents/INC-4421
```

Report:

```
=== Context Audit: ./incidents/INC-4421 ===

  Total tokens:            121,900
  Window utilization:      95.2%
  Instruction survival:    44.0%
  Stale content ratio:     28.0%
  Repetition ratio:        47.0%

  Top contributors:
    tool_output:api-errors.log: 41,200 tokens
    tool_output:k8s-state.txt: 28,400 tokens
    tool_output:db-slow.log: 22,100 tokens
    conversation: 18,900 tokens
    tool_output:metrics_*.json: 11,300 tokens
```

Translation:

- **Utilization is 95.2%.** The window is effectively full.
- **Repetition is 47%.** The agent is looping — nearly half the
  context is duplicated content.
- **Instruction survival is 44%.** The engineer's initial description
  of the incident has been pushed out by tool output.

The agent is thrashing. Every new turn adds more data and pushes out
useful information.

### Classification

**Primary:** Overload. The window is at 95% utilization.

**Secondary:** Confusion. The agent cannot distinguish between
relevant and irrelevant log lines because there is no structure.

### The fix

**Step 1 — Stop and compress. Do not continue the current turn.**

The engineer interrupts the agent and runs the emergency compression
procedure.

**Step 2 — Find the biggest offenders.**

```bash
python scripts/token_estimator.py --dir ./incidents/INC-4421/tool_outputs --top 5
```

Output:

```
Total: 102,000 tokens across 22 files

    Tokens  File
    ------  --------------------------------------------------
    41,200  api-errors.log
    28,400  k8s-state.txt
    22,100  db-slow.log
     6,800  metrics_latency.json
     4,500  metrics_errors.json
```

**Step 3 — Summarize each log file to 200 tokens.**

For `api-errors.log`:

```
api-errors.log — 48,201 lines, 312 errors.
  Time range: 01:45–02:12 UTC.
  Top error signatures:
    - E_CONN_RESET (142 occurrences, all to db-primary-2)
    - E_TIMEOUT (98 occurrences, all to upstream-payments)
    - E_MEMORY (72 occurrences, worker-3 only)
  Peak rate: 82 errors/min at 02:02 UTC.
  Full file: /tmp/INC-4421/api-errors.log
```

For `k8s-state.txt`:

```
k8s-state.txt — 342 pods across 4 nodes.
  Node status: node-3 NotReady (since 02:01 UTC).
  Restarting pods: 18, all on node-3.
  Memory pressure: node-3 at 94%, others under 60%.
  Full dump: /tmp/INC-4421/k8s-state.txt
```

For `db-slow.log`:

```
db-slow.log — 156 slow queries between 01:50 and 02:12.
  Top slow query: SELECT ... FROM orders (avg 3.2s, 89 occurrences).
  Correlates with api-errors E_CONN_RESET timing.
  Full file: /tmp/INC-4421/db-slow.log
```

**Step 4 — Build a hypothesis board.**

The engineer asks the agent to externalize its reasoning into a
structured board that replaces free-form reasoning:

```
## Hypotheses

- [H1] DB connection pool exhaustion
  STATUS: TESTED, negative
  Evidence: pool metrics show capacity available

- [H2] Memory leak in worker-3
  STATUS: TESTED, negative
  Evidence: worker-3 restarted clean, leak persists

- [H3] Node-3 network degradation
  STATUS: TESTING
  Evidence: node-3 NotReady, 18 pods restarting, k8s memory
            pressure correlates with api-error timing

- [H4] Upstream timeout cascade
  STATUS: UNTESTED
  Evidence: E_TIMEOUT errors are downstream of node-3 issues
```

This board is ~400 tokens. It replaces thousands of tokens of
meandering reasoning.

**Step 5 — Enforce a token cap on new tool output.**

The runtime is configured: **no tool output larger than 2,000 tokens
enters context.** Anything larger is written to disk and referenced
by path with a summary.

### The outcome

The agent finds the root cause (H3 — node-3 network degradation) two
turns later.

| Metric | Before fix | After fix |
|---|---|---|
| Total tokens | 121,900 | 24,300 |
| Window utilization | 95.2% | 19.0% |
| Instruction survival | 44% | 91% |
| Repetition | 47% | 6% |
| Time to root cause | est. 45+ min | 12 min |

The engineer reported afterward: without the fix, the agent would
likely have looped indefinitely or required starting the incident
response over from scratch. The 12-minute time-to-resolution was
**the fastest of the quarter** for a comparable incident.

---

## Example 5 — The Multi-Day Project That Resumes Cleanly

### The symptom

A founder works with an agent across five days on a product spec.
Each morning, the agent seems to have forgotten decisions from the
previous day. The founder re-explains context every session.

By day 3, the founder is keeping a separate document on the side to
remember what the agent was told, because the agent cannot be trusted
to remember it.

### The audit

There is no single session to audit — the problem is **between**
sessions. But the effect is measurable. The founder timed the
catch-up: **roughly 15 minutes each morning**, and roughly 25,000
tokens of re-orientation in the first 10 turns.

### Classification

**Primary:** Confusion across sessions. Each session starts fresh
with no memory of the previous session's decisions.

**Secondary:** Overload within sessions. Because the founder
re-explains context at the start, the first 10 turns carry a heavy
load that crowds out actual work.

### The fix

**Step 1 — Create a resume brief template.**

The founder creates `context/resume-brief.md` in the project:

```markdown
## Resume Brief

### Task
[One sentence: what are we doing and why?]

### Decisions
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

### Constraints
- [Constraint 1] (source: [user / AGENTS.md / discovered])
- [Constraint 2]

### Open Questions
- [Question 1]
- [Question 2]

### Files
- [Path]: [Current state — modified, created, read-only]
- [Path]: [Current state]

### Active Sub-task
[What the agent was doing when the session paused, and its
acceptance criteria]

### Next Step
[The single next action to take at the start of the next session.]
```

**Step 2 — End every session by writing the brief.**

The agent is instructed to produce the resume brief as the **final
action** of every session. The instruction is added to the project's
`AGENTS.md`:

```markdown
## Session End

Before ending the session, write `context/resume-brief.md` with the
current state. See the template in the file itself. This is the
last action of every session.
```

**Step 3 — Start every session by loading the brief.**

The instruction is also added to `AGENTS.md`:

```markdown
## Session Start

The first action of every session is to read
`context/resume-brief.md`. Everything in that file is authoritative.
Do not proceed until it is loaded.
```

**Step 4 — Keep a decision log.**

Every decision is written to `references/decision-log.md` with a
timestamp, the decision, the rationale, and the alternatives
considered:

```markdown
## 2026-01-12

### Decision: Use PostgreSQL rather than SQLite

**Rationale:** Multi-user access is required. SQLite's locking model
would serialize writes under load.

**Alternatives considered:**
- SQLite with WAL mode — rejected, still single-writer.
- MySQL — rejected, team has no operational experience.
- Postgres — selected.

**Impact:** Affects `references/architecture.md` (data layer section).
```

This file lives in the `on_demand` tier. It is loaded only when the
current task touches a decision.

**Step 5 — Add project rules.**

```yaml
rules:
  - "The final action of every session is to write context/resume-brief.md."
  - "The first action of every session is to read context/resume-brief.md."
  - "Every decision goes in references/decision-log.md, with rationale."
```

### The outcome

| Metric | Before | After |
|---|---|---|
| First-10-turn token cost | ~25,000 | ~4,200 |
| Catch-up time each morning | ~15 min | ~30 sec |
| Decisions lost across sessions | Frequent | None observed over 5 days |
| Founder satisfaction | "Exhausting" | "It just works" |

The founder reported: **"I stopped keeping notes on the side. The
brief is the notes. Every morning I just open it and we pick up where
we left off."**

The same pattern works for any multi-session project:

- **Book writing** — chapter decisions, character choices, plot
  threads.
- **Legal research** — case citations, precedents, argument strategy.
- **Long-running refactors** — architectural decisions, migration
  state, in-flight changes.
- **Thesis work** — argument structure, source notes, open questions.
- **Campaign planning** — audience decisions, messaging choices,
  channel strategy.

The mechanics are identical. Only the content of the brief changes.

---

## Pattern Summary Across All Five Examples

Every real-world win follows the same shape:

### 1. Measure

Run the audit. Get numbers, not opinions. Without numbers, you cannot
tell whether a change made things better or worse.

The audit script produces:
- Total tokens and window utilization.
- Instruction survival rate.
- Stale content ratio.
- Repetition ratio.
- Top contributors.

### 2. Name the failure

Classify against the five degradation modes:

| Class | Primary signal |
|---|---|
| **Poisoning** | A fact the agent cites consistently is wrong |
| **Clash** | Oscillating between contradictory instructions |
| **Confusion** | References to stale content |
| **Lost-in-Middle** | Middle instructions ignored |
| **Overload** | Utilization > 80% |

A session can have multiple classes. **Fix Overload first** — it
amplifies the others.

### 3. Move content to the right tier

Off the always-on desk and into on-demand references, or compress it
into a brief.

- **Stable knowledge** → `references/`
- **Long conversation history** → resume brief
- **Large tool outputs** → cached to disk, referenced by path
- **Policy and hard constraints** → always-on, re-injected every turn

### 4. Write the rule down

Add the fix to `context-profile.yaml` so it persists across sessions.
A fix that is applied once and forgotten is not a fix — it is a
bandage.

The rule encodes the lesson. Next time the same failure starts to
develop, the trigger fires and the fix is applied automatically.

### 5. Re-measure

Run the audit again. Confirm:

- The numbers improved.
- Task quality did not regress.
- The agent can state its constraints when asked.

If the numbers improved but quality did not, the diagnosis was wrong.
Re-classify and repeat.

---

## Cross-Example Comparison

| | Ex 1 | Ex 2 | Ex 3 | Ex 4 | Ex 5 |
|---|---|---|---|---|---|
| **Primary class** | Overload | Lost-in-Middle | Confusion | Overload | Confusion |
| **Trigger** | 3-hour coding | 30-turn support | 40-paper survey | 2 AM incident | 5-day project |
| **Key fix** | Resume brief | Policy re-injection | Paper index | Emergency compression | Session bookends |
| **Tokens before** | 112k | 61k | 95k | 122k | ~25k/session |
| **Tokens after** | 38k | ~61k* | 43k | 24k | ~4k/session |
| **Primary win** | Instruction survival | Zero policy violations | Zero hallucinations | Time to resolution | Cross-session continuity |

*Example 2's token count did not change much — the fix was to
restructure, not to reduce. Policy was moved from the conversation
into a re-injected tier, which added ~200 tokens per turn but
eliminated the failure mode entirely.

---

## The Common Thread

All five examples share three properties:

1. **The problem was invisible until measured.** Each human knew
   something was wrong, but could not have told you the instruction
   survival rate, or the stale content ratio, or which specific block
   of context was the largest contributor.

2. **The fix was structural, not linguistic.** No example was solved
   by rewording a prompt. Every fix moved content to a different
   tier, or compressed it, or re-injected it at a position where the
   model would weight it more heavily.

3. **The fix was made permanent.** Every example ended with a change
   to `context-profile.yaml` or `AGENTS.md` that prevents the same
   failure from recurring. The fix was not applied once and forgotten
   — it was encoded into the project's architecture.

This is the difference between **debugging** and **engineering**.
Debugging fixes the current problem. Engineering prevents the class
of problem from recurring.

The context-engineering skill is a debugging tool. The
`context-profile.yaml` it produces is an engineering artifact. Used
together, they turn a recurring source of pain into a one-time fix.