# Skills and workflow notes

This repository intentionally includes a lightweight skill layer inspired by Anthropic, Matt Pocock, Superpowers, and other structured agent workflow patterns. The point is not to copy a framework verbatim, but to make the workflow explicit and reusable.

## Included skills

- `assumption-atlas/` — extracts assumptions and tensions from documents
- `contradiction-scan/` — looks for incompatible or conflicting statements
- `decision-critique/` — evaluates whether a decision has real evidence behind it

## Design pattern

Each skill follows the same format:

- objective
- inputs
- steps
- expected output
- review criteria

This keeps the project easy to adapt to Claude Code, Codex, Cursor, or other agent environments without adding unnecessary complexity.
