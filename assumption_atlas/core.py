from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

ASSUMPTION_KEYWORDS = (
    "assume",
    "assumption",
    "believe",
    "expects",
    "expect",
    "likely",
    "probably",
    "should",
    "must",
    "need",
    "will",
    "users want",
    "users need",
    "we think",
    "we assume",
    "likely to",
    "probably will",
)

CONTRAST_MARKERS = (
    "however",
    "but",
    "yet",
    "although",
    "despite",
    "while",
    "whereas",
    "in contrast",
    "on the other hand",
    "tradeoff",
    "tension",
    "conflict",
    "contradicts",
    "contradiction",
)

OPPOSING_TOKENS = (
    ("speed", "slowness"),
    ("simple", "complex"),
    ("fast", "slow"),
    ("cheap", "expensive"),
    ("more", "less"),
    ("growth", "decline"),
    ("scale", "limit"),
    ("value", "cost"),
    ("easy", "hard"),
    ("clear", "confusing"),
)

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "is", "are", "we", "our", "you", "your",
    "for", "with", "from", "into", "this", "that", "these", "those", "it", "its", "as",
    "to", "of", "in", "on", "be", "by", "at", "will", "should", "must", "can", "could",
    "too", "very", "more", "less", "not", "have", "has", "had", "about", "after", "before",
    "through", "over", "under", "between", "because", "while", "when", "where", "there",
}


