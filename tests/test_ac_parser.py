"""Tests for acceptance criteria parser."""

import pytest
from pathlib import Path

from jira_wrapper.ac_parser import (
    AcceptanceCriteria,
    AcceptanceCriteriaSection,
    parse_markdown_file,
    generate_preview_table,
    parse_and_preview,
)


@pytest.fixture
def test_ac_file():
    """Path to test acceptance criteria file."""
    return Path(__file__).parent / "orchestrator_acceptance_criteria.md"


def test_parse_markdown_file_exists(test_ac_file):
    """Test that parser raises error for non-existent file."""
    with pytest.raises(FileNotFoundError):
        parse_markdown_file(Path("nonexistent.md"))


def test_parse_markdown_file_structure(test_ac_file):
    """Test that parser extracts correct structure."""
    sections = parse_markdown_file(test_ac_file)
    
    assert len(sections) == 4, "Should have 4 sections (A, B, C, D)"
    
    # Check first section
    section_a = sections[0]
    assert section_a.section_id == "A"
    assert section_a.section_title == "Run Identity and Timing"
    assert len(section_a.acceptance_criteria) == 3
    
    # Check first AC
    ac_001 = section_a.acceptance_criteria[0]
    assert ac_001.id == "AC-RUN-001"
    assert ac_001.title == "Run UUID"
    assert "RUN_UUID" in ac_001.description
    assert ac_001.section_id == "A"
    assert ac_001.line_number > 0


def test_parse_markdown_file_all_sections(test_ac_file):
    """Test that all sections are parsed correctly."""
    sections = parse_markdown_file(test_ac_file)
    
    section_ids = [s.section_id for s in sections]
    assert section_ids == ["A", "B", "C", "D"]
    
    # Check section B
    section_b = sections[1]
    assert section_b.section_id == "B"
    assert section_b.section_title == "Triggers and Entrypoints"
    assert len(section_b.acceptance_criteria) == 3
    
    # Check AC-TRIG-001
    ac_trig_001 = section_b.acceptance_criteria[0]
    assert ac_trig_001.id == "AC-TRIG-001"
    assert ac_trig_001.title == "Git Post-Commit Trigger"
    assert "post-commit git hook" in ac_trig_001.description


def test_generate_preview_table(test_ac_file):
    """Test preview table generation."""
    sections = parse_markdown_file(test_ac_file)
    preview = generate_preview_table(sections, project_key="TEST")
    
    assert "TEST" in preview
    assert "Epic" in preview
    assert "Story" in preview
    assert "AC-RUN-001" in preview
    assert "A) Run Identity and Timing" in preview
    assert "Total Epics" in preview
    assert "Total Stories" in preview


def test_parse_and_preview(test_ac_file):
    """Test combined parse and preview function."""
    preview = parse_and_preview(test_ac_file, project_key="TEST")
    
    assert isinstance(preview, str)
    assert len(preview) > 0
    assert "TEST" in preview
    assert "AC-RUN-001" in preview


def test_ac_description_contains_bullets(test_ac_file):
    """Test that AC descriptions include bullet points."""
    sections = parse_markdown_file(test_ac_file)
    
    ac_001 = sections[0].acceptance_criteria[0]
    assert "-" in ac_001.description or "*" in ac_001.description
    assert "RUN_UUID" in ac_001.description


def test_section_c_ac_count(test_ac_file):
    """Test that section C has correct number of ACs."""
    sections = parse_markdown_file(test_ac_file)
    section_c = sections[2]
    
    assert section_c.section_id == "C"
    assert section_c.section_title == "Target Selection"
    assert len(section_c.acceptance_criteria) == 3
    
    ac_ids = [ac.id for ac in section_c.acceptance_criteria]
    assert "AC-TARGET-001" in ac_ids
    assert "AC-TARGET-002" in ac_ids
    assert "AC-TARGET-003" in ac_ids


