#!/usr/bin/env python3
"""
Estimate relative token counts for text, files, or directories.

This is a character-based approximation. It is useful for relative
comparisons and rough budgeting, not exact tokenizer accounting.

Usage:
    python token_estimator.py --text "hello"
    python token_estimator.py --file path/to/file
    python token_estimator.py --dir . --recursive --top 20
"""

import argparse
import os

DEFAULT_CHARS_PER_TOKEN = 3.8

def estimate(
    text: str,
    chars_per_token: float = DEFAULT_CHARS_PER_TOKEN,
) -> int:
    """Return a character-based token estimate."""
    if not text:
        return 0

    return max(
        1,
        int(len(text) / chars_per_token),
    )

def estimate_file(
    path: str,
    chars_per_token: float,
) -> int:
    """Estimate tokens in a UTF-8 text file."""
    with open(
        path,
        "r",
        encoding="utf-8",
        errors="replace",
    ) as handle:
        return estimate(
            handle.read(),
            chars_per_token,
        )

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Estimate token counts using a configurable "
            "character-based heuristic."
        )
    )

    group = parser.add_mutually_exclusive_group(
        required=True
    )

    group.add_argument(
        "--text",
        help="Text to estimate.",
    )

    group.add_argument(
        "--file",
        help="File to estimate.",
    )

    group.add_argument(
        "--dir",
        help="Directory to scan.",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan subdirectories.",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of largest files to display.",
    )

    parser.add_argument(
        "--chars-per-token",
        type=float,
        default=DEFAULT_CHARS_PER_TOKEN,
        help=(
            "Character-to-token approximation. "
            f"Default: {DEFAULT_CHARS_PER_TOKEN}."
        ),
    )

    return parser

def main() -> None:
    """Run the token estimator."""
    parser = build_parser()
    args = parser.parse_args()

    if args.chars_per_token <= 0:
        parser.error(
            "--chars-per-token must be greater than zero."
        )

    if args.top < 1:
        parser.error("--top must be at least 1.")

    if args.text is not None:
        print(
            f"{estimate(args.text, args.chars_per_token):,} "
            "estimated tokens"
        )
        return

    if args.file is not None:
        if not os.path.isfile(args.file):
            parser.error(
                f"File does not exist: {args.file}"
            )

        tokens = estimate_file(
            args.file,
            args.chars_per_token,
        )

        print(
            f"{tokens:,} estimated tokens  ({args.file})"
        )
        return

    results = []

    if not os.path.isdir(args.dir):
        parser.error(
            f"Directory does not exist: {args.dir}"
        )

    for root, dirs, files in os.walk(args.dir):
        if not args.recursive:
            dirs.clear()

        for filename in files:
            path = os.path.join(
                root,
                filename,
            )

            try:
                tokens = estimate_file(
                    path,
                    args.chars_per_token,
                )
            except (
                OSError,
                UnicodeError,
            ):
                continue

            results.append(
                (tokens, path)
            )

    results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    total = sum(
        tokens
        for tokens, _ in results
    )

    print(
        f"\nTotal: {total:,} estimated tokens "
        f"across {len(results)} files\n"
    )

    print(
        f"{'Estimated tokens':>18}  File"
    )
    print(
        f"{'-' * 18}  {'-' * 50}"
    )

    for tokens, path in results[:args.top]:
        relative = os.path.relpath(
            path,
            args.dir,
        )

        print(
            f"{tokens:>18,}  {relative}"
        )

if __name__ == "__main__":
    main()