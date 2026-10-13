import pytest
from retrieval.chunking import parse_markdown_sections


def test_markdown_structure_parsing():
    # Headers should start exactly at the beginning of the line
    sample_md = """# FedEx Operations
## Lost in Transit
This is a standard procedure text regarding lost items.
### Sub-Section Level
Additional carrier rules here."""

    sections = parse_markdown_sections(sample_md)
    
    assert len(sections) >= 1
    assert sections[0]["headers"][1] == "FedEx Operations"
    assert sections[0]["headers"][2] == "Lost in Transit"
    assert "This is a standard procedure" in sections[0]["text"]
