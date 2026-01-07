# Jira Integration - Generic Module Implementation Plan

## Overview

This document outlines the plan for implementing a **generic, reusable Jira integration module** that can be used in any project, not just the orchestrator. This module will be implemented first to provide immediate value and can be used to create Jira issues for tracking this project's work.

## Why Implement Jira Integration First?

### Benefits

1. **Immediate Value**: Can start using it right away to track orchestrator implementation work
2. **Generic & Reusable**: Not tied to orchestrator-specific logic, usable in any Python project
3. **Dogfooding**: Using your own tool is the best way to test and improve it
4. **Early Feedback**: Discover API design issues, edge cases, and improvements early
5. **Standalone Feature**: Doesn't depend on other orchestrator components
6. **Real-World Validation**: Creating real Jira issues validates the design with actual use

### Use Cases

1. **This Project**: Create Jira issues for orchestrator implementation tasks
2. **Orchestrator Integration**: Later integrate with orchestrator to create issues for findings
3. **Other Projects**: Reusable in any Python project that needs Jira integration
4. **CI/CD Pipelines**: Can be used in automation scripts

---

## Module Structure

### Option 1: Standalone Package (Recommended)

Create a separate, installable package that can be used anywhere:

```
jira-client/                    # New standalone package
├── jira_client/
│   ├── __init__.py
│   ├── client.py              # Main JiraClient class
│   ├── models.py              # Pydantic models for issues, etc.
│   ├── exceptions.py           # Custom exceptions
│   ├── templates.py            # Issue templates/formatters
│   └── utils.py                # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_models.py
│   └── conftest.py
├── pyproject.toml
├── README.md
└── .env.example
```

**Pros:**
- Completely independent
- Can be published to PyPI
- Easy to use in other projects
- Clear separation of concerns

**Cons:**
- More setup overhead
- Need to manage versioning separately

### Option 2: Shared Utilities Module (Alternative)

Create a shared utilities module within the current project:

```
gcrs_project/
├── shared/                     # New shared utilities
│   ├── __init__.py
│   ├── jira/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── models.py
│   │   ├── exceptions.py
│   │   └── templates.py
│   └── ... (other shared utilities)
├── gcrs/
├── orchestrator/
└── ...
```

**Pros:**
- Simpler structure
- No separate package management
- Easy to refactor later

**Cons:**
- Less portable
- Tied to this project structure

### Option 3: Orchestrator Submodule (Not Recommended)

Put it in orchestrator but make it generic:

```
orchestrator/
├── integrations/
│   ├── __init__.py
│   ├── jira/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── ...
```

**Pros:**
- Simple location

**Cons:**
- Not truly generic (tied to orchestrator)
- Harder to reuse elsewhere

---

## Recommendation: Option 1 (Standalone Package)

**Rationale:**
- Maximum reusability
- Can be published and shared
- Clear boundaries
- Easy to test independently
- Can be used in this project via `pip install -e ./jira-client`

---

## Implementation Plan

### Phase 1: Core Jira Client (MVP)

#### 1.1 Project Setup

**Tasks:**
- [ ] Create `jira-client/` directory structure
- [ ] Set up `pyproject.toml` with dependencies:
  - `httpx` or `requests` - HTTP client
  - `pydantic` - Data validation
  - `python-dotenv` - Environment variable management
- [ ] Create `README.md` with usage examples
- [ ] Set up basic test structure

**Dependencies:**
```toml
[project]
name = "jira-client"
version = "0.1.0"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.8",
    "python-dotenv>=1.0.0",
]
```

#### 1.2 Core Models

**Tasks:**
- [ ] Create `jira_client/models.py` with Pydantic models:
  - [ ] `JiraConfig` - Configuration model
  - [ ] `JiraIssue` - Issue data model
  - [ ] `JiraIssueCreate` - Issue creation payload
  - [ ] `JiraIssueUpdate` - Issue update payload
  - [ ] `JiraIssueResponse` - API response model
  - [ ] `JiraProject` - Project information
  - [ ] `JiraUser` - User information
  - [ ] `JiraPriority` - Priority enum
  - [ ] `JiraIssueType` - Issue type enum
