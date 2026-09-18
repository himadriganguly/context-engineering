# Installation Guide

This repository contains an Agent Skills-compatible skill plus
optional Python utilities.

> [!WARNING]
> **Use at your own risk.**
>
> The Python utilities inspect files you explicitly provide and use
> heuristic estimates. Review the scripts and input paths before using
> them on sensitive session data. Keep backups of important data
> before applying agent-assisted changes.

---

## 1. Repository layout

The actual installable skill is:

```
skills/context-engineering/
├── SKILL.md
├── references/
├── scripts/
└── templates/
```

Install that directory, **not** the repository root.

The installed directory must have:

```
<runtime-skills-directory>/context-engineering/SKILL.md
```

---

## 2. Requirements

The core skill requires only an Agent Skills-compatible runtime.

The optional Python utilities require:

- **Python 3.9+**

They use only the Python standard library.

Check:

```bash
python3 --version
```

No `pip install` step is required.

---

## 3. Hermes Agent

Hermes supports Agent Skills and GitHub skill taps. Its user-level
skill directory is:

```
~/.hermes/skills/
```

Hermes also supports project-local skills depending on the installation
and project configuration. Consult the Hermes documentation for
runtime-specific precedence rules.

### Local installation

From this repository:

```bash
mkdir -p ~/.hermes/skills
cp -r skills/context-engineering ~/.hermes/skills/
```

Verify:

```bash
ls ~/.hermes/skills/context-engineering/SKILL.md
```

Then restart or refresh the Hermes session if necessary.

### GitHub tap

Hermes supports GitHub skill taps using a repository layout containing
`skills/<skill-name>/SKILL.md`.

For this repository:

```bash
hermes skills tap add himadriganguly/context-engineering
```

Search:

```bash
hermes skills search context-engineering --source github
```

Install:

```bash
hermes skills install \
  himadriganguly/context-engineering/context-engineering
```

The exact installation identifier may depend on the Hermes version.

### Skills Hub publishing

The documented Hermes publishing command is:

```bash
hermes skills publish \
  skills/context-engineering \
  --to github \
  --repo himadriganguly/context-engineering
```

Hermes' public Skills Hub uses a generated catalog snapshot. A GitHub
publication may therefore take time to become visible in the public
catalog.

---

## 4. Claude Code

Claude Code supports the Agent Skills format.

The repository's core `SKILL.md` is designed to be compatible with the
format.

A typical installation uses the runtime's documented skill directory.

For example, if your Claude Code installation uses:

```
~/.claude/skills/
```

copy:

```
skills/context-engineering/
```

there:

```bash
mkdir -p ~/.claude/skills
cp -r skills/context-engineering ~/.claude/skills/
```

Verify the skill using Claude Code's current skill-discovery mechanism.

> **Important**
>
> This repository does not provide a Claude Code session adapter.
>
> The Python audit utility should therefore not be assumed to
> understand Claude Code's native session storage.
>
> The Markdown skill remains usable independently of the audit utility.

---

## 5. Cursor

Cursor supports the Agent Skills format.

If your Cursor installation uses:

```
~/.cursor/skills/
```

install:

```bash
mkdir -p ~/.cursor/skills
cp -r skills/context-engineering ~/.cursor/skills/
```

Verify that Cursor can discover the skill using the current Cursor
skill interface.

> **Important**
>
> The Python audit utility is not a native Cursor session integration.
>
> Use it only if you can provide a compatible exported/session
> directory.

---

## 6. OpenAI Codex

Codex supports Skills.

If your Codex environment uses:

```
~/.codex/skills/
```

install:

```bash
mkdir -p ~/.codex/skills
cp -r skills/context-engineering ~/.codex/skills/
```

Verify using the current Codex skill-discovery interface.

> **Important**
>
> This repository does not claim native Codex session-audit
> integration.
>
> The core skill can be used without the audit utility.

---

## 7. Gemini CLI

Gemini CLI supports the Agent Skills model.

If your environment uses:

```
~/.gemini/skills/
```

