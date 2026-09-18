# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned

- A web-based audit viewer that renders `audit-*.json` reports as
  charts over time.
- A `--watch` mode for `context_audit.py` that re-runs automatically
  when the session directory changes.
- Reference file templates for common domains (API, database, ML,
  frontend).
- Translations of `SKILL.md` into Spanish, French, German, Japanese,
  and Mandarin.
- A `context-profile.schema.json` file for editor autocomplete and
  validation.
- Support for reading session state directly from Hermes, Claude Code,
  and Cursor APIs, instead of requiring a session directory.

---

## [1.0.0] — 2026-09-19

### Added

#### Core skill

- `SKILL.md` — the main procedure. Defines the five-step context
  engineering workflow: audit, classify, fix, rebuild, verify.
  Includes a "When to Use" section with seven trigger signals, a
  "Pitfalls" section with five common mistakes, and a "Verification"
  section with four success criteria.
- YAML frontmatter with `name`, `description`, `license`,
  `compatibility`, and `metadata` fields, valid for any Agent Skills
  runtime.

#### Reference documents

- `references/degradation-signals.md` — full taxonomy of the five
  context failure modes:
  - **Poisoning** — a false statement enters context and is treated
    as ground truth.
  - **Clash** — two sources give contradictory instructions.
  - **Confusion** — stale content is treated as relevant.
  - **Lost-in-Middle** — attention degrades with position.
  - **Overload** — the window is near capacity.
  Each class includes signals, common sources, a fix procedure, and
  verification steps. Also includes a "Mixed Failures" section and a
  "Diagnostic Order" section.
- `references/progressive-disclosure-patterns.md` — six reusable
  patterns for keeping context small:
  1. The three-tier context (always-on, on-demand, ephemeral).
  2. The resume brief.
  3. Reference file structure (Quick Reference first).
  4. Skill description as loading signal.
  5. Conditional activation via toolsets.
  6. Tool output summarization (extract, diff, chunk, cache).
  Includes an "Applying the Patterns Together" section and a
  six-item checklist.
- `references/token-budget-framework.md` — measurement, allocation,
  and enforcement. Includes:
  - A calibrated budget for 128k, 32k, and 8k windows.
  - Five enforcement rules with numeric thresholds.
  - Side-by-side healthy and unhealthy audit profiles.
  - A "Reading a Profile at a Glance" table for fast interpretation.
  - Monitoring guidance with recommended audit frequencies.

#### Scripts

- `scripts/context_audit.py` — produces a quantitative audit report
  for any session directory. Measures:
  - Total tokens and window utilization.
  - Instruction survival rate (fraction of user constraints still
    present).
  - Stale content ratio (fraction of conversation no longer relevant).
  - Repetition ratio (fraction of duplicated 6-grams).
  - Top 10 largest contributors.
  Writes a JSON report to `~/.hermes/context-audit/` for historical
  comparison. Supports `--json` and `--compare` modes.
- `scripts/token_estimator.py` — predicts token cost of text, a
  single file, or a directory tree. Uses a calibrated heuristic of
  3.8 characters per token. Supports `--text`, `--file`, `--dir`,
  `--recursive`, and `--top N` options.

Both scripts depend only on the Python standard library. No
`pip install` required. Compatible with Python 3.9+.

#### Templates

- `templates/context-profile.yaml` — a starter configuration file
  for a project's context architecture. Declares:
  - Project identity.
  - Three context tiers with file lists and token budgets.
  - Rules for resolving conflicts and preventing duplication.
  - Five degradation triggers paired with actions.
  - Audit settings.
  Includes extensive inline comments explaining the reasoning
  behind each default.

#### Documentation

- `README.md` — GitHub landing page. Includes badges, a summary of
  the problem, a component table, quick-install commands, and a
  compatibility matrix.
- `INSTALL.md` — step-by-step installation for seven runtimes:
  Hermes Agent, Claude Code, Cursor, OpenAI Codex, Gemini CLI,
  OpenClaw, and generic Agent Skills runtimes. Includes git submodule
  installation, npm installation, a post-install checklist, and
  troubleshooting.
- `EXAMPLES.md` — five real-world case studies with before/after
  metrics:
  1. Long coding session that forgot its architecture.
  2. Customer support agent that drifts from policy.
  3. Research assistant that loses track of sources.
  4. DevOps agent debugging a production incident.
  5. Multi-day project that resumes cleanly.
  Each case study follows the same arc: symptom, audit, fix, outcome.