- [ ] Add validation and type hints

**Example Models:**
```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict, Any

class JiraPriority(str, Enum):
    LOWEST = "Lowest"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    HIGHEST = "Highest"

class JiraIssueCreate(BaseModel):
    project_key: str
    summary: str
    description: str
    issue_type: str = "Task"
    priority: Optional[JiraPriority] = None
    labels: Optional[List[str]] = None
    assignee: Optional[str] = None
    components: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class JiraIssueResponse(BaseModel):
    key: str
    id: str
    self: str
    summary: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    created: str
    updated: str
    url: Optional[str] = None
```

#### 1.3 Jira Client Implementation

**Tasks:**
- [ ] Create `jira_client/client.py`:
  - [ ] `JiraClient` class
  - [ ] Authentication (API token or OAuth)
  - [ ] `create_issue()` method
  - [ ] `get_issue()` method
  - [ ] `update_issue()` method
  - [ ] `search_issues()` method
  - [ ] `get_project()` method
  - [ ] `bulk_create_issues()` method
  - [ ] Error handling and retries
  - [ ] Rate limiting support
- [ ] Support Jira Cloud REST API v3
- [ ] Handle authentication (API token recommended)
- [ ] Add request/response logging

**Example API:**
```python
from jira_client import JiraClient, JiraIssueCreate

# Initialize client
client = JiraClient(
    base_url="https://your-domain.atlassian.net",
    email="user@example.com",
    api_token=os.getenv("JIRA_API_TOKEN")
)

# Create a single issue
issue = client.create_issue(
    JiraIssueCreate(
        project_key="PROJ",
        summary="Implement orchestrator core",
        description="Create the main orchestrator class with run identity",
        issue_type="Task",
        priority=JiraPriority.HIGH,
        labels=["orchestrator", "phase-1"]
    )
)
print(f"Created issue: {issue.key} - {issue.url}")

# Bulk create issues
issues = client.bulk_create_issues([
    JiraIssueCreate(project_key="PROJ", summary="Task 1", ...),
    JiraIssueCreate(project_key="PROJ", summary="Task 2", ...),
])
```

#### 1.4 Configuration Management

**Tasks:**
- [ ] Create configuration system:
  - [ ] Environment variable support
  - [ ] Config file support (YAML/JSON)
  - [ ] Default values
- [ ] Support multiple Jira instances
- [ ] Credential management (never commit secrets)

**Configuration Example:**
```python
# From environment variables
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=user@example.com
JIRA_API_TOKEN=your_api_token_here
JIRA_PROJECT_KEY=PROJ

# Or from config file
jira:
  base_url: "https://your-domain.atlassian.net"
  email: "user@example.com"
  api_token_env: "JIRA_API_TOKEN"
  project_key: "PROJ"
  default_priority: "Medium"
  default_labels: ["automated"]
```

#### 1.5 Issue Templates

**Tasks:**
- [ ] Create `jira_client/templates.py`:
  - [ ] `IssueTemplate` base class
  - [ ] Template formatters for common use cases
  - [ ] Markdown/Jira markup support
  - [ ] Custom template support
- [ ] Pre-built templates:
  - [ ] `TaskTemplate` - Generic task template
  - [ ] `BugTemplate` - Bug report template
  - [ ] `FeatureTemplate` - Feature request template
  - [ ] `OrchestratorTaskTemplate` - Orchestrator-specific template

**Example Template:**
```python
from jira_client.templates import TaskTemplate

template = TaskTemplate(
    project_key="PROJ",
    summary="Implement {component}",
    description="""
    ## Overview
    {overview}
    
    ## Tasks
    {tasks}
    
    ## Acceptance Criteria
    {acceptance_criteria}
    
    ## References
    - Design doc: {design_doc}
    """,
    labels=["orchestrator", "{phase}"]
)

issue = template.create_issue(
    component="Orchestrator Core",
    overview="Create the main orchestrator class",
    tasks="- [ ] Create Orchestrator class\n- [ ] Add run UUID generation",
    acceptance_criteria="AC-RUN-001, AC-RUN-002",
    design_doc="ORCHESTRATOR_DESIGN.md",
    phase="phase-1"
)
```

