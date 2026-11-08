from __future__ import annotations

import argparse
import json
from pathlib import Path

from assumption_atlas.core import AnalysisResult, analyze_documents, render_text_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze documents for hidden assumptions, contradictions, and experiment opportunities.")
    parser.add_argument("--input", required=True, help="Path to a file or directory containing Markdown/TXT documents.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of findings to print.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        result = analyze_documents(args.input)
        if args.format == "json":
            output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        else:
            output = render_text_report(result, limit=args.limit)
        print(output)
        return 0
    except Exception as exc:  # pragma: no cover - CLI safety net
        print(f"Error: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
