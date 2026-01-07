# Acceptance Criteria to Jira Pipeline - Implementation Plan

## Overview

This document outlines the implementation plan for a pipeline that:
1. Parses acceptance criteria from markdown files (format: `AC-XXX-### | Title`)
2. Generates Jira Stories (one per section) and Subtasks (one per AC)
3. Creates a tracking report mapping AC IDs to Jira issues
4. Updates markdown files with Jira issue links

## Acceptance Criteria Format

Based on `tests/orchestrator_acceptance_criteria.md`:

```
## A) Section Title

### AC-RUN-001 | Run UUID

- Each execution MUST generate a unique RUN_UUID.
- RUN_UUID MUST be included in:
  - logs
  - persisted records
  - output artifacts (including SARIF).
```

**Format Rules:**
- Main sections: `## X) Section Title` (e.g., `## A) Run Identity and Timing`)
- AC entries: `### AC-XXX-### | Title` (e.g., `### AC-RUN-001 | Run UUID`)
- AC content: Bullet points describing the criteria
- AC ID pattern: `AC-{PREFIX}-{NUMBER}` (e.g., `AC-RUN-001`, `AC-TRIG-002`)

## Implementation Plan

### Phase 1: Acceptance Criteria Parser

#### 1.1 Create `jira_wrapper/ac_parser.py`

**Models:**
```python
class AcceptanceCriteria(BaseModel):
    """Represents a single acceptance criterion."""
    id: str                    # e.g., "AC-RUN-001"
    title: str                 # e.g., "Run UUID"
    description: str           # Full text including bullet points
    section_id: str            # e.g., "A"
    section_title: str         # e.g., "Run Identity and Timing"
    line_number: int           # Line number in source file
    raw_content: str           # Original markdown content

class AcceptanceCriteriaSection(BaseModel):
    """Represents a section containing multiple ACs."""
    section_id: str            # e.g., "A"
    section_title: str        # e.g., "Run Identity and Timing"
    acceptance_criteria: List[AcceptanceCriteria]
```

**Parser Functions:**
- `parse_markdown_file(file_path: Path) -> List[AcceptanceCriteriaSection]`
  - Parse markdown file
  - Extract sections (pattern: `## X) Title`)
  - Extract ACs (pattern: `### AC-XXX-### | Title`)
  - Extract AC content (bullet points until next AC or section)
  - Return structured data

**Example Output:**
```python
[
    AcceptanceCriteriaSection(
        section_id="A",
        section_title="Run Identity and Timing",
        acceptance_criteria=[
            AcceptanceCriteria(
                id="AC-RUN-001",
                title="Run UUID",
                description="- Each execution MUST generate...",
                section_id="A",
                section_title="Run Identity and Timing",
                line_number=9,
                raw_content="### AC-RUN-001 | Run UUID\n\n- Each execution..."
            ),
            # ... more ACs
        ]
    ),
    # ... more sections
]
```

#### 1.2 Tests

- Test parsing of valid markdown file
- Test extraction of sections
- Test extraction of AC IDs and titles
- Test extraction of AC descriptions
- Test handling of edge cases (missing sections, malformed ACs)

---

### Phase 2: Jira Issue Generator

#### 2.1 Create `jira_wrapper/ac_to_jira.py`

**Models:**
```python
class ACToJiraMapping(BaseModel):
    """Maps an acceptance criterion to a Jira issue."""
    ac_id: str
    jira_issue_key: str
    jira_issue_status: str
    issue_type: str            # "Story" or "Sub-task"
    parent_issue_key: Optional[str]  # For subtasks, the parent Story key
    created_at: str
    url: str

class JiraGenerationResult(BaseModel):
    """Result of generating Jira issues from ACs."""
    mappings: List[ACToJiraMapping]
    stories_created: int
    subtasks_created: int
    skipped: int               # Already existing issues
```

**Generator Functions:**
- `generate_jira_issues(
    jira_wrapper: JiraWrapper,
    sections: List[AcceptanceCriteriaSection],
    project_key: str,
    mappings_file: Optional[Path] = None
) -> JiraGenerationResult`
  
  **Logic:**
  1. Load existing mappings from file (if exists) for idempotency
  2. For each section:
     - Check if Story already exists (by section ID in label or custom field)
     - If not, create Story:
       - Summary: `{Section ID}) {Section Title}`
       - Description: Section overview + list of ACs
       - Labels: `["acceptance-criteria", f"section-{section_id}"]`
       - Issue Type: `Story`
     - For each AC in section:
       - Check if Sub-task already exists (by AC ID)
       - If not, create Sub-task:
         - Summary: `{AC ID}: {AC Title}`
         - Description: AC description
         - Labels: `["acceptance-criteria", f"ac-{ac_id.lower()}"]`
         - Issue Type: `Sub-task`
         - Parent: Story key
  3. Save mappings to file (JSON)
  4. Return result

