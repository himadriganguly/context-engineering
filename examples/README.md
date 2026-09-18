# Examples

The full case studies live in [../EXAMPLES.md](../EXAMPLES.md). This
directory holds runnable reproductions of each scenario.

## Index

1. **Long coding session that forgot its architecture**
   An agent edits files it was told never to touch, after a 3-hour
   session pushes its working memory to 88% full.

2. **Customer support agent that drifts from policy**
   A support agent promises a $200 refund despite a $50 hard cap,
   because the policy got buried under 30 turns of conversation.

3. **Research assistant that loses track of sources**
   An agent invents plausible-sounding citations after reading 40
   papers, because 55% of its context is stale paper detail.

4. **DevOps agent debugging a production incident**
   An on-call agent thrashes on 12 log files, re-suggesting fixes
   it already tried, because its window is 95% full.

5. **Multi-day project that resumes cleanly**
   A founder re-explains context every morning until a resume brief
   cuts catch-up time from 15 minutes to 30 seconds.

Each scenario in `../EXAMPLES.md` includes:

- **The symptom** — what the human notices going wrong.
- **The audit** — the actual numbers the script reports.
- **The fix** — the specific steps taken.
- **The outcome** — before/after metrics in a table.

## What to Take From These

Every example follows the same five-step procedure:

1. **Measure** — run the audit. Get numbers, not opinions.
2. **Name the failure** — poisoning, clash, confusion,
   lost-in-middle, or overload.
3. **Move content to the right tier** — off the always-on desk and
   into on-demand references, or compress it into a brief.
4. **Write the rule down** — in `context-profile.yaml`, so the fix
   persists across sessions.
5. **Re-measure** — confirm the numbers improved and quality did
   not regress.

The specific fixes differ. The procedure does not. That is the point
of the skill: turn a vague, hard problem into a repeatable procedure.

## Adding Your Own Example

If you have a real-world case where this skill solved a problem,
open a pull request adding it to `../EXAMPLES.md`. Concrete numbers
beat abstract advice. Include:

- The symptom (what the human noticed).
- The audit output (paste the actual report).
- The fix (specific steps).
- Before/after metrics in a table.

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for style rules.