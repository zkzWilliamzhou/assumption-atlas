from assumption_atlas.core import analyze_text


def test_basic_analysis() -> None:
    text = """
    We assume users want speed more than simplicity.
    However, the roadmap adds complexity and slows the flow.
    We must ship in 30 days, but the team has limited resources.
    """
    result = analyze_text(text, "demo.md")
    assert result["assumptions"], "Expected at least one assumption"
    assert result["contradictions"], "Expected at least one contradiction"
    assert result["opportunities"], "Expected at least one opportunity"


def test_empty_input_is_handled() -> None:
    result = analyze_text("Nothing here to inspect.", "demo.md")
    assert isinstance(result["assumptions"], list)
    assert isinstance(result["contradictions"], list)
    assert isinstance(result["opportunities"], list)