#### 1.6 Error Handling

**Tasks:**
- [ ] Create `jira_client/exceptions.py`:
  - [ ] `JiraError` - Base exception
  - [ ] `JiraAuthenticationError` - Auth failures
  - [ ] `JiraNotFoundError` - Resource not found
  - [ ] `JiraValidationError` - Invalid request
  - [ ] `JiraRateLimitError` - Rate limiting
  - [ ] `JiraServerError` - Server errors
- [ ] Add retry logic with exponential backoff
- [ ] Handle rate limiting (429 responses)
- [ ] Graceful error messages

#### 1.7 Testing

**Tasks:**
- [ ] Create comprehensive test suite:
  - [ ] Unit tests for models
  - [ ] Unit tests for client (mocked HTTP)
  - [ ] Integration tests (optional, against test Jira instance)
  - [ ] Test fixtures and mocks
- [ ] Use `pytest` and `pytest-httpx` or `responses` for mocking
- [ ] Test error scenarios
- [ ] Test rate limiting handling

---

### Phase 2: CLI Tool & Project Integration

#### 2.1 CLI Tool

**Tasks:**
- [ ] Create CLI tool for creating issues:
  - [ ] `jira-cli create` - Create single issue
  - [ ] `jira-cli bulk-create` - Create multiple issues from file
  - [ ] `jira-cli list` - List issues
  - [ ] `jira-cli get` - Get issue details
- [ ] Support reading from YAML/JSON files
- [ ] Support templates

**CLI Example:**
```bash
# Create issue from command line
jira-cli create \
  --project PROJ \
  --summary "Implement orchestrator core" \
  --description "Create main orchestrator class" \
  --priority High \
  --labels orchestrator,phase-1

# Bulk create from file
jira-cli bulk-create issues.yaml

# List issues
jira-cli list --project PROJ --labels orchestrator
```

#### 2.2 Integration with This Project

**Tasks:**
- [ ] Create script to generate Jira issues from implementation plan:
  - [ ] Parse `ORCHESTRATOR_IMPLEMENTATION_PLAN.md`
  - [ ] Extract tasks and phases
  - [ ] Generate Jira issues for each task
  - [ ] Link issues (parent/child relationships)
- [ ] Create issues for:
  - [ ] Each phase
  - [ ] Each major task group
  - [ ] Individual implementation tasks (optional)
- [ ] Add Jira issue keys to implementation plan (back-reference)

**Example Script:**
```python
# scripts/create_orchestrator_issues.py
from jira_client import JiraClient, JiraIssueCreate
from pathlib import Path
import yaml

def parse_implementation_plan(plan_path: Path):
    """Parse implementation plan and extract tasks."""
    # Parse markdown, extract phases and tasks
    pass

def create_issues_from_plan(client: JiraClient, plan_path: Path):
    """Create Jira issues from implementation plan."""
    phases = parse_implementation_plan(plan_path)
    
    for phase in phases:
        # Create parent issue for phase
        phase_issue = client.create_issue(
            JiraIssueCreate(
                project_key="PROJ",
                summary=f"Phase {phase.number}: {phase.name}",
                description=phase.description,
                issue_type="Epic",
                labels=["orchestrator", f"phase-{phase.number}"]
            )
        )
        
        # Create child issues for tasks
        for task_group in phase.task_groups:
            task_issue = client.create_issue(
                JiraIssueCreate(
                    project_key="PROJ",
                    summary=task_group.name,
                    description=task_group.description,
                    issue_type="Task",
                    labels=["orchestrator", f"phase-{phase.number}"],
                    # Link to parent (via custom field or subtask)
                )
            )
```

#### 2.3 Documentation

**Tasks:**
- [ ] Create comprehensive README:
  - [ ] Installation instructions
  - [ ] Quick start guide
  - [ ] API documentation
  - [ ] Configuration examples
  - [ ] Usage examples
  - [ ] Error handling guide
- [ ] Add docstrings to all public APIs
- [ ] Create example scripts

---

### Phase 3: Advanced Features (Future)

#### 3.1 Issue Synchronization