**Idempotency Strategy:**
- Store mappings in JSON file: `{project_key}_ac_mappings.json`
- Format:
  ```json
  {
    "AC-RUN-001": {
      "jira_issue_key": "PROJ-123",
      "jira_issue_status": "To Do",
      "issue_type": "Sub-task",
      "parent_issue_key": "PROJ-100",
      "created_at": "2025-01-16T10:00:00Z",
      "url": "https://..."
    },
    ...
  }
  ```
- Before creating issue, check if AC ID exists in mappings
- If exists, skip creation and fetch current status from Jira

#### 2.2 Tests

- Test Story creation
- Test Sub-task creation with parent
- Test idempotency (skip existing)
- Test mapping file persistence
- Test error handling

---

### Phase 3: Report Generator

#### 3.1 Create `jira_wrapper/report_generator.py`

**Functions:**
- `generate_markdown_report(
    mappings: List[ACToJiraMapping],
    output_path: Path,
    title: str = "Acceptance Criteria to Jira Mapping"
) -> None`
  
  **Output Format:**
  ```markdown
  # Acceptance Criteria to Jira Mapping
  
  | Acceptance Criteria ID | Jira Issue Key | Jira Issue Status | Summary |
  |----------------------|----------------|-------------------|---------|
  | AC-RUN-001 | [PROJ-123](url) | To Do | AC-RUN-001: Run UUID |
  | AC-RUN-002 | [PROJ-124](url) | In Progress | AC-RUN-002: Run Timestamps |
  ...
  ```
  
  - Sort by AC ID
  - Include links to Jira issues
  - Group by section (optional, can add later)

- `refresh_report_status(
    jira_wrapper: JiraWrapper,
    mappings_file: Path,
    output_path: Path
) -> None`
  
  - Load mappings from file
  - Fetch current status from Jira for each issue
  - Update mappings
  - Regenerate report

#### 3.2 Tests

- Test markdown table generation
- Test report refresh
- Test formatting

---

### Phase 4: Markdown Updater

#### 4.1 Create `jira_wrapper/markdown_updater.py`

**Functions:**
- `update_markdown_with_jira_links(
    input_path: Path,
    mappings: Dict[str, ACToJiraMapping],
    output_path: Path,
    dry_run: bool = False
) -> UpdateResult`
  
  **Update Strategy:**
  
  1. **Update AC Headings:**
     - Find: `### AC-RUN-001 | Run UUID`
     - Update to: `### AC-RUN-001 | Run UUID [[PROJ-123]]`
     - Or: `### AC-RUN-001 | Run UUID [PROJ-123](url)`
  
  2. **Update Section Headings:**
     - Find: `## A) Run Identity and Timing`
     - Update to: `## A) Run Identity and Timing [[PROJ-100]]`
     - Or: `## A) Run Identity and Timing [PROJ-100](url)`
  
  3. **Update Task Lists (if any):**
     - Find: `- [ ] AC-RUN-001`
     - Update to: `- [ ] AC-RUN-001 [[PROJ-123]]`
  
  **Preservation Rules:**
  - Only add links if they don't already exist
  - Preserve all existing formatting
  - Preserve whitespace
  - Don't modify content, only add links

**Link Format Options:**
- Jira link format: `[[PROJ-123]]` (Jira will auto-link)
- Markdown link: `[PROJ-123](url)`
- Start with Jira format, can add markdown later

#### 4.2 Tests