@dataclass
class Finding:
    title: str
    statement: str
    source: str
    category: str
    score: float
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    assumptions: list[Finding] = field(default_factory=list)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    opportunities: list[dict[str, Any]] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "assumptions": [item.to_dict() for item in self.assumptions],
            "contradictions": self.contradictions,
            "opportunities": self.opportunities,
            "sources": self.sources,
        }


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _split_sentences(text: str) -> list[str]:
    cleaned = _normalize_whitespace(text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\(\[])", cleaned)
    sentences = [part.strip() for part in parts if part.strip()]
    return sentences


def infer_category(sentence: str) -> str:
    lower = sentence.lower()
    if any(token in lower for token in ("user", "customer", "buyer", "segment", "persona")):
        return "user-need"
    if any(token in lower for token in ("growth", "retention", "activation", "adoption", "acquisition", "revenue")):
        return "growth"
    if any(token in lower for token in ("cost", "budget", "time", "team", "resource", "capacity")):
        return "resource"
    if any(token in lower for token in ("speed", "launch", "ship", "delivery", "timeline")):
        return "execution"
    if any(token in lower for token in ("risk", "uncertainty", "unknown", "assumption", "hypothesis")):
        return "risk"
    return "strategy"


def _sentence_score(sentence: str) -> float:
    lower = sentence.lower()
    score = 0.0
    if any(keyword in lower for keyword in ("assume", "assumption")):
        score += 4.0
    if any(keyword in lower for keyword in ("should", "must", "need", "will", "expect", "likely", "probably")):
        score += 3.0
    if any(keyword in lower for keyword in ("users want", "users need", "we think", "we believe")):
        score += 2.0
    if any(keyword in lower for keyword in ("if", "when", "until")):
        score += 1.0
    if len(sentence.split()) > 8:
        score += 0.5
    return min(score, 10.0)


def extract_assumptions(sentences: Iterable[str], source: str) -> list[Finding]:
    findings: list[Finding] = []
    for sentence in sentences:
        lower = sentence.lower()
        if any(keyword in lower for keyword in ASSUMPTION_KEYWORDS):
            title = sentence[:80].rstrip(".")
            rationale = "This sentence expresses an assumption or a causal claim without direct evidence."
            if "assume" in lower or "assumption" in lower:
                rationale = "Explicit assumption language indicates unproven belief."
            elif "should" in lower or "must" in lower:
                rationale = "The statement treats a requirement as settled without proving it."
            elif "users" in lower and ("want" in lower or "need" in lower):
                rationale = "User preference is inferred rather than validated."
            findings.append(
                Finding(
                    title=title,
                    statement=sentence,
                    source=source,
                    category=infer_category(sentence),
                    score=_sentence_score(sentence),
                    rationale=rationale,
                )
            )
    return findings


def _keyword_signature(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower())
    return {word for word in words if word not in STOP_WORDS}


def sentence_has_opposed_signal(a: str, b: str) -> bool:
    sig_a = _keyword_signature(a)
    sig_b = _keyword_signature(b)
    overlap = sig_a & sig_b
    if not overlap:
        return False
    for left, right in OPPOSING_TOKENS:
        if (left in a.lower() and right in b.lower()) or (right in a.lower() and left in b.lower()):
            return True
    if any(marker in a.lower() for marker in ("faster", "slower", "more", "less", "higher", "lower")) and any(
        marker in b.lower() for marker in ("faster", "slower", "more", "less", "higher", "lower")
    ):
        return True
    return False


def extract_contradictions(sentences: Iterable[str], source: str) -> list[dict[str, Any]]:
    sentence_list = list(sentences)
    contradictions: list[dict[str, Any]] = []
    for index, sentence in enumerate(sentence_list):
        lower = sentence.lower()
        if not any(marker in lower for marker in CONTRAST_MARKERS):
            continue
        nearby = []
        if index > 0:
            nearby.append(sentence_list[index - 1])
        if index + 1 < len(sentence_list):
            nearby.append(sentence_list[index + 1])
        for neighbor in nearby:
            if not neighbor or neighbor == sentence:
                continue
            if sentence_has_opposed_signal(sentence, neighbor):
                contradictions.append(
                    {
                        "title": sentence[:80].rstrip("."),
                        "statement": f"{sentence} // {neighbor}",
                        "source": source,
                        "severity": "high" if any(term in lower for term in ("must", "should", "requires", "but", "however")) else "medium",
                        "rationale": "The plan contains a direct tension or trade-off worth validating."
                    }
                )
    # deduplicate
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in contradictions:
        key = (item["title"], item["statement"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def generate_experiments(assumptions: Iterable[Finding], contradictions: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    experiments: list[dict[str, Any]] = []
    assumption_items = sorted(list(assumptions), key=lambda item: item.score, reverse=True)[:3]
    for assumption in assumption_items:
        experiments.append(
            {
                "title": f"Test assumption: {assumption.title[:60]}",
                "goal": "Validate whether the assumption is supported by evidence.",
                "method": "Run 3-5 interviews or observe usage data that directly tests the claim.",
                "priority": "high" if assumption.score >= 7 else "medium",
            }
        )
    for contradiction in list(contradictions)[:2]:
        experiments.append(
            {
                "title": f"Resolve tension: {contradiction['title'][:60]}",
                "goal": "Reduce uncertainty around the trade-off.",
                "method": "Design a small experiment comparing the two approaches against the same success metric.",
                "priority": "high",
            }
        )
    return experiments


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _iter_supported_files(input_path: str | Path) -> list[Path]:
    root = Path(input_path)
    if root.is_file():
        return [root]
    if not root.exists():
        raise FileNotFoundError(f"Input path does not exist: {root}")
    suffixes = {".md", ".txt", ".rst", ".log", ".json"}
    return sorted(
        [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in suffixes],
        key=lambda p: str(p),
    )


def analyze_text(document_text: str, source: str = "document") -> dict[str, Any]:
    sentences = _split_sentences(document_text)
    assumptions = extract_assumptions(sentences, source)
    contradictions = extract_contradictions(sentences, source)
    opportunities = generate_experiments(assumptions, contradictions)
    return {
        "assumptions": [item.to_dict() for item in assumptions],
        "contradictions": contradictions,
        "opportunities": opportunities,
        "source": source,
    }


def analyze_documents(input_path: str | Path) -> AnalysisResult:
    files = _iter_supported_files(input_path)
    if not files:
        raise ValueError(f"No supported text files were found in: {input_path}")

    assumptions: list[Finding] = []
    contradictions: list[dict[str, Any]] = []
    opportunities: list[dict[str, Any]] = []
    sources: list[str] = []

    for file_path in files:
        text = _read_text_file(file_path)
        if not text.strip():
            continue
        result = analyze_text(text, source=str(file_path))
        assumptions.extend(Finding(**item) for item in result["assumptions"])
        contradictions.extend(result["contradictions"])
        opportunities.extend(result["opportunities"])
        sources.append(str(file_path))

    final = AnalysisResult(
        assumptions=assumptions,
        contradictions=contradictions,
        opportunities=opportunities,
        sources=sources,
    )
    return final


def render_text_report(result: AnalysisResult, limit: int = 5) -> str:
    assumptions = result.assumptions[:limit]
    contradictions = result.contradictions[:limit]
    opportunities = result.opportunities[:limit]

    lines: list[str] = [
        "Assumption Atlas",
        f"Files analyzed: {len(result.sources)}",
        "",
        "Top assumptions:",
    ]

    if not assumptions:
        lines.append("- No explicit assumptions detected.")
    else:
        for index, item in enumerate(assumptions, start=1):
            lines.append(f"{index}. [{item.category}] {item.title} (score={item.score:.1f})")
            lines.append(f"   {item.rationale}")

    lines.extend(["", "Contradictions:"])
    if not contradictions:
        lines.append("- No direct contradictions detected.")
    else:
        for index, item in enumerate(contradictions, start=1):
            lines.append(f"{index}. {item['title']}")
            lines.append(f"   {item['statement']}")

    lines.extend(["", "Opportunity experiments:"])
    if not opportunities:
        lines.append("- No experiments generated.")
    else:
        for index, item in enumerate(opportunities, start=1):
            lines.append(f"{index}. {item['title']} [{item['priority']}]")
            lines.append(f"   Goal: {item['goal']}")
            lines.append(f"   Method: {item['method']}")

    return "\n".join(lines)


if __name__ == "__main__":
    sample = """
    We assume users want speed more than simplicity.
    However, the design says the flow should feel simple and calm.
    We must ship quickly, but the team has limited time and money.
    """
    report = analyze_text(sample, "example.txt")
    print(json.dumps(report, indent=2, ensure_ascii=False))
