#!/usr/bin/env python3
"""
Context audit for Agent Skills-compatible sessions.

Reads a session directory and reports token distribution, instruction
survival, stale content, and repetition.

Usage:
    python context_audit.py --session-dir ~/.hermes/sessions/current
    python context_audit.py --session-dir . --compare
    python context_audit.py --session-dir . --json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

CHARS_PER_TOKEN = 3.8


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int(len(text) / CHARS_PER_TOKEN))


def load_session(session_dir: str) -> dict:
    artifacts = {
        "system_prompt": "",
        "skill_index": "",
        "conversation": [],
        "tool_outputs": [],
        "references": [],
    }
    for name in ("system_prompt.txt", "SYSTEM.md", "system.md"):
        path = os.path.join(session_dir, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                artifacts["system_prompt"] = f.read()
            break
    for name in ("skill_index.txt", "skills.txt", "SKILLS.md"):
        path = os.path.join(session_dir, name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                artifacts["skill_index"] = f.read()
            break
    conv_path = os.path.join(session_dir, "conversation.jsonl")
    if os.path.exists(conv_path):
        with open(conv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        artifacts["conversation"].append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    tool_dir = os.path.join(session_dir, "tool_outputs")
    if os.path.isdir(tool_dir):
        for fname in sorted(os.listdir(tool_dir)):
            fpath = os.path.join(tool_dir, fname)
            if os.path.isfile(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    artifacts["tool_outputs"].append(
                        {"file": fname, "content": f.read()}
                    )
    ref_dir = os.path.join(session_dir, "references")
    if os.path.isdir(ref_dir):
        for fname in sorted(os.listdir(ref_dir)):
            fpath = os.path.join(ref_dir, fname)
            if os.path.isfile(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    artifacts["references"].append(
                        {"file": fname, "content": f.read()}
                    )
    return artifacts


def audit(artifacts: dict) -> dict:
    total = 0
    contributors = []

    sp_tokens = estimate_tokens(artifacts["system_prompt"])
    if sp_tokens:
        contributors.append({"source": "system_prompt", "tokens": sp_tokens})
        total += sp_tokens

    si_tokens = estimate_tokens(artifacts["skill_index"])
    if si_tokens:
        contributors.append({"source": "skill_index", "tokens": si_tokens})
        total += si_tokens

    conv_tokens = 0
    conv_texts = []
    for turn in artifacts["conversation"]:
        text = json.dumps(turn)
        conv_texts.append(text)
        conv_tokens += estimate_tokens(text)
    if conv_tokens:
        contributors.append({"source": "conversation", "tokens": conv_tokens})
        total += conv_tokens

    for output in artifacts["tool_outputs"]:
        t = estimate_tokens(output["content"])
        total += t
        contributors.append({"source": f"tool_output:{output['file']}", "tokens": t})

    for ref in artifacts["references"]:
        t = estimate_tokens(ref["content"])
        total += t
        contributors.append({"source": f"reference:{ref['file']}", "tokens": t})

    constraints = []
    for turn in artifacts["conversation"]:
        if turn.get("role") == "user":
            content = turn.get("content", "")
            for sentence in re.split(r"[.!?]\s+", content):
                sentence = sentence.strip()
                if re.match(
                    r"^(must|should|never|always|do not|don't|ensure|make sure|"
                    r"require|need|only|avoid)",
                    sentence, re.IGNORECASE,
                ):
                    constraints.append(sentence)
    context_text = (
        artifacts["system_prompt"]
        + artifacts["skill_index"]
        + " ".join(conv_texts)
        + " ".join(o["content"] for o in artifacts["tool_outputs"])
        + " ".join(r["content"] for r in artifacts["references"])
    )
    survived = sum(1 for c in constraints if c.lower() in context_text.lower())
    survival_rate = survived / len(constraints) if constraints else 1.0

    recent_cutoff = 10
    recent_text = " ".join(json.dumps(t) for t in artifacts["conversation"][-5:])
    stale_tokens = 0
    for turn in artifacts["conversation"][: -recent_cutoff] if len(artifacts["conversation"]) > recent_cutoff else []:
        text = json.dumps(turn)
        words = set(re.findall(r"\b[a-z]{5,}\b", text.lower()))
        recent_words = set(re.findall(r"\b[a-z]{5,}\b", recent_text.lower()))
        if not (words & recent_words):
            stale_tokens += estimate_tokens(text)
    stale_ratio = stale_tokens / conv_tokens if conv_tokens else 0.0

    all_blocks = (
        [artifacts["system_prompt"], artifacts["skill_index"]]
        + conv_texts
        + [o["content"] for o in artifacts["tool_outputs"]]
        + [r["content"] for r in artifacts["references"]]
    )
    ngram_counts = Counter()
    for block in all_blocks:
        words = re.findall(r"\b\w+\b", block.lower())
        for i in range(len(words) - 5):
            ngram_counts[tuple(words[i : i + 6])] += 1
    total_ngrams = sum(ngram_counts.values())
    duplicated = sum(c - 1 for c in ngram_counts.values() if c > 1)
    repetition_ratio = duplicated / total_ngrams if total_ngrams else 0.0

    contributors.sort(key=lambda x: x["tokens"], reverse=True)

    return {
        "total_tokens": total,
        "window_size": 128000,
        "utilization": round(total / 128000, 3),
        "instruction_survival_rate": round(survival_rate, 3),
        "stale_content_ratio": round(stale_ratio, 3),
        "repetition_ratio": round(repetition_ratio, 3),
        "constraint_count": len(constraints),
        "constraints_survived": survived,
        "top_contributors": contributors[:20],
        "timestamp": datetime.utcnow().isoformat(),
    }


def compare_reports(old_path: str, new_path: str) -> str:
    with open(old_path) as f:
        old = json.load(f)
    with open(new_path) as f:
        new = json.load(f)
    lines = ["", "=== Context Audit Comparison ===", ""]
    for key in (
        "total_tokens", "utilization", "instruction_survival_rate",
        "stale_content_ratio", "repetition_ratio",
    ):
        o = old.get(key, 0)
        n = new.get(key, 0)
        delta = n - o
        arrow = "↓" if delta < 0 else "↑" if delta > 0 else "→"
        if key == "instruction_survival_rate":
            arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        lines.append(f"  {key}: {o} → {n}  ({arrow} {abs(delta):.3f})")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit context usage.")
    parser.add_argument("--session-dir", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()

    artifacts = load_session(args.session_dir)
    report = audit(artifacts)

    audit_dir = os.path.expanduser("~/.hermes/context-audit")
    os.makedirs(audit_dir, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    report_path = os.path.join(audit_dir, f"audit-{stamp}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n=== Context Audit: {args.session_dir} ===\n")
        print(f"  Total tokens:            {report['total_tokens']:,}")
        print(f"  Window utilization:      {report['utilization']:.1%}")
        print(f"  Instruction survival:    {report['instruction_survival_rate']:.1%}")
        print(f"  Stale content ratio:     {report['stale_content_ratio']:.1%}")
        print(f"  Repetition ratio:        {report['repetition_ratio']:.1%}")
        print(f"\n  Top contributors:")
        for c in report["top_contributors"][:10]:
            print(f"    {c['source']}: {c['tokens']:,} tokens")
        print(f"\n  Report saved: {report_path}")

    if args.compare:
        reports = sorted(
            os.path.join(audit_dir, f)
            for f in os.listdir(audit_dir)
            if f.startswith("audit-") and f.endswith(".json")
        )
        if len(reports) >= 2:
            print(compare_reports(reports[-2], reports[-1]))
        else:
            print("\n  No previous audit to compare against.")


if __name__ == "__main__":
    main()