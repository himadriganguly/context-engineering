#!/usr/bin/env python3
"""
Context audit for Agent Skills-compatible session artifacts.

The script reads a directory containing supported session artifacts and
reports lightweight estimates for context size, instruction survival,
stale content, repetition, and major contributors.

These metrics are heuristics. They are not semantic measurements of
model attention or reasoning quality.

Usage:
    python context_audit.py --session-dir PATH
    python context_audit.py --session-dir PATH --window-size 200000
    python context_audit.py --session-dir PATH --json
    python context_audit.py --session-dir PATH --compare
"""

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone

DEFAULT_CHARS_PER_TOKEN = 3.8
DEFAULT_WINDOW_SIZE = 128_000
DEFAULT_OUTPUT_DIR = "~/.context-engineering/audits"

def estimate_tokens(text: str, chars_per_token: float) -> int:
    """Return a character-based estimate of token count."""
    if not text:
        return 0
    return max(1, int(len(text) / chars_per_token))

def read_text(path: str) -> str:
    """Read a UTF-8 text file, replacing invalid byte sequences."""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()

def load_session(session_dir: str) -> dict:
    """
    Load artifacts from the supported generic session layout.

    The loader intentionally does not claim to understand any runtime's
    private session format. Runtimes may need an adapter that exports
    their session into this layout.
    """
    artifacts = {
        "system_prompt": "",
        "skill_index": "",
        "conversation": [],
        "tool_outputs": [],
        "references": [],
    }

    system_names = ("system_prompt.txt", "SYSTEM.md", "system.md")
    for name in system_names:
        path = os.path.join(session_dir, name)
        if os.path.isfile(path):
            artifacts["system_prompt"] = read_text(path)
            break

    skill_names = ("skill_index.txt", "skills.txt", "SKILLS.md")
    for name in skill_names:
        path = os.path.join(session_dir, name)
        if os.path.isfile(path):
            artifacts["skill_index"] = read_text(path)
            break

    conversation_path = os.path.join(session_dir, "conversation.jsonl")
    if os.path.isfile(conversation_path):
        with open(
            conversation_path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    artifacts["conversation"].append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    tool_dir = os.path.join(session_dir, "tool_outputs")
    if os.path.isdir(tool_dir):
        for fname in sorted(os.listdir(tool_dir)):
            path = os.path.join(tool_dir, fname)
            if os.path.isfile(path):
                artifacts["tool_outputs"].append(
                    {
                        "file": fname,
                        "content": read_text(path),
                    }
                )

    ref_dir = os.path.join(session_dir, "references")
    if os.path.isdir(ref_dir):
        for fname in sorted(os.listdir(ref_dir)):
            path = os.path.join(ref_dir, fname)
            if os.path.isfile(path):
                artifacts["references"].append(
                    {
                        "file": fname,
                        "content": read_text(path),
                    }
                )

    return artifacts

def audit(
    artifacts: dict,
    window_size: int,
    chars_per_token: float,
) -> dict:
    """Calculate heuristic context metrics."""
    total = 0
    contributors = []

    system_tokens = estimate_tokens(
        artifacts["system_prompt"],
        chars_per_token,
    )
    if system_tokens:
        contributors.append(
            {"source": "system_prompt", "tokens": system_tokens}
        )
        total += system_tokens

    skill_tokens = estimate_tokens(
        artifacts["skill_index"],
        chars_per_token,
    )
    if skill_tokens:
        contributors.append(
            {"source": "skill_index", "tokens": skill_tokens}
        )
        total += skill_tokens

    conversation_tokens = 0
    conversation_texts = []

    for turn in artifacts["conversation"]:
        text = json.dumps(turn, ensure_ascii=False)
        conversation_texts.append(text)
        conversation_tokens += estimate_tokens(
            text,
            chars_per_token,
        )

    if conversation_tokens:
        contributors.append(
            {
                "source": "conversation",
                "tokens": conversation_tokens,
            }
        )
        total += conversation_tokens

    for output in artifacts["tool_outputs"]:
        tokens = estimate_tokens(
            output["content"],
            chars_per_token,
        )
        total += tokens
        contributors.append(
            {
                "source": f"tool_output:{output['file']}",
                "tokens": tokens,
            }
        )

    for reference in artifacts["references"]:
        tokens = estimate_tokens(
            reference["content"],
            chars_per_token,
        )
        total += tokens
        contributors.append(
            {
                "source": f"reference:{reference['file']}",
                "tokens": tokens,
            }
        )

    constraints = []

    for turn in artifacts["conversation"]:
        if turn.get("role") != "user":
            continue

        content = turn.get("content", "")
        if not isinstance(content, str):
            continue

        for sentence in re.split(r"[.!?]\s+", content):
            sentence = sentence.strip()

            if re.match(
                r"^(must|should|never|always|do not|don't|ensure|"
                r"make sure|require|need|only|avoid)\b",
                sentence,
                re.IGNORECASE,
            ):
                constraints.append(sentence)

    context_text = (
        artifacts["system_prompt"]
        + artifacts["skill_index"]
        + " ".join(conversation_texts)
        + " ".join(
            item["content"]
            for item in artifacts["tool_outputs"]
        )
        + " ".join(
            item["content"]
            for item in artifacts["references"]
        )
    )

    survived = sum(
        1
        for constraint in constraints
        if constraint.lower() in context_text.lower()
    )

    survival_rate = (
        survived / len(constraints)
        if constraints
        else 1.0
    )

    recent_cutoff = 10
    recent_text = " ".join(
        json.dumps(turn, ensure_ascii=False)
        for turn in artifacts["conversation"][-5:]
    )

    recent_words = set(
        re.findall(
            r"\b[a-z]{5,}\b",
            recent_text.lower(),
        )
    )

    stale_tokens = 0

    if len(artifacts["conversation"]) > recent_cutoff:
        older_turns = artifacts["conversation"][:-recent_cutoff]
    else:
        older_turns = []

    for turn in older_turns:
        text = json.dumps(turn, ensure_ascii=False)
        words = set(
            re.findall(
                r"\b[a-z]{5,}\b",
                text.lower(),
            )
        )

        if not (words & recent_words):
            stale_tokens += estimate_tokens(
                text,
                chars_per_token,
            )

    stale_ratio = (
        stale_tokens / conversation_tokens
        if conversation_tokens
        else 0.0
    )

    all_blocks = (
        [artifacts["system_prompt"], artifacts["skill_index"]]
        + conversation_texts
        + [
            item["content"]
            for item in artifacts["tool_outputs"]
        ]
        + [
            item["content"]
            for item in artifacts["references"]
        ]
    )

    ngram_counts = Counter()

    for block in all_blocks:
        words = re.findall(
            r"\b\w+\b",
            block.lower(),
        )

        for index in range(max(0, len(words) - 5)):
            ngram = tuple(words[index:index + 6])
            ngram_counts[ngram] += 1

    total_ngrams = sum(ngram_counts.values())
    duplicated = sum(
        count - 1
        for count in ngram_counts.values()
        if count > 1
    )

    repetition_ratio = (
        duplicated / total_ngrams
        if total_ngrams
        else 0.0
    )

    contributors.sort(
        key=lambda item: item["tokens"],
        reverse=True,
    )

    utilization = total / window_size

    return {
        "estimated_tokens": total,
        "window_size": window_size,
        "chars_per_token": chars_per_token,
        "utilization": round(utilization, 3),
        "instruction_survival_rate": round(
            survival_rate,
            3,
        ),
        "stale_content_ratio": round(
            stale_ratio,
            3,
        ),
        "repetition_ratio": round(
            repetition_ratio,
            3,
        ),
        "constraint_count": len(constraints),
        "constraints_survived": survived,
        "top_contributors": contributors[:20],
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

def compare_reports(old_path: str, new_path: str) -> str:
    """Return a human-readable comparison of two audit reports."""
    with open(old_path, "r", encoding="utf-8") as handle:
        old = json.load(handle)

    with open(new_path, "r", encoding="utf-8") as handle:
        new = json.load(handle)

    lines = [
        "",
        "=== Context Audit Comparison ===",
        "",
    ]

    metrics = (
        "estimated_tokens",
        "utilization",
        "instruction_survival_rate",
        "stale_content_ratio",
        "repetition_ratio",
    )

    for key in metrics:
        old_value = old.get(key, 0)
        new_value = new.get(key, 0)
        delta = new_value - old_value

        if key == "instruction_survival_rate":
            arrow = (
                "↑" if delta > 0
                else "↓" if delta < 0
                else "→"
            )
        else:
            arrow = (
                "↓" if delta < 0
                else "↑" if delta > 0
                else "→"
            )

        lines.append(
            f"  {key}: {old_value} → {new_value}  "
            f"({arrow} {abs(delta):.3f})"
        )

    lines.append("")
    return "\n".join(lines)

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description="Audit context usage using lightweight heuristics."
    )

    parser.add_argument(
        "--session-dir",
        required=True,
        help="Directory containing supported session artifacts.",
    )

    parser.add_argument(
        "--window-size",
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        help=(
            "Context-window size used for utilization estimates. "
            f"Default: {DEFAULT_WINDOW_SIZE}."
        ),
    )

    parser.add_argument(
        "--chars-per-token",
        type=float,
        default=DEFAULT_CHARS_PER_TOKEN,
        help=(
            "Character-to-token estimate. "
            f"Default: {DEFAULT_CHARS_PER_TOKEN}."
        ),
    )

    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Directory for audit reports. "
            f"Default: {DEFAULT_OUTPUT_DIR}."
        ),
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full report as JSON.",
    )

    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare the two most recent reports.",
    )

    return parser

