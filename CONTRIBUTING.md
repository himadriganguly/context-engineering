# Contributing

Thanks for considering a contribution. This skill exists because context
engineering is the foundation of reliable agents, and no single person
has all the patterns. The best contributions come from people running
agents in production, hitting real failure modes, and figuring out what
actually works.

This guide tells you what we want, what we do not want, and how to
submit your work.

---

## Table of Contents

- [What We Want](#what-we-want)
- [What We Do Not Want](#what-we-do-not-want)
- [How to Contribute](#how-to-contribute)
- [Style Guide](#style-guide)
- [Versioning](#versioning)
- [Code of Conduct](#code-of-conduct)

---

## What We Want

Five categories of contribution, in rough order of value to the project.

### 1. New degradation patterns

If you have observed a context failure mode not covered in
[`references/degradation-signals.md`](references/degradation-signals.md),
add it. The current taxonomy has five classes — poisoning, clash,
confusion, lost-in-middle, overload. If your failure does not fit any
of them, we want to know.

A good new pattern includes:

- **A short name** — one or two words, like "poisoning" or "clash."
- **A one-sentence definition** — what the class actually is.
- **Signals** — observable symptoms that indicate this class.
- **Common sources** — where the failure typically originates.
- **A fix procedure** — specific, ordered steps.
- **A verification step** — how to confirm the fix worked.

Add it to `references/degradation-signals.md` in the same format as
the existing five classes. Also add it to the summary table at the
bottom of the file.

### 2. Real-world case studies

The examples in [`EXAMPLES.md`](EXAMPLES.md) are the most-read part of
the project. Concrete numbers beat abstract advice every time. If you
have a real case where this skill solved a problem, we want it.

A good case study includes:

- **The symptom** — what the human noticed going wrong. One paragraph.
- **The audit** — paste the actual audit output. Real numbers, not
  approximations.
- **The fix** — the specific steps taken. Not "I applied best
  practices" but "I moved the architecture doc into references/ and
  compressed history to a resume brief."
- **Before/after metrics** — a table comparing the same metrics
  before and after the fix.

Anonymize as needed. Remove company names, API keys, and any content
that identifies a customer. But keep the numbers — they are the point.

### 3. New runtime support

If you use a runtime not listed in [`INSTALL.md`](INSTALL.md), add
install instructions. The current list is Hermes, Claude Code, Cursor,
OpenAI Codex, Gemini CLI, and OpenClaw. If your runtime follows the
Agent Skills specification and uses a different skills path, tell us
what it is.

A good runtime addition includes:

- **The runtime name** and a link to its documentation.
- **The user-level skills path** and the project-level path.
- **Exact install commands** — copy-paste ready.
- **A verification step** — how the user confirms the skill is
  loaded.
- **Any runtime-specific quirks** — for example, if the runtime
  caches the skill index and needs a restart.

Add a new numbered section to `INSTALL.md`.

### 4. Script improvements

The two scripts in `scripts/` are intentionally simple. Improvements
that keep them simple are welcome. Improvements that make them complex
are not.

Good script changes:

- **Bug fixes** — the script crashes or produces wrong output in
  some input case.
- **Additional input formats** — the `load_session()` function in
  `context_audit.py` currently expects a specific layout; adding
  support for another layout is useful.
- **Performance improvements** — the audit runs faster on large
  sessions without changing its output.
- **Better error messages** — the script tells the user what went
  wrong and how to fix it.

Bad script changes:

- Adding external dependencies. The scripts must run on a bare
  Python 3.9+ install with no `pip install` step.
- Changing the output format in a way that breaks downstream tools.
- Adding configuration options that could be handled by editing the
  script directly.

If you are unsure whether a change is in scope, open an issue first.

### 5. Translations

`SKILL.md` and `README.md` are read by developers all over the world.
Translations are welcome. The convention is:

- `SKILL.es.md` for Spanish.
- `SKILL.fr.md` for French.
- `SKILL.de.md` for German.
- `SKILL.ja.md` for Japanese.
- `SKILL.zh.md` for Mandarin.

Keep the translation alongside the original. Do not replace it. Add a
line at the top of the translation linking back to the English version
so readers know which one is authoritative.

Translations of `SKILL.md` must preserve the YAML frontmatter — the
`name`, `description`, and other fields are read by the runtime and
must remain valid. Translate only the body of the file.

---

## What We Do Not Want

Three categories of change that will be politely declined.

### 1. External Python dependencies

The scripts must run on a bare Python 3.9+ installation. This means:

- No `pip install` step.
- No `requirements.txt` file.
- No imports outside the standard library.

The reason is distribution. A skill that requires installing Python
packages will not be installed. A skill that runs anywhere Python
runs will. The character-based token estimator is less accurate than
a real tokenizer, but it works identically across every environment.
That tradeoff is deliberate.

If you need a feature that requires an external dependency, propose
it as an optional add-on script in a new directory, with clear
instructions that it requires the dependency. Do not modify the core
scripts.

### 2. Runtime-specific hacks in `SKILL.md`

`SKILL.md` must remain runtime-agnostic. Runtime-specific behavior
belongs in one of two places:

- **In the `metadata` frontmatter** — for example,
  `metadata.hermes.fallback_for_toolsets`. The runtime reads its own
  namespace and ignores the rest.
- **In a `references/` file** — a runtime-specific guide that loads
  on demand for users of that runtime.

Do not put `if runtime == 'hermes'` logic in the body of `SKILL.md`.
The skill is loaded by any compliant runtime, and the body must make
sense to all of them.

### 3. Uncontrolled always-on cost

Any change that increases the always-on token cost of the skill must
justify the increase. The skill is loaded into every session by every
user who installs it. A 500-token addition to `SKILL.md` costs 500
tokens multiplied by every session of every user. That is real money.

Before adding to `SKILL.md`, ask:

- Can this go in a `references/` file instead? Those are loaded only
  when needed.
- Can this be shortened? A 200-token version of the same instruction
  is better than a 500-token version.
- Is this necessary for the core procedure? If not, it belongs in
  a reference.

Additions to `references/`, `scripts/`, `templates/`, and `examples/`
have no such constraint — those are not loaded on every session.

---

## How to Contribute

The standard GitHub fork-and-PR workflow.

### Step 1 — Open an issue first

For anything larger than a typo fix, open an issue describing what you
want to change and why. This serves two purposes:

- It gives the maintainers a chance to say "yes, we want this" or
  "actually, this is out of scope" before you write the code.
- It creates a place for discussion that becomes the rationale for
  the change.

Small fixes — typos, broken links, one-line clarifications — can skip
the issue and go straight to a pull request.

### Step 2 — Fork the repository

```bash
# On GitHub, click the "Fork" button, then:
git clone https://github.com/<your-username>/context-engineering-skill.git
cd context-engineering-skill
```

### Step 3 — Create a branch

```bash
git checkout -b my-improvement
```

Use a short, descriptive branch name. Good names:

- `add-poisoning-example`
- `fix-audit-crash-on-empty-dir`
- `translate-skill-to-spanish`

Bad names:

- `patch-1`
- `my-changes`
- `fix`

### Step 4 — Make your changes

Follow the style guide below. Add a changelog entry under
`## [Unreleased]` in `CHANGELOG.md` if your change is user-visible.

### Step 5 — Test

Run the scripts to make sure they still work:

```bash
python3 scripts/token_estimator.py --text "test"
python3 scripts/context_audit.py --session-dir /tmp
```

If you added a new reference file, verify it is valid Markdown:

```bash
# Check for unbalanced code fences
grep -c '^```' references/your-new-file.md
# Should be even
```

If you changed `SKILL.md` frontmatter, verify it still parses:

```bash
python3 - <<'PY'
import re
text = open("SKILL.md").read()
m = re.match(r"^---\n(.*?)\n---", text, re.S)
assert m, "Missing frontmatter"
for field in ("name:", "description:", "license:"):
    assert field in m.group(1), f"Missing {field}"
print("Frontmatter OK")
PY
```

### Step 6 — Commit

Write a clear commit message. Use the imperative mood ("Add X", not
"Added X" or "Adds X").

Good commit messages:

```
Add poisoning example to EXAMPLES.md

Adds a real-world case study of context poisoning from a customer
support session. Includes audit output, the fix applied, and
before/after metrics.
```

Bad commit messages:

```
update
fixed stuff
WIP
```

### Step 7 — Push and open a pull request

```bash
git push origin my-improvement
```

Then open a pull request on GitHub. In the PR description:

- Reference the issue you opened in Step 1 (if applicable).
- Describe what the change does and why.
- Note anything reviewers should pay particular attention to.
- If your change affects the audit metrics, include before/after
  numbers from your own testing.

### Step 8 — Respond to review

A maintainer will review your PR. They may ask for changes. This is
normal — reviews improve the change. Respond to comments, push
updates to the same branch, and the PR will update automatically.

Once approved, a maintainer will merge. You do not need to do
anything else.

---

## Style Guide

Small details that keep the project consistent.

### Markdown

- Use ATX headers (`#`, `##`, `###`), not setext (`===`, `---`).
- Wrap prose at 72–80 characters where practical. Long lines are
  harder to review in a diff.
- Use fenced code blocks with a language tag:
  - ```` ```bash ```` for shell commands.
  - ```` ```yaml ```` for YAML.
  - ```` ```python ```` for Python.
  - ```` ```markdown ```` for Markdown examples.
- Use `-` for unordered lists, not `*`.
- Use one blank line between paragraphs, and one blank line before
  and after headers.
- Link to other files in the repo using relative paths, not absolute
  GitHub URLs. `[INSTALL.md](INSTALL.md)` works both on GitHub and in
  a local clone. `https://github.com/.../INSTALL.md` works only on
  GitHub.

### YAML frontmatter

- Two-space indentation.
- No trailing whitespace.
- Strings that contain `:` must be quoted.
- Long descriptions can wrap with `>` for folded scalars:
  ```yaml
  description: >
    This is a long description that wraps across
    multiple lines but is read as one line.
  ```

### Python

- 4-space indentation. No tabs.
- Type hints where they clarify the signature:
  ```python
  def estimate_tokens(text: str) -> int:
  ```
- No external dependencies. Standard library only.
- Prefer clarity over cleverness. A 10-line loop is better than a
  3-line comprehension if the loop is easier to read.
- Docstrings on every function that does something non-obvious.
- No `print()` debugging statements in committed code.
- Run `python3 -m py_compile scripts/*.py` before committing to catch
  syntax errors.

### Naming

- **Files** — lowercase, hyphens for spaces:
  `degradation-signals.md`, not `DegradationSignals.md`.
- **Functions** — snake_case: `estimate_tokens`, `load_session`.
- **Constants** — UPPER_SNAKE_CASE: `CHARS_PER_TOKEN`.
- **Classes** — PascalCase: not applicable to this project currently,
  but reserved for future use.

### Language

- American or British English: pick one per file and be consistent.
  The current files use American English.
- Second person ("you") when addressing the reader directly.
- Imperative mood for instructions ("Run the script", not "The script
  should be run").
- Active voice where possible.

### Tone

- Direct. Say what you mean. Avoid hedging.
- Concrete. Numbers, examples, and specific instructions beat
  abstract advice.
- Respectful. Assume the reader is smart but does not have your
  context. Explain jargon the first time it appears.

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** — breaking changes to the `SKILL.md` procedure or to a
  script's command-line interface. Users must update their workflows.
- **MINOR** — new patterns, new reference files, new examples, new
  optional CLI flags. Existing behavior is preserved.
- **PATCH** — typo fixes, clarifications, script bug fixes that do
  not change behavior for correct inputs.

You do not need to update the version number in your pull request.
That happens at release time. You only need to add an entry under
`## [Unreleased]` in `CHANGELOG.md`.

### What counts as a breaking change for a skill

For a library, "breaking change" has an obvious meaning: existing code
stops compiling. For a skill, the definition is subtler. The "API" of
a skill is its procedure — the steps the agent follows. A change is
breaking if it can cause an existing agent to behave incorrectly.

Examples of breaking changes:

- Reordering the five steps in `SKILL.md`.
- Removing a step.
- Changing the meaning of a step.
- Renaming a CLI flag or removing it.
- Changing the `context-profile.yaml` schema in a way that
  invalidates existing files.

Examples of non-breaking changes:

- Adding a new reference file.
- Adding a new example to `EXAMPLES.md`.
- Adding an optional CLI flag to a script.
- Clarifying a sentence without changing its meaning.
- Fixing a typo.

When in doubt, ask in the pull request. It is better to over-mark a
change as breaking than to surprise users with a behavior change in a
patch release.

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/)
v2.1. The short version:

- Be kind. Assume good faith.
- Critique ideas, not people.
- No harassment, no discrimination, no personal attacks.
- Disagreements about technical direction are fine. Disagreements
  about how to treat other contributors are not.

If you experience or witness unacceptable behavior, open an issue
marked `[conduct]` or contact a maintainer privately. Reports are
handled confidentially.

The full text of the Contributor Covenant is available at
https://www.contributor-covenant.org/version/2/1/code_of_conduct/.

---

## Questions

If anything in this guide is unclear, open an issue and ask. A
question is a contribution — it tells us where the documentation is
missing or the process is confusing.

We would rather answer ten questions than have one contributor give
up because they could not figure out how to get started.

Thanks for reading this far. Now go write something.