- Test heading updates
- Test task list updates
- Test preservation of existing formatting
- Test dry-run mode
- Test idempotency (don't add duplicate links)

---

### Phase 5: CLI Integration

#### 5.1 Create `scripts/ac_to_jira_pipeline.py`

**CLI Commands:**

```bash
# Full pipeline: Parse → Generate → Report → Update
jira-wrapper ac-pipeline \
  --input tests/orchestrator_acceptance_criteria.md \
  --project PROJ \
  --output-dir ./reports \
  --update-markdown \
  --dry-run

# Individual steps
jira-wrapper ac-parse \
  --input tests/orchestrator_acceptance_criteria.md \
  --output parsed_ac.json

jira-wrapper ac-generate \
  --input parsed_ac.json \
  --project PROJ \
  --mappings-file mappings.json

jira-wrapper ac-report \
  --mappings mappings.json \
  --output report.md

jira-wrapper ac-update-markdown \
  --input tests/orchestrator_acceptance_criteria.md \
  --mappings mappings.json \
  --output updated.md \
  --dry-run
```

**Arguments:**
- `--input`: Input markdown file
- `--project`: Jira project key
- `--output-dir`: Directory for reports and mappings
- `--mappings-file`: Path to mappings file (for idempotency)
- `--update-markdown`: Whether to update source markdown
- `--dry-run`: Don't make changes, just show what would happen
- `--refresh`: Refresh report status from Jira

#### 5.2 Integration with `pyproject.toml`

Add CLI entry point:
```toml
[project.scripts]
jira-wrapper = "jira_wrapper.cli:main"
```

---

## File Structure

```
jira-wrapper/
├── jira_wrapper/
│   ├── ac_parser.py              # NEW: Parse ACs from markdown
│   ├── ac_to_jira.py             # NEW: Generate Jira issues
│   ├── report_generator.py       # NEW: Generate tracking reports
│   ├── markdown_updater.py       # NEW: Update markdown with links
│   ├── cli.py                    # NEW: CLI interface
│   ├── client.py                 # Existing
│   ├── models.py                 # Existing (may extend)
│   └── exceptions.py             # Existing
├── scripts/
│   └── ac_to_jira_pipeline.py    # NEW: Main pipeline script
├── tests/
│   ├── test_ac_parser.py         # NEW
│   ├── test_ac_to_jira.py        # NEW
│   ├── test_report_generator.py  # NEW
│   ├── test_markdown_updater.py  # NEW
│   └── orchestrator_acceptance_criteria.md  # Existing test data
└── reports/                      # NEW: Generated reports
    ├── PROJ_ac_mappings.json
    └── PROJ_ac_report.md
```

---

## Data Flow

```
1. Input: orchestrator_acceptance_criteria.md
   ↓
2. Parser: Extract sections and ACs
   ↓
3. Generator: Create Jira issues (Stories + Subtasks)
   - Check mappings.json for existing issues
   - Create missing issues
   - Save mappings.json
   ↓
4. Report Generator: Create markdown table
   - Load mappings.json
   - Generate report.md
   ↓
5. Markdown Updater: Add Jira links
   - Load mappings.json
   - Update headings and task lists
   - Write updated markdown
```

---

## Example Output

### Mappings File (`PROJ_ac_mappings.json`)
```json
{
  "AC-RUN-001": {
    "jira_issue_key": "PROJ-123",
    "jira_issue_status": "To Do",
    "issue_type": "Sub-task",
    "parent_issue_key": "PROJ-100",
    "created_at": "2025-01-16T10:00:00Z",
    "url": "https://your-domain.atlassian.net/browse/PROJ-123"
  },
  "AC-RUN-002": {
    "jira_issue_key": "PROJ-124",
    "jira_issue_status": "In Progress",
    "issue_type": "Sub-task",
    "parent_issue_key": "PROJ-100",
    "created_at": "2025-01-16T10:01:00Z",
    "url": "https://your-domain.atlassian.net/browse/PROJ-124"
  },
  "section-A": {
    "jira_issue_key": "PROJ-100",
    "jira_issue_status": "To Do",
    "issue_type": "Story",
    "parent_issue_key": null,
    "created_at": "2025-01-16T10:00:00Z",
    "url": "https://your-domain.atlassian.net/browse/PROJ-100"
  }
}
```

### Report (`PROJ_ac_report.md`)
```markdown
# Acceptance Criteria to Jira Mapping

Generated: 2025-01-16 10:05:00

## Section A) Run Identity and Timing

| Acceptance Criteria ID | Jira Issue Key | Jira Issue Status | Summary |
|----------------------|----------------|-------------------|---------|
| AC-RUN-001 | [PROJ-123](https://...) | To Do | AC-RUN-001: Run UUID |
| AC-RUN-002 | [PROJ-124](https://...) | In Progress | AC-RUN-002: Run Timestamps |
| AC-RUN-003 | [PROJ-125](https://...) | To Do | AC-RUN-003: Repeatability |

**Parent Story:** [PROJ-100](https://...) - A) Run Identity and Timing

## Section B) Triggers and Entrypoints

...
```

### Updated Markdown
```markdown
## A) Run Identity and Timing [[PROJ-100]]

### AC-RUN-001 | Run UUID [[PROJ-123]]

- Each execution MUST generate a unique RUN_UUID.
...
```

---

## Implementation Order

1. **Phase 1: AC Parser** - Parse acceptance criteria from markdown
2. **Phase 2: Jira Generator** - Create issues from ACs (with idempotency)
3. **Phase 3: Report Generator** - Generate tracking tables
4. **Phase 4: Markdown Updater** - Update source files with links
5. **Phase 5: CLI Integration** - Combine into pipeline

---

## Testing Strategy

- Unit tests for each component
- Integration tests with mock Jira
- End-to-end test with test markdown file
- Test idempotency (multiple runs)
- Test error handling (missing ACs, Jira errors, etc.)

---

## Future Enhancements

- Support multiple AC formats
- Confluence report generation
- Additional report columns (priority, assignee, dates)
- Custom field mapping
- Issue linking (blocks, relates to)
- Status synchronization

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-16  
**Status:** Ready for Implementation