**Tasks:**
- [ ] `sync_issue_status()` - Sync status from Jira
- [ ] `update_issue_from_local()` - Update Jira from local changes
- [ ] Webhook support for real-time updates

#### 3.2 Advanced Queries

**Tasks:**
- [ ] JQL (Jira Query Language) support
- [ ] Complex search queries
- [ ] Issue linking (blocks, relates to, etc.)
- [ ] Attachment support

#### 3.3 Workflow Integration

**Tasks:**
- [ ] Transition issues through workflows
- [ ] Comment on issues
- [ ] Assign issues
- [ ] Add watchers

---

## Usage in This Project

### Creating Issues for Orchestrator Implementation

**Step 1: Install the module**
```bash
cd jira-client
pip install -e .
```

**Step 2: Configure**
```bash
export JIRA_BASE_URL=https://your-domain.atlassian.net
export JIRA_EMAIL=your-email@example.com
export JIRA_API_TOKEN=your_token
export JIRA_PROJECT_KEY=PROJ
```

**Step 3: Create issues**
```python
from jira_client import JiraClient, JiraIssueCreate

client = JiraClient.from_env()

# Create issues for Phase 1 tasks
issues = [
    JiraIssueCreate(
        project_key="PROJ",
        summary="Phase 1.1: Project Setup",
        description="Set up orchestrator directory structure and dependencies",
        issue_type="Task",
        labels=["orchestrator", "phase-1"]
    ),
    # ... more issues
]

for issue_data in issues:
    issue = client.create_issue(issue_data)
    print(f"Created: {issue.key}")
```

**Step 4: Use CLI**
```bash
# Create issues from YAML file
jira-cli bulk-create orchestrator_issues.yaml
```

### Integration with Orchestrator (Later)

Once orchestrator is implemented, the Jira client can be integrated:

```python
# In orchestrator/runners/gcgm_runner.py
from jira_client import JiraClient, JiraIssueCreate

class GCGMRunner:
    def __init__(self, jira_client: JiraClient):
        self.jira_client = jira_client
    
    def create_issue_for_finding(self, finding: Finding) -> JiraIssue:
        """Create Jira issue for a code finding."""
        issue = self.jira_client.create_issue(
            JiraIssueCreate(
                project_key=self.config.project_key,
                summary=f"[GCCO] {finding.rule_id}: {finding.rule_description}",
                description=self._format_finding_description(finding),
                issue_type="Bug",
                priority=self._calculate_priority(finding),
                labels=["gcrs", "code-optimization", finding.language],
                custom_fields={
                    "finding_id": finding.id,
                    "file_path": finding.file_path,
                    "line_number": finding.line_start,
                }
            )
        )
        return issue
```

---

## Project Structure Recommendation

```
gcrs_project/
├── jira-client/               # NEW: Standalone Jira client package
│   ├── jira_client/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── models.py
│   │   ├── exceptions.py
│   │   └── templates.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── gcrs/                      # Existing GCRS scanner
├── orchestrator/              # Orchestrator (uses jira-client)
├── scripts/                    # Utility scripts
│   └── create_orchestrator_issues.py
└── docs-and-design/
```

---

## Benefits of This Approach

1. **Immediate Value**: Start tracking work in Jira right away
2. **Generic Module**: Reusable in any Python project
3. **Early Testing**: Discover issues before orchestrator integration
4. **Clear Separation**: Jira logic separate from orchestrator logic
5. **Easy Integration**: Simple import when ready
6. **Publishable**: Can be published to PyPI for others to use

---

## Next Steps

1. **Review and approve this plan**
2. **Set up Jira instance** (if not already done)
3. **Create API token** in Jira
4. **Start Phase 1.1: Project Setup**
5. **Create first Jira issues** for orchestrator implementation tasks

---

## Open Questions

1. **Jira Instance**: Do you already have a Jira instance set up?
2. **Project Key**: What project key should we use? (e.g., "GCRS", "ORCH")
3. **Issue Types**: What issue types do you want to use? (Task, Story, Bug, Epic)
4. **Workflow**: Do you have custom workflows or use default?
5. **Authentication**: API token or OAuth?

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-16  
**Status:** Planning Phase

