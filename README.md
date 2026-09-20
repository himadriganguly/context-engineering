# Context Engineering — An Agent Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blue)](https://agentskills.io)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](CHANGELOG.md)
[![Validate skill](https://github.com/himadriganguly/context-engineering/workflows/Validate%20skill/badge.svg)](https://github.com/himadriganguly/context-engineering/actions/workflows/validate.yml)

A portable Agent Skill for diagnosing and improving context usage in
long-running AI-agent sessions.

The project combines a concise `SKILL.md` procedure with optional
reference material and standalone Python utilities for inspecting
session artifacts and estimating the relative size of files.

> [!WARNING]
> **Use at your own risk.**
>
> This project provides heuristics and workflow guidance. Its metrics
> are estimates and are not authoritative measurements of model
> attention, reasoning quality, or context-window behavior.
>
> Review the scripts before running them on sensitive data. The audit
> utility reads files from the session directory you provide and writes
> reports to a local output directory. Do not point it at directories
> containing sensitive information unless you understand what will be
> read and where the resulting report will be written.
>
> Back up important project or session data before applying automated
> or agent-assisted changes. Validate recommendations against your own
> model, runtime, and workload.

**The missing meta-skill for AI agents.** Teaches any Agent
Skills–compatible agent how to diagnose, optimize, and maintain its own
context window — the working memory that determines whether every other
skill works or fails.

---

## What this skill does

Context is the working information available to an AI agent while it
performs a task.

As context grows, several problems can become more difficult to
diagnose:

- stale information remains active
- large tool outputs crowd out more relevant material
- instructions can become harder to retrieve
- duplicate information consumes space
- conflicting instructions can remain active simultaneously
- long conversations can become difficult to summarize accurately

This skill provides a repeatable workflow:

1. **Measure** available context where compatible session artifacts
   exist.
2. **Identify** a likely degradation pattern.
3. **Apply** a structural context-management change.
4. **Encode** durable project rules in appropriate project
   documentation.
5. **Re-measure** and evaluate the actual task result.

The goal is not to claim that one fixed threshold works for every
model. The goal is to provide a practical way to investigate context
problems.

---

## What you get

| Component | Purpose |
|---|---|
| `skills/context_engineering/SKILL.md` | Core five-step workflow |
| `skills/context_engineering/scripts/context_audit.py` | Lightweight audit of supported session artifacts |
| `skills/context_engineering/scripts/token_estimator.py` | Relative size/token estimate for text, files, and directories |
| `skills/context_engineering/references/degradation-signals.md` | Context degradation taxonomy |
| `skills/context_engineering/references/progressive-disclosure-patterns.md` | Context organization patterns |
| `skills/context_engineering/references/token-budget-framework.md` | Budgeting guidance and example thresholds |
| `skills/context_engineering/templates/context-profile.yaml` | Example project context profile |
| `EXAMPLES.md` | Illustrative scenarios |
| `INSTALL.md` | Installation and runtime compatibility notes |

The Python utilities use only the Python standard library.

No `pip install` step is required.

The project does not require telemetry or a hosted service.

---

## Agent Skills compatibility

The core skill follows the open Agent Skills format:

```
skills/context_engineering/
├── SKILL.md
├── references/
├── scripts/
└── templates/
```

The portable portion is the Markdown skill and its referenced
resources.

The optional Python audit utility is different: it expects a particular
session-artifact layout. A runtime that stores its sessions differently
may require an adapter or an exported session directory.

Therefore:

> **Agent Skills format compatibility does not mean native
> session-script compatibility with every runtime.**

This distinction is intentional.

---

## Compatibility

| Runtime | Core skill format | Audit scripts | Status in this repository |
|---|---|---|---|
| Hermes Agent | Compatible | Designed for compatible exported/session artifacts | Primary target |
| Claude Code | Agent Skills format compatible | Runtime session integration not provided | Format-compatible; script integration not independently validated |
| Cursor | Agent Skills format compatible | Runtime session integration not provided | Format-compatible; script integration not independently validated |
| OpenAI Codex | Agent Skills format compatible | Runtime session integration not provided | Format-compatible; script integration not independently validated |
| Gemini CLI | Agent Skills format compatible | Runtime session integration not provided | Format-compatible; script integration not independently validated |
| OpenClaw | Not independently validated by this repository | Not independently validated | Do not assume compatibility |
| Other runtimes | Potentially compatible | Runtime-dependent | Validate before use |

The skill itself requires only an Agent Skills-compatible runtime.

The optional Python utilities require Python 3.9+.

Runtime-specific skills paths and installation procedures are
documented in [INSTALL.md](INSTALL.md).

---

## Hermes Skills Hub

This repository is structured as a GitHub skill tap:

```
context-engineering/
├── skills/
│   └── context-engineering/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── templates/
├── skills.sh.json
└── README.md
```

Hermes supports GitHub skill taps using this layout and supports
`skills.sh.json` for category groupings.

Publish the skill with:

```bash
hermes skills publish \
  skills/context_engineering \
  --to github \
  --repo himadriganguly/context-engineering
```

For a custom GitHub tap:

```bash
hermes skills tap add himadriganguly/context-engineering
```

Then search the GitHub source:

```bash
hermes skills search context-engineering --source github
```

The public Hermes Skills Hub uses a generated catalog snapshot rather
than crawling GitHub live. A newly published skill may therefore take
time to appear in the public catalog.

---

## Quick install

### Hermes

For a direct local installation, the installed skill directory should
contain `SKILL.md` at its top level:

```bash
mkdir -p ~/.hermes/skills
cp -r skills/context_engineering ~/.hermes/skills/
```

Verify:

```bash
ls ~/.hermes/skills/context_engineering/SKILL.md
```

Hermes also supports GitHub skill taps and Hub installation. See
[INSTALL.md](INSTALL.md).

### Other Agent Skills runtimes

Do not blindly copy the repository root into another runtime's skill
directory.

Copy the skill directory:

```
skills/context_engineering/
```

to the location documented by that runtime.

See [INSTALL.md](INSTALL.md) for runtime-specific notes.

---

## Python Utilities Installation

The core Python scripts require zero external dependencies and run on standard Python 3.9+.

Standard Install (Heuristic Token Counting):

```bash
pip install .
```

Exact Token Math Install:

To use exact token counting instead of the character-based heuristic, install the exact-tokens extra, which includes tiktoken:

```bash
pip install .[exact-token]
```

Development Install:

To install testing dependencies (pytest, pyyaml) alongside exact token math:

```bash
pip install -e .[dev]
```

### Testing

This project uses pytest to validate logic, file handling, metadata, and CLI integration. To run the test suite locally:

1. Ensure you have installed the development dependencies (pip install -e .[dev]).

2. Run pytest from the repository root:

```bash
pytest test/ -v
```

---

## Using the skill

Ask the agent to use the skill when a context problem is suspected.

For example:

> Use the context-engineering skill to investigate why important
> constraints are being missed during this long session.

The agent should:

1. Determine whether compatible session artifacts are available.
2. Run the audit when appropriate.
3. Read the relevant reference material.
4. Form a hypothesis about the likely context problem.
5. Apply a structural intervention.
6. Verify the result.

If the runtime does not expose compatible session artifacts, the agent
can still use the conceptual workflow and the static token estimator.

---

## Using the audit utility

The audit utility accepts a directory containing the supported
artifact layout.

Basic usage:

```bash
python3 skills/context_engineering/scripts/context_audit.py \
  --session-dir PATH
```

Specify a model/runtime context-window size:

```bash
python3 skills/context_engineering/scripts/context_audit.py \
  --session-dir PATH \
  --window-size 200000
```

JSON output:

```bash
python3 skills/context_engineering/scripts/context_audit.py \
  --session-dir PATH \
  --json
```

Compare the two latest reports:

```bash
python3 skills/context_engineering/scripts/context_audit.py \
  --session-dir PATH \
  --compare
```

Specify where reports are written:

```bash
python3 skills/context_engineering/scripts/context_audit.py \
  --session-dir PATH \
  --output-dir ./audit-results
```

The audit uses heuristics. It does not inspect the model's internal
attention or determine causality.

---

## Using the token estimator

Estimate a string:

```bash
python3 skills/context_engineering/scripts/token_estimator.py \
  --text "example text"
```

Estimate a file:

```bash
python3 skills/context_engineering/scripts/token_estimator.py \
  --file path/to/file
```

Find large files:

```bash
python3 skills/context_engineering/scripts/token_estimator.py \
  --dir . \
  --recursive \
  --top 20
```

The estimator uses a character-based approximation.

It is intended for relative comparisons and rough planning.

It is not an exact tokenizer and should not be used for billing,
quota, or model-capacity calculations.

---

## Interpreting the metrics

The audit reports several lightweight indicators.

### Estimated tokens

An approximation based on characters divided by a configurable
characters-per-token value.

### Window utilization

Estimated context size divided by the configured context-window size.

### Instruction survival

The fraction of detectable user constraints that remain findable in
the inspected artifacts.

This is not semantic instruction-following evaluation.

### Stale content

A heuristic based on vocabulary overlap between older and recent
conversation material.

### Repetition

A heuristic based on repeated word n-grams.

### Top contributors

The largest inspected blocks by estimated token count.

These metrics are useful for identifying trends and candidates for
investigation. They should not be interpreted as proof of model
behavior.

---

## Context headroom

The project uses 80% utilization as a conservative investigation
threshold.

That does not mean that every model begins degrading at exactly 80%.

Actual behavior depends on:

- model architecture
- tokenizer
- context-window implementation
- system instructions
- tool schemas
- runtime overhead
- task complexity
- information placement
- workload

Treat 80% as a starting point, not a universal law.

---

## Token estimation limitations

The included estimator uses a simple character-based heuristic.

For example:

```
characters / 3.8 ≈ estimated tokens
```

The value is configurable because different languages, file formats,
tokenizers, and models can produce substantially different ratios.

If exact token counts matter, use the tokenizer appropriate for the
model you are actually using.

---

## Examples

[EXAMPLES.md](EXAMPLES.md) contains illustrative scenarios showing how
the workflow can be applied.

The examples are not presented as controlled benchmarks or guarantees.

Results from context restructuring vary by model, runtime, task, and
workload.

When reporting your own results, record:

- model/provider
- runtime and version
- context-window size
- input/task
- before metrics
- intervention
- after metrics
- task-quality evaluation method

This makes results easier to reproduce and compare.

---

## Design principles

### Measure before changing

Use measurements and observations to establish a baseline where
possible.

### Structure beats prompt tricks

Context problems are often better addressed by deciding what should be
always-on, what should be on-demand, and what should be externalized.

### Preserve headroom

Avoid designing workflows that depend on filling the entire context
window.

### Treat skills as context

Skills and their references consume context too. Load only what the
task requires.

### Verify the task, not only the metric

A lower estimated token count is not automatically an improvement if
important information was removed.

---

## Project Structure

```
context-engineering/
│
├── .github/
│   └── workflows/
│       └── validate.yml                            # CI: validates frontmatter + runs scripts
├── examples/
│   └── README.md                                   # Index for the case studies
├── skills/
│   └── context-engineering/                        # ★ The installable skill
│       ├── references/
│       │   ├── degradation-signals.md              # Taxonomy of the 5 failure modes
│       │   ├── progressive-disclosure-patterns.md  # 6 patterns for keeping context small
│       │   └── token-budget-framework.md           # Budget allocation + enforcement
│       ├── scripts/
│       │   ├── context_audit.py                    # Produces the quantitative audit
│       │   └── token_estimator.py                  # Pre-flight cost estimator
│       ├── templates/
│       │   └── context-profile.yaml                # Declarative context architecture
│       └── SKILL.md                                # The core procedure
│
├── .gitignore
├── CHANGELOG.md                                    # Version history
├── CONTRIBUTING.md                                 # Contribution guide
├── EXAMPLES.md                                     # 5 real-world case studies
├── INSTALL.md                                      # Install for 7 runtimes
├── LICENSE                                         # MIT
├── README.md                                       # This file
└── skills.sh.json                                  # Manifest for `npx skills add`
```

---

## Contributing

Useful contributions include:

- new context degradation patterns
- additional runtime adapters
- additional supported session formats
- better test fixtures
- reproducible case studies
- documentation improvements
- translations

When adding runtime support, distinguish clearly between:

1. Agent Skills format compatibility.
2. Installation/discovery compatibility.
3. Python-script compatibility.
4. Native session integration.

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security and privacy

The core skill is Markdown.

The Python audit utility reads files from the directory supplied
through `--session-dir`.

Do not assume that a session directory is safe to expose.

Before running the audit:

- inspect the input directory
- understand what files will be read
- avoid sensitive directories unless necessary
- choose an appropriate `--output-dir`
- review generated JSON reports before sharing them

The project does not require network access for the included Python
utilities.

---

## License

MIT.

See [LICENSE](LICENSE).

---

## Status

Version 1.0.0.

The Agent Skills format and Hermes integration are the primary
distribution targets.

Runtime-specific script integrations should be considered experimental
until independently validated and documented.