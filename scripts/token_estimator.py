#!/usr/bin/env python3
"""Estimate token count for text, files, or directories."""

import argparse
import os

CHARS_PER_TOKEN = 3.8


def estimate(text: str) -> int:
    return max(1, int(len(text) / CHARS_PER_TOKEN))


def estimate_file(path: str) -> int:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return estimate(f.read())


def main():
    parser = argparse.ArgumentParser(description="Estimate token counts.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text")
    group.add_argument("--file")
    group.add_argument("--dir")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    if args.text:
        print(f"{estimate(args.text):,} tokens")
    elif args.file:
        print(f"{estimate_file(args.file):,} tokens  ({args.file})")
    elif args.dir:
        results = []
        for root, dirs, files in os.walk(args.dir):
            if not args.recursive:
                dirs.clear()
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    results.append((estimate_file(fpath), fpath))
                except Exception:
                    pass
        results.sort(reverse=True)
        total = sum(t for t, _ in results)
        print(f"\nTotal: {total:,} tokens across {len(results)} files\n")
        print(f"{'Tokens':>10}  File")
        print(f"{'-' * 10}  {'-' * 50}")
        for tokens, fpath in results[: args.top]:
            rel = os.path.relpath(fpath, args.dir)
            print(f"{tokens:>10,}  {rel}")


if __name__ == "__main__":
    main()