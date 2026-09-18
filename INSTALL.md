# Installation Guide

This skill conforms to the [Agent Skills specification](https://agentskills.io).
Installation is the same idea for every compatible runtime: **place the
`context-engineering/` directory where your agent looks for skills.**

The paths differ. The procedure does not. This guide covers every major
runtime, plus installation methods for teams, and a troubleshooting
section at the end.

---

## Table of Contents

- [Before You Install](#before-you-install)
- [1. Hermes Agent (Nous Research)](#1-hermes-agent-nous-research)
- [2. Claude Code](#2-claude-code)
- [3. Cursor](#3-cursor)
- [4. OpenAI Codex (CLI and IDE)](#4-openai-codex-cli-and-ide)
- [5. Gemini CLI](#5-gemini-cli)
- [6. OpenClaw and Other Runtimes](#6-openclaw-and-other-runtimes)
- [7. Install via Git Submodule (for Teams)](#7-install-via-git-submodule-for-teams)
- [8. Install via npm or degit](#8-install-via-npm-or-degit)
- [Post-Install Checklist](#post-install-checklist)
- [Uninstall](#uninstall)
- [Troubleshooting](#troubleshooting)

---

## Before You Install

Three prerequisites, none of them difficult.

### 1. Python 3.9 or later

The two scripts in `scripts/` are written in Python and use only the
standard library. Check your version:

```bash
python3 --version
```

You should see `Python 3.9.x` or later. If you see 3.8 or earlier,
upgrade. On macOS, the system Python is often old — install a newer
one via [Homebrew](https://brew.sh) (`brew install python@3.11`) or
from [python.org](https://python.org).

No `pip install` step is required. The scripts have zero external
dependencies.

### 2. The skill directory

You should have a directory named `context-engineering/` containing
`SKILL.md` at its top level. If you downloaded the project as a zip
from GitHub, unzip it first:

```bash
unzip context-engineering-skill.zip
cd context-engineering-skill
```

The directory is now ready to be installed. If you are cloning from a
Git repository instead, `git clone` and `cd` into it.

### 3. A terminal

All install commands are run in a shell. On macOS and Linux this is
Terminal. On Windows, use WSL (recommended) or PowerShell. The
commands below assume a POSIX shell (`bash` or `zsh`); Windows users
running PowerShell should translate `cp` to `Copy-Item` and
`mkdir -p` to `New-Item -ItemType Directory -Force`.

---

## 1. Hermes Agent (Nous Research)

Hermes loads skills from two locations:

- **User-level (global):** `~/.hermes/skills/`
- **Project-level (per-repo):** `.hermes/skills/` in the project root

Project-level skills override user-level skills with the same name.
Use project-level when the skill should be tied to one repository;
use user-level when you want the skill available everywhere.

### Install globally

```bash
mkdir -p ~/.hermes/skills
cp -r context-engineering ~/.hermes/skills/
```

The result:

```
~/.hermes/skills/
└── context-engineering/
    ├── SKILL.md
    ├── scripts/
    ├── references/
    └── ...
```

### Install per-project

```bash
cd /path/to/your/project
mkdir -p .hermes/skills
cp -r /path/to/context-engineering .hermes/skills/
```

The result:

```
your-project/
├── .hermes/
│   └── skills/
│       └── context-engineering/
│           ├── SKILL.md
│           └── ...
└── ...
```

### Verify

Start a Hermes session and ask:

> "List your available skills."

`context-engineering` should appear in the list with its description.
You can also ask:

> "What does the context-engineering skill do?"

Hermes should read `SKILL.md` and summarise it.

### Optional: auto-audit on session start

If you want the agent to run the audit automatically at the start of
every session, add this to your project's `AGENTS.md`:

```markdown
## Session Start

At the beginning of every session, run:

    python .hermes/skills/context-engineering/scripts/context_audit.py \
        --session-dir "$HERMES_SESSION_DIR"

If instruction survival is below 0.7 or utilization is above 0.8,
load the context-engineering skill and follow its procedure.
```

Replace `$HERMES_SESSION_DIR` with the environment variable or path
that Hermes uses for the current session. Check `hermes --help` or
the Hermes documentation if you are not sure.

### Optional: conditional activation

By default, the skill appears in the skill index every turn. If you
want it to load only when relevant, the `SKILL.md` frontmatter
already includes the metadata field Hermes uses:

```yaml
metadata:
  category: agent-infrastructure
```

You can add:

```yaml
metadata:
  hermes:
    auto_load: false
```

The skill is then registered but not loaded into the index. The agent
loads it when the description matches the task.

---

## 2. Claude Code

Claude Code reads skills from:

- **User-level:** `~/.claude/skills/`
- **Project-level:** `.claude/skills/` in the project root

### Install

```bash
mkdir -p ~/.claude/skills
cp -r context-engineering ~/.claude/skills/
```

Or, for a single project:

```bash
cd /path/to/your/project
mkdir -p .claude/skills
cp -r /path/to/context-engineering .claude/skills/
```

### Verify

In a Claude Code session, type:

```
/skills
```

You should see `context-engineering` listed. Invoke it with:

```
Use the context-engineering skill to audit this session.
```

### Notes

- Claude Code caches the skill index at session start. If you install
  the skill while a session is running, restart the session to see it.
- The skill's Python scripts run in Claude Code's sandbox. If
  Python is not available in the sandbox, the scripts will not run,
  but the Markdown content of `SKILL.md` and the references will
  still be usable.

---

## 3. Cursor

Cursor reads skills from:

- **User-level:** `~/.cursor/skills/`
- **Project-level:** `.cursor/skills/`

### Install

```bash
mkdir -p ~/.cursor/skills
cp -r context-engineering ~/.cursor/skills/
```

Or per-project:

```bash
cd /path/to/your/project
mkdir -p .cursor/skills
cp -r /path/to/context-engineering .cursor/skills/
```

### Verify

Cursor surfaces skills in the skill picker (Cmd+Shift+P on macOS,
Ctrl+Shift+P on Windows/Linux, then search for "skills"). In Agent
mode, mention the skill to invoke it:

```
@context-engineering audit this session
```

---

## 4. OpenAI Codex (CLI and IDE)

Codex reads skills from:

- **User-level:** `~/.codex/skills/`
- **Project-level:** `.codex/skills/`

### Install

```bash
mkdir -p ~/.codex/skills
cp -r context-engineering ~/.codex/skills/
```

Or per-project:

```bash
cd /path/to/your/project
mkdir -p .codex/skills
cp -r /path/to/context-engineering .codex/skills/
```

### Verify

In a Codex session, the skill index is available via the codex CLI:

```bash
codex skills list
```

The command should include `context-engineering`.

---

## 5. Gemini CLI

Gemini CLI reads skills from:

- **User-level:** `~/.gemini/skills/`
- **Project-level:** `.gemini/skills/`

### Install

```bash
mkdir -p ~/.gemini/skills
cp -r context-engineering ~/.gemini/skills/
```

Or per-project:

```bash
cd /path/to/your/project
mkdir -p .gemini/skills
cp -r /path/to/context-engineering .gemini/skills/
```

### Verify

In a Gemini CLI session:

```
/skills
```

The list should include `context-engineering`.

---

## 6. OpenClaw and Other Runtimes

Any runtime that follows the [Agent Skills specification](https://agentskills.io)
will work. The canonical fallback location is:

- **User-level:** `~/.agent-skills/`
- **Project-level:** `.agent-skills/`

### Install

```bash
mkdir -p ~/.agent-skills
cp -r context-engineering ~/.agent-skills/
```

If your runtime uses a different path, consult its documentation and
copy the `context-engineering/` directory there. The skill itself is
runtime-agnostic — it is plain Markdown plus standalone Python
scripts. Nothing in the content is Hermes-specific or
Claude-specific.

### Runtime compatibility matrix

| Runtime | User-level path | Project-level path |
|---|---|---|
| Hermes Agent | `~/.hermes/skills/` | `.hermes/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| OpenAI Codex | `~/.codex/skills/` | `.codex/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| OpenClaw | `~/.agent-skills/` | `.agent-skills/` |
| Generic fallback | `~/.agent-skills/` | `.agent-skills/` |

---

## 7. Install via Git Submodule (for Teams)

If you want a specific version of the skill pinned to your project
and shared with everyone who clones the repository, use a Git
submodule.

### Add the submodule

```bash
cd /path/to/your/project
mkdir -p .hermes/skills
git submodule add https://github.com/<your-org>/context-engineering-skill.git \
    .hermes/skills/context-engineering
git submodule update --init --recursive
```

The submodule pins a specific commit. When you commit your project,
the commit SHA of the skill is recorded in `.gitmodules`. Everyone
who clones your project gets the same version.

### Update the submodule later

```bash
git submodule update --remote .hermes/skills/context-engineering
git add .hermes/skills/context-engineering
git commit -m "Update context-engineering skill to latest"
```

The update is a normal commit — it can be reviewed, reverted, and
annotated like any other change.

### Why submodules

Submodules make the version explicit and reviewable. When you update
the skill, the update shows up as a change to a single SHA in a
commit. A reviewer can see exactly what changed. This is the right
choice for teams that want reproducibility.

The downside is that submodules add complexity for contributors who
are not used to them. If your team is small and informal, a plain
`cp -r` may be simpler.

---

## 8. Install via npm or degit

If you prefer to distribute the skill through npm or a similar
package manager, `degit` fetches a Git repository without the history:

```bash
npx degit <your-org>/context-engineering-skill ./context-engineering
cp -r context-engineering ~/.hermes/skills/
```

`degit` requires Node.js to be installed but does not require the
target project to be a Node project.

This method is convenient for one-off installs. It does not provide
version pinning or automatic updates — for those, use the submodule
method.

---

## Post-Install Checklist

After installing, verify these four things.

### 1. The directory exists in the correct location

```bash
ls ~/.hermes/skills/context-engineering/SKILL.md
```

The output should be the path to `SKILL.md`. If the file is not
found, the directory is not in the right place. `SKILL.md` must be at
`<skills-path>/context-engineering/SKILL.md` — not nested any deeper.

### 2. The scripts are executable

```bash
chmod +x ~/.hermes/skills/context-engineering/scripts/*.py
```

This is not strictly required — you can always invoke a Python script
with `python3 script.py` regardless of its executable bit — but
setting it means you can also run the scripts directly:

```bash
~/.hermes/skills/context-engineering/scripts/token_estimator.py --text "hello"
```

### 3. Python 3.9+ is available

```bash
python3 --version
```

Should print `Python 3.9.x` or later. If it prints 3.8 or earlier,
install a newer version. The scripts are not tested against 3.8 and
will not work on 3.7.

### 4. The agent can see the skill

Ask your agent:

> "List your available skills."

Or, in a chat:

> "What skills do you have available?"

`context-engineering` should appear in the response with its
description. If it does not appear, see the [Troubleshooting](#troubleshooting)
section below.

---

## Uninstall

Removing the skill is one command:

```bash
rm -rf ~/.hermes/skills/context-engineering
```

No other state is modified. The audit reports live in
`~/.hermes/context-audit/` — delete that directory too if you want a
completely clean removal:

```bash
rm -rf ~/.hermes/context-audit
```

If you installed per-project:

```bash
rm -rf /path/to/your/project/.hermes/skills/context-engineering
```

If you installed as a Git submodule, remove it properly:

```bash
git submodule deinit -f .hermes/skills/context-engineering
git rm -f .hermes/skills/context-engineering
rm -rf .git/modules/.hermes/skills/context-engineering
```

The first two commands remove the submodule from the project. The
third removes the cached Git data. Without the third command, Git
retains a stale reference.

---

## Troubleshooting

### The agent does not list the skill

**Cause 1:** The directory is in the wrong location.

Check that `SKILL.md` is at
`<skills-path>/context-engineering/SKILL.md`. If it is nested one
level deeper — for example,
`<skills-path>/context-engineering-skill/context-engineering/SKILL.md`
— move it up one level.

```bash
# See the actual layout
find ~/.hermes/skills -maxdepth 3 -name SKILL.md
```

**Cause 2:** The YAML frontmatter in `SKILL.md` is invalid.

A missing `name:` or `description:` field will cause the skill to be
ignored. Verify with:

```bash
head -20 ~/.hermes/skills/context-engineering/SKILL.md
```

You should see:

```
---
name: context-engineering
description: ...
license: MIT
...
---
```

The three lines between the `---` markers must include `name:`,
`description:`, and `license:`. If any are missing or malformed, the
skill will not load.

**Cause 3:** The runtime caches the skill index at startup.

Restart the agent. Most runtimes load the skill index once at session
start and do not re-scan the filesystem during a session.

### The audit script fails with "command not found"

**Cause:** Python is not on the PATH, or is named `python` instead
of `python3`.

Try:

```bash
python --version
```

If that works and `python3 --version` does not, use `python` in all
commands. If neither works, install Python 3.9+ from
[python.org](https://python.org) or via your system's package
manager.

### The audit script produces a division-by-zero error

**Cause:** The script divides by conversation token count when
computing stale and repetition ratios. If a session directory has
zero conversation turns, the divisor is zero.

This should be handled by the `if conv_tokens else 0.0` guard. If you
see this error, you may be running an older version of the script.
Update to the latest release.

### The audit reports zero tokens

**Cause:** The script expects a session directory with a specific
layout. If your runtime stores sessions differently, the script finds
no content to measure.

Check what the script found:

```bash
python3 scripts/context_audit.py --session-dir /path/to/session --json
```

If the JSON report shows `"total_tokens": 0`, the directory does not
contain the expected files. The script looks for:

- `system_prompt.txt` or `SYSTEM.md` or `system.md`
- `skill_index.txt` or `skills.txt` or `SKILLS.md`
- `conversation.jsonl`
- `tool_outputs/` directory
- `references/` directory

Every component is optional. If none are present, the audit reports
zero. Adapt the `load_session()` function in `context_audit.py` to
read your runtime's format.

### Instruction survival rate looks wrong

**Cause:** The script extracts user constraints by matching imperative
sentences that start with one of these words:

```
must, should, never, always, do not, don't, ensure,
make sure, require, need, only, avoid
```

If your constraints use different language — for example, "the system
shall..." — they are not being counted.

Edit the regex in `context_audit.py` to add your patterns. The
relevant code is:

```python
if re.match(
    r"^(must|should|never|always|do not|don't|ensure|make sure|"
    r"require|need|only|avoid)",
    sentence, re.IGNORECASE,
):
```

Add your verbs to the alternation.

### The audit script cannot read a file

**Cause:** File permissions, or the file is a broken symlink.

The script handles unreadable files gracefully — it skips them and
continues. If you want to see which files were skipped, run with
`--json` and check the `top_contributors` list. Files that could not
be read will simply be absent.

To fix the underlying issue:

```bash
chmod +r /path/to/unreadable/file
```

Or remove the broken symlink:

```bash
find /path/to/session -xtype l -delete
```

### The scripts run but output nothing

**Cause:** The output may be buffered. Try running with `-u`
(unbuffered) mode:

```bash
python3 -u scripts/context_audit.py --session-dir /tmp
```

If the output still does not appear, check that you are running the
correct version of the script. Run:

```bash
python3 scripts/context_audit.py --help
```

You should see an argparse help message listing `--session-dir`,
`--json`, and `--compare`. If you see a Python traceback or an
unrecognised-argument error, the script file may be corrupted. Re-download
from the repository.

### Everything works but the agent does not use the skill

**Cause:** The agent only loads a skill when the task matches the
skill's description. If you ask the agent something unrelated, it
will not load `context-engineering`.

To invoke the skill explicitly, phrase the request in terms the
description matches:

> "My session feels bloated and you're ignoring my earlier
> instructions. Use the context-engineering skill to diagnose and
> fix it."

The trigger phrases are: "output quality degrades," "sessions feel
bloated," "ignores instructions," "token costs spike," "new project
needs deliberate context architecture."

If the agent still does not load the skill, it may not be indexing
skills at all. Verify by asking it to list its skills. If
`context-engineering` is not in the list, see the first
troubleshooting entry above.

---

## Getting Help

If none of the troubleshooting entries solve your problem, open an
issue on the GitHub repository. Include:

- Your operating system and version.
- Your Python version (`python3 --version`).
- Your agent runtime and version.
- The exact command you ran and the full output.
- What you expected to happen.

A short reproduction is worth more than a long description. If you
can point to a specific command that fails, that is the fastest path
to a fix.