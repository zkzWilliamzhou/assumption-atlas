# Assumption Atlas

Assumption Atlas is a focused research and decision-support tool for one core job:

- read strategic, product, and planning documents
- surface hidden assumptions
- detect contradictions, tension, and risk
- rank the opportunities and experiments that can reduce uncertainty fastest

The project is intentionally narrow and opinionated. It does not try to be a generic AI assistant. It is built to help teams answer the questions that matter most in early product and strategy work:

- What are we assuming without proof?
- Where are the contradictions in our plan?
- What decisions are most risky?
- What experiments will reduce uncertainty fastest?

## Why this project exists
Most AI tools summarize or generate. Assumption Atlas is designed to make hidden structure visible.

It is optimized for:
- product briefs
- strategy docs
- user interviews
- launch plans
- roadmap docs
- idea memos
- research notes

## Core function
The function of the project is intentionally fixed:

1. ingest one or more text documents
2. split them into statements
3. extract assumptions and belief statements
4. identify contradictions and trade-offs
5. convert the strongest findings into decision experiments
6. output a concise report

This function is preserved while the implementation is iterated and tightened.

## Skill inspiration
This project is shaped by patterns from public AI skills work such as:

- Anthropic skills
- Matt Pocock skills
- Superpowers-style agent workflows
- structured brainstorming and critique patterns

The repo includes a lightweight skill layer under `skills/` so the workflow remains easy to adapt to Claude Code, Codex, Cursor, and other agent environments.

## Quick start

Install the package locally:

```bash
pip install -e .
```

Analyze a single file:

```bash
assumption-atlas --input docs/brief.md --format text
```

Analyze a directory:

```bash
assumption-atlas --input docs/ --format json
```

## Example output

```text
Assumption Atlas
Files analyzed: 3

Top assumptions:
- We assume users want speed more than simplicity.
- We assume the product can be built with a lean team.
- We assume growth will follow launch friction reduction.

Contradictions:
- The roadmap says we will simplify onboarding, but the implementation plan adds more workflow steps.
- The team wants to launch quickly, while the plan depends on broad user research.

Opportunity experiments:
- Run 5 interviews to validate whether users prefer speed or simplicity.
- Test two onboarding flows against conversion and retention.
- Measure whether complexity is reducing activation more than it improves feature depth.
```

## Repository layout

```text
assumption-atlas/
├── README.md
├── pyproject.toml
├── assumption_atlas/
│   ├── __init__.py
│   ├── core.py
│   └── cli.py
├── tests/
│   └── test_core.py
├── skills/
│   ├── README.md
│   ├── assumption-atlas/SKILL.md
│   ├── contradiction-scan/SKILL.md
│   └── decision-critique/SKILL.md
└── docs/ (user content can go here)
```

## Safety and quality constraints

This project follows a strict review model:

- keep the core function stable
- reduce false confidence
- avoid claiming certainty without evidence
- require experiments instead of pure opinion
- keep report output clear and auditable

## License
MIT