install:

```bash
mkdir -p ~/.gemini/skills
cp -r skills/context-engineering ~/.gemini/skills/
```

Verify the skill using the current Gemini CLI skill interface.

> **Important**
>
> The Python audit utility is not a Gemini CLI session integration.
>
> It requires a compatible session-artifact directory.

---

## 8. OpenClaw

This repository does not currently claim independently validated
OpenClaw compatibility.

If your OpenClaw version supports the Agent Skills format, you may test
the core skill according to OpenClaw's current documentation.

Do not assume that the Python audit utility can read OpenClaw's native
session data.

If you validate OpenClaw support, record:

- OpenClaw version
- operating system
- model/provider
- installation path
- whether `SKILL.md` loads
- whether references load
- whether scripts run
- the session-artifact format used by the scripts

---

## 9. Other Agent Skills runtimes

For another runtime:

1. Confirm that it supports the Agent Skills format.
2. Find its documented skill directory.
3. Copy:

   ```
   skills/context-engineering/
   ```

   into that directory.

4. Verify that `SKILL.md` is discovered.
5. Test the Markdown procedure.
6. Treat the Python scripts as optional until their required input
   format is available.

Do not infer full runtime compatibility merely because a runtime
recognizes `SKILL.md`.

---

## 10. Using the audit utility

The audit utility expects a supported artifact layout such as:

```
session/
├── system_prompt.txt
├── skill_index.txt
├── conversation.jsonl
├── tool_outputs/
│   └── ...
└── references/
    └── ...
```

Run:

```bash
python3 skills/context-engineering/scripts/context_audit.py \
  --session-dir PATH
```

If your runtime uses a different layout, create an adapter or export
the required information into this format.

### Configure the context window

The default is:

```
128000
```

but that is only a default.

Use the actual model/runtime value where known:

```bash
python3 skills/context-engineering/scripts/context_audit.py \
  --session-dir PATH \
  --window-size 200000
```

### Choose the output directory

```bash
python3 skills/context-engineering/scripts/context_audit.py \
  --session-dir PATH \
  --output-dir ./audit-results
```

### JSON output

```bash
python3 skills/context-engineering/scripts/context_audit.py \
  --session-dir PATH \
  --json
```

### Compare reports

```bash
python3 skills/context-engineering/scripts/context_audit.py \
  --session-dir PATH \
  --compare
```

---

## 11. Using the token estimator

### Text

```bash
python3 skills/context-engineering/scripts/token_estimator.py \
  --text "hello"
```

### File

```bash
python3 skills/context-engineering/scripts/token_estimator.py \
  --file path/to/file
```

### Directory

```bash
python3 skills/context-engineering/scripts/token_estimator.py \
  --dir . \
  --recursive \
  --top 20
```

The result is an **estimate**.

It is not an exact tokenizer count.

---

## 12. Verify the installation

At minimum:

```bash
python3 -m py_compile \
  skills/context-engineering/scripts/context_audit.py \
  skills/context-engineering/scripts/token_estimator.py
```

Then:

```bash
python3 skills/context-engineering/scripts/token_estimator.py \
  --text "installation test"
```

If you have a compatible session fixture:

```bash
python3 skills/context-engineering/scripts/context_audit.py \
  --session-dir PATH \
  --json
```

Finally, verify that your target runtime discovers:

```
context-engineering
```

---

## 13. Uninstall

Remove the installed skill directory from the runtime's skill location.

For Hermes:

```bash
rm -rf ~/.hermes/skills/context-engineering
```

If you created audit reports using the default location:

```bash
rm -rf ~/.context-engineering/audits
```

If you selected another output directory, remove that directory
instead.

---

## 14. Reporting runtime compatibility

If you test this skill on another runtime, please report:

```
Runtime:
Runtime version:
OS:
Model/provider:
Skill installation method:
SKILL.md discovered:
References loaded:
Python available:
Audit script tested:
Session artifact format:
Result:
```

This project intentionally distinguishes **format compatibility** from
**runtime-specific script compatibility**.