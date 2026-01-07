"""Parser for acceptance criteria from markdown files."""

import re
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class AcceptanceCriteria(BaseModel):
    """Represents a single acceptance criterion."""

    id: str = Field(..., description="AC ID, e.g., 'AC-RUN-001'")
    title: str = Field(..., description="AC title, e.g., 'Run UUID'")
    description: str = Field(..., description="Full text including bullet points")
    section_id: str = Field(..., description="Section ID, e.g., 'A'")
    section_title: str = Field(..., description="Section title, e.g., 'Run Identity and Timing'")
    line_number: int = Field(..., description="Line number in source file where AC heading starts")
    raw_content: str = Field(..., description="Original markdown content for this AC")


class AcceptanceCriteriaSection(BaseModel):
    """Represents a section containing multiple ACs."""

    section_id: str = Field(..., description="Section ID, e.g., 'A'")
    section_title: str = Field(..., description="Section title, e.g., 'Run Identity and Timing'")
    acceptance_criteria: List[AcceptanceCriteria] = Field(default_factory=list)


def parse_markdown_file(file_path: Path) -> List[AcceptanceCriteriaSection]:
    """
    Parse markdown file and extract acceptance criteria sections.
    
    Expected format:
    ## X) Section Title
    ### AC-XXX-### | AC Title
    - Bullet point 1
    - Bullet point 2
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        List of sections, each containing acceptance criteria
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    sections: List[AcceptanceCriteriaSection] = []
    current_section: Optional[AcceptanceCriteriaSection] = None
    current_ac: Optional[AcceptanceCriteria] = None
    current_ac_lines: List[str] = []
    current_ac_start_line = 0
    
    # Patterns
    section_pattern = re.compile(r'^##\s+([A-Z])\)\s+(.+)$')
    ac_pattern = re.compile(r'^###\s+(AC-[A-Z]+-\d+)\s*\|\s*(.+)$')
    
    for line_num, line in enumerate(lines, start=1):
        line_stripped = line.rstrip()
        
        # Check for section heading
        section_match = section_pattern.match(line_stripped)
        if section_match:
            # Save previous AC if exists
            if current_ac and current_ac_lines:
                current_ac.description = ''.join(current_ac_lines).strip()
                current_ac.raw_content = ''.join(lines[current_ac_start_line - 1:line_num - 1])
                if current_section:
                    current_section.acceptance_criteria.append(current_ac)
            
            # Start new section
            section_id = section_match.group(1)
            section_title = section_match.group(2).strip()
            current_section = AcceptanceCriteriaSection(
                section_id=section_id,
                section_title=section_title,
                acceptance_criteria=[]
            )
            sections.append(current_section)
            current_ac = None
            current_ac_lines = []
            continue
        
        # Check for AC heading
        ac_match = ac_pattern.match(line_stripped)
        if ac_match:
            # Save previous AC if exists
            if current_ac and current_ac_lines:
                current_ac.description = ''.join(current_ac_lines).strip()
                current_ac.raw_content = ''.join(lines[current_ac_start_line - 1:line_num - 1])
                if current_section:
                    current_section.acceptance_criteria.append(current_ac)
            
            # Start new AC
            ac_id = ac_match.group(1)
            ac_title = ac_match.group(2).strip()
            current_ac = AcceptanceCriteria(
                id=ac_id,
                title=ac_title,
                description="",
                section_id=current_section.section_id if current_section else "",
                section_title=current_section.section_title if current_section else "",
                line_number=line_num,
                raw_content=""
            )
            current_ac_start_line = line_num
            current_ac_lines = []
            continue
        
        # Collect content for current AC
        if current_ac:
            current_ac_lines.append(line)
    
    # Save last AC if exists
    if current_ac and current_ac_lines:
        current_ac.description = ''.join(current_ac_lines).strip()
        current_ac.raw_content = ''.join(lines[current_ac_start_line - 1:])
        if current_section:
            current_section.acceptance_criteria.append(current_ac)
    
    return sections


def generate_preview_table(
    sections: List[AcceptanceCriteriaSection],
    project_key: str = "PROJ"
) -> str:
    """
    Generate a markdown table preview showing what Jira issues would be created.
    
    Hierarchy:
    - Epic: Section (e.g., "A) Run Identity and Timing")
    - Story: Individual AC (e.g., "AC-RUN-001 | Run UUID")
    
    Args:
        sections: Parsed acceptance criteria sections
        project_key: Jira project key (for preview purposes)
        
    Returns:
        Markdown string with preview table
    """
    lines = [
        "# Acceptance Criteria to Jira Issues Preview",
        "",
        f"**Project:** {project_key}",
        "",
        "This table shows what Jira issues would be created from the acceptance criteria.",
        "",
        "## Hierarchy",
        "",
        "- **Epic**: Section (e.g., A) Run Identity and Timing)",
        "- **Story**: Individual Acceptance Criterion (e.g., AC-RUN-001 | Run UUID)",
        "",
        "---",
        "",
    ]
    
    for section in sections:
        # Epic row
        epic_summary = f"{section.section_id}) {section.section_title}"
        lines.append(f"## Epic: {epic_summary}")
        lines.append("")
        lines.append("| Issue Type | Summary | Description Preview |")
        lines.append("|------------|---------|---------------------|")
        
        # Truncate description for preview
        epic_desc_preview = f"Section: {section.section_title}. Contains {len(section.acceptance_criteria)} acceptance criteria."
        if len(epic_desc_preview) > 60:
            epic_desc_preview = epic_desc_preview[:57] + "..."
        
        lines.append(f"| Epic | {epic_summary} | {epic_desc_preview} |")
        lines.append("")
        
        # Stories (ACs) table
        if section.acceptance_criteria:
            lines.append("### Stories (Acceptance Criteria)")
            lines.append("")
            lines.append("| Issue Type | AC ID | Summary | Description Preview |")
            lines.append("|-----------|-------|---------|---------------------|")
            
            for ac in section.acceptance_criteria:
                story_summary = f"{ac.id}: {ac.title}"
                desc_preview = ac.description.split('\n')[0] if ac.description else ""
                if len(desc_preview) > 60:
                    desc_preview = desc_preview[:57] + "..."
                if not desc_preview:
                    desc_preview = "(no description)"
                
                lines.append(f"| Story | {ac.id} | {story_summary} | {desc_preview} |")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    # Summary
    total_epics = len(sections)
    total_stories = sum(len(section.acceptance_criteria) for section in sections)
    
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Epics (Sections):** {total_epics}")
    lines.append(f"- **Total Stories (ACs):** {total_stories}")
    lines.append("")
    
    return '\n'.join(lines)


def parse_and_preview(file_path: Path, project_key: str = "PROJ") -> str:
    """
    Parse acceptance criteria file and generate preview table.
    
    This is the default behavior - parse and show what would be created.
    
    Args:
        file_path: Path to markdown file with acceptance criteria
        project_key: Jira project key (for preview purposes)
        
    Returns:
        Markdown string with preview table
    """
    sections = parse_markdown_file(file_path)
    return generate_preview_table(sections, project_key)