- `CONTRIBUTING.md` — contribution guide. Describes what we want
  (new degradation patterns, new runtimes, real-world case studies,
  script improvements, translations) and what we do not want
  (external dependencies, runtime-specific hacks, uncontrolled
  always-on costs). Includes a style guide and versioning policy.
- `UPLOAD.md` — instructions for uploading to GitHub, either via the
  GitHub CLI or manually. Includes a post-upload checklist and
  instructions for submitting to the Agent Skills registry,
  Hermes community skills, and Awesome Agent Skills.

#### Infrastructure

- `LICENSE` — MIT License.
- `.gitignore` — Python-focused ignore rules, extended with
  project-specific entries for context audit output, distribution
  archives, editors, operating systems, logs, local session
  artifacts, and secrets.
- `.github/workflows/validate.yml` — GitHub Actions workflow that
  runs on every push and pull request. Validates the `SKILL.md`
  frontmatter, runs the token estimator against a test string, and
  runs the audit script against an empty session directory.
- `examples/README.md` — index of the case studies with a short
  summary of each, plus a "What to Take From These" section that
  explains the common procedure across all five.

### Design decisions

- **No external Python dependencies.** Both scripts use only the
  standard library. This keeps installation trivial and ensures the
  scripts run in any environment where Python 3.9+ is available.
- **Character-based token estimation.** The estimator uses a
  blended heuristic of 3.8 characters per token rather than a real
  tokenizer. This is accurate to ±10% and works identically across
  model providers, which is what a cross-platform skill needs.
- **JSON report storage.** Reports accumulate in
  `~/.hermes/context-audit/` with timestamped filenames. This
  enables the `--compare` mode and makes long-term trends visible.
- **Progressive disclosure as a first-class principle.** The skill
  itself follows the patterns it teaches: `SKILL.md` is compact, the
  references load on demand, the scripts execute rather than load.
- **MIT license.** No restrictions on commercial use, modification,
  or redistribution. The goal is adoption, not control.

### Known limitations

- The audit script expects a specific session directory layout
  (`conversation.jsonl`, `system_prompt.txt`, `tool_outputs/`,
  `references/`). Runtimes that store sessions differently will
  require adapting the `load_session()` function.
- The instruction survival metric uses a fixed regex for imperative
  sentences (`must|should|never|always|do not|don't|ensure|make
  sure|require|need|only|avoid`). Constraints phrased with other
  verbs will not be counted.
- The stale content heuristic compares 5+ letter words between turns
  older than 10 and the most recent 5 turns. This is a proxy, not a
  semantic analysis. It can produce false positives on sessions with
  heavy vocabulary overlap between unrelated sub-tasks.
- Token estimation is approximate. It is consistent across files
  within a session, but it is not suitable for billing calculations.
- The skill has been validated against Hermes, Claude Code, and
  Cursor. Other runtimes are expected to work but have not been
  formally tested.

### Acknowledgments

This skill was created in response to a widely observed gap in the
2026 agent ecosystem: context engineering is consistently named as
the number-one unmet skill for AI agent developers, but no
comprehensive, open-source solution existed. The skill draws on:

- The [Agent Skills specification](https://agentskills.io) for the
  file format and loading semantics.
- The Hermes Agent skills documentation for runtime-specific
  conventions.
- Public discussions of context window degradation across the
  agent-development community.

Contributions are welcome. See `CONTRIBUTING.md`.

---

## Versioning Policy

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** — breaking changes to the `SKILL.md` procedure or the
  script CLIs. Users must update their workflows.
- **MINOR** — new patterns, new reference files, new examples,
  new optional CLI flags. Existing behavior is preserved.
- **PATCH** — typo fixes, clarifications, script bug fixes that do
  not change behavior for correct inputs.

Every change is documented here.

---

## Changelog Format

Each entry follows the [Keep a Changelog](https://keepachangelog.com/)
conventions. Changes are grouped under one of these headings:

- **Added** — new features, files, or capabilities.
- **Changed** — changes to existing behavior.
- **Deprecated** — features marked for removal in a future release.
- **Removed** — features removed in this release.
- **Fixed** — bug fixes.
- **Security** — fixes for vulnerabilities.

The `[Unreleased]` section at the top collects changes that are
committed but not yet released. On release, its contents are moved
under a new version heading with the release date.