def main() -> None:
    """Run the command-line audit."""
    parser = build_parser()
    args = parser.parse_args()

    if args.window_size <= 0:
        parser.error("--window-size must be greater than zero.")

    if args.chars_per_token <= 0:
        parser.error(
            "--chars-per-token must be greater than zero."
        )

    if not os.path.isdir(args.session_dir):
        parser.error(
            f"Session directory does not exist: {args.session_dir}"
        )

    artifacts = load_session(args.session_dir)

    report = audit(
        artifacts,
        window_size=args.window_size,
        chars_per_token=args.chars_per_token,
    )

    audit_dir = os.path.abspath(
        os.path.expanduser(args.output_dir)
    )
    os.makedirs(audit_dir, exist_ok=True)

    stamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d-%H%M%S-%f")

    report_path = os.path.join(
        audit_dir,
        f"audit-{stamp}.json",
    )

    with open(
        report_path,
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            report,
            handle,
            indent=2,
            ensure_ascii=False,
        )

    if args.json:
        print(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(
            f"\n=== Context Audit: {args.session_dir} ===\n"
        )
        print(
            f"  Estimated tokens:       "
            f"{report['estimated_tokens']:,}"
        )
        print(
            f"  Window size:            "
            f"{report['window_size']:,}"
        )
        print(
            f"  Window utilization:     "
            f"{report['utilization']:.1%}"
        )
        print(
            f"  Instruction survival:   "
            f"{report['instruction_survival_rate']:.1%}"
        )
        print(
            f"  Stale content ratio:    "
            f"{report['stale_content_ratio']:.1%}"
        )
        print(
            f"  Repetition ratio:       "
            f"{report['repetition_ratio']:.1%}"
        )

        print("\n  Top contributors:")

        for contributor in report["top_contributors"][:10]:
            print(
                f"    {contributor['source']}: "
                f"{contributor['tokens']:,} estimated tokens"
            )

        print(
            f"\n  Report saved: {report_path}"
        )

    if args.compare:
        reports = sorted(
            os.path.join(audit_dir, filename)
            for filename in os.listdir(audit_dir)
            if filename.startswith("audit-")
            and filename.endswith(".json")
        )

        if len(reports) >= 2:
            print(
                compare_reports(
                    reports[-2],
                    reports[-1],
                )
            )
        else:
            print(
                "\n  No previous audit to compare against."
            )

if __name__ == "__main__":
    main()