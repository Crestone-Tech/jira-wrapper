# Jira Wrapper - Generic Standalone Module Plan

## Overview

This document outlines the plan for creating a **generic, standalone wrapper module** around the existing `jira` Python library. This approach gives us the best of both worlds:

- ✅ **Use battle-tested library**: No need to build HTTP client, auth, error handling
- ✅ **Simpler API**: Wrapper provides a cleaner, more intuitive interface
- ✅ **Templates & Formatters**: Custom templates for common use cases
- ✅ **Generic & Reusable**: Standalone package usable in any project
- ✅ **Faster Implementation**: Much quicker than building from scratch

## Why a Wrapper?

### Benefits

1. **Simpler API**: The `jira` library can be verbose - wrapper simplifies common operations
2. **Templates**: Pre-built templates for common issue types
3. **Better Error Handling**: Wrap errors in more user-friendly exceptions
4. **Type Safety**: Add Pydantic models for better IDE support and validation
5. **Convenience Methods**: Add helper methods for common workflows
6. **Configuration Management**: Easier config handling
7. **Still Generic**: Not tied to orchestrator, usable anywhere

### Example: Before vs After

**Before (raw jira library):**
```python
from jira import JIRA

jira = JIRA(
    server='https://your-domain.atlassian.net',
    basic_auth=('email@example.com', 'api_token')
)

issue_dict = {
    'project': {'key': 'PROJ'},
    'summary': 'Task title',
    'description': 'Task description',
    'issuetype': {'name': 'Task'},
    'labels': ['label1', 'label2'],
    'priority': {'name': 'High'}
}

issue = jira.create_issue(fields=issue_dict)
```

**After (with wrapper):**
```python
from jira_wrapper import JiraWrapper, IssueCreate

jira = JiraWrapper.from_env()

issue = jira.create_issue(
    IssueCreate(
        project_key='PROJ',
        summary='Task title',
        description='Task description',
        issue_type='Task',
        labels=['label1', 'label2'],
        priority='High'
    )
)
```

Much cleaner! 🎉

---

## Module Structure

### Standalone Package Structure

```
jira-wrapper/                    # Standalone package
├── jira_wrapper/
│   ├── __init__.py
│   ├── client.py                # Main JiraWrapper class (wraps jira library)
│   ├── models.py                # Pydantic models for type safety
│   ├── templates.py             # Issue templates/formatters
│   ├── exceptions.py            # Custom exceptions
│   └── config.py                # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_models.py
│   ├── test_templates.py
│   └── conftest.py
├── pyproject.toml
├── README.md
├── .env.example
└── examples/
    ├── basic_usage.py
    ├── bulk_create.py
    └── template_usage.py
```

---

## Implementation Plan

### Phase 1: Core Wrapper (MVP)

#### 1.1 Project Setup

**Tasks:**
- [ ] Create `jira-wrapper/` directory structure
- [ ] Set up `pyproject.toml`:
  ```toml
  [project]
  name = "jira-wrapper"
  version = "0.1.0"
  dependencies = [
      "jira>=3.5.0",
      "pydantic>=2.8",
      "python-dotenv>=1.0.0",
  ]
  
  [project.optional-dependencies]
  dev = [
      "pytest>=8.3",
      "pytest-cov>=6.0",
      "httpx>=0.27",  # For mocking in tests
  ]
  ```
- [ ] Create `README.md` with quick start
- [ ] Set up test structure

#### 1.2 Pydantic Models

**Tasks:**
- [ ] Create `jira_wrapper/models.py` with clean Pydantic models:
  - [ ] `JiraConfig` - Configuration model
  - [ ] `IssueCreate` - Simplified issue creation model
  - [ ] `IssueUpdate` - Issue update model
  - [ ] `IssueResponse` - Response model (simplified from jira library)
  - [ ] `Priority` - Enum for priorities
  - [ ] `IssueType` - Common issue types enum
- [ ] Add validation
- [ ] Add helper methods for common operations

**Example Models:**
```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict, Any

class Priority(str, Enum):
    """Jira priority levels."""
    LOWEST = "Lowest"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    HIGHEST = "Highest"
    CRITICAL = "Critical"  # If your Jira has this

class IssueType(str, Enum):
    """Common Jira issue types."""
    TASK = "Task"
    BUG = "Bug"
    STORY = "Story"
    EPIC = "Epic"
    SUBTASK = "Sub-task"

class IssueCreate(BaseModel):
    """Simplified model for creating Jira issues."""
    project_key: str = Field(..., description="Jira project key (e.g., 'PROJ')")
    summary: str = Field(..., min_length=1, description="Issue summary/title")
    description: str = Field(default="", description="Issue description")
    issue_type: str | IssueType = Field(default=IssueType.TASK, description="Issue type")
    priority: Optional[Priority] = Field(default=None, description="Issue priority")
    labels: Optional[List[str]] = Field(default=None, description="Issue labels")
    assignee: Optional[str] = Field(default=None, description="Assignee email or username")
    components: Optional[List[str]] = Field(default=None, description="Component names")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Custom fields")
    parent_key: Optional[str] = Field(default=None, description="Parent issue key for subtasks")
    
    def to_jira_dict(self) -> Dict[str, Any]:
        """Convert to jira library format."""
        fields = {
            'project': {'key': self.project_key},
            'summary': self.summary,
            'description': self.description,
            'issuetype': {'name': str(self.issue_type)},
        }
        
        if self.priority:
            fields['priority'] = {'name': str(self.priority)}
        if self.labels:
            fields['labels'] = self.labels
        if self.assignee:
            fields['assignee'] = {'name': self.assignee}
        if self.components:
            fields['components'] = [{'name': c} for c in self.components]
        if self.parent_key:
            fields['parent'] = {'key': self.parent_key}
        if self.custom_fields:
            fields.update(self.custom_fields)
            
        return {'fields': fields}

class IssueResponse(BaseModel):
    """Simplified response model."""
    key: str
    id: str
    summary: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    labels: List[str] = []
    url: str
    created: str
    updated: str
    
    @classmethod
    def from_jira_issue(cls, jira_issue) -> 'IssueResponse':
        """Create from jira library Issue object."""
        return cls(
            key=jira_issue.key,
            id=jira_issue.id,
            summary=jira_issue.fields.summary,
            description=getattr(jira_issue.fields, 'description', None),
            status=jira_issue.fields.status.name,
            priority=getattr(jira_issue.fields.priority, 'name', None) if jira_issue.fields.priority else None,
            assignee=getattr(jira_issue.fields.assignee, 'emailAddress', None) if jira_issue.fields.assignee else None,
            labels=getattr(jira_issue.fields, 'labels', []) or [],
            url=jira_issue.permalink(),
            created=str(jira_issue.fields.created),
            updated=str(jira_issue.fields.updated),
        )
```

#### 1.3 JiraWrapper Client

**Tasks:**
- [ ] Create `jira_wrapper/client.py`:
  - [ ] `JiraWrapper` class that wraps `jira.JIRA`
  - [ ] `__init__()` - Initialize with config
  - [ ] `from_env()` - Class method to create from environment variables
  - [ ] `from_config()` - Class method to create from config file
  - [ ] `create_issue()` - Simplified issue creation
  - [ ] `get_issue()` - Get issue by key
  - [ ] `update_issue()` - Update issue
  - [ ] `search_issues()` - Search with JQL
  - [ ] `bulk_create_issues()` - Create multiple issues
  - [ ] `add_comment()` - Add comment to issue
  - [ ] `transition_issue()` - Transition issue through workflow
  - [ ] `get_project()` - Get project info
- [ ] Wrap jira library errors in custom exceptions
- [ ] Add convenience methods

**Example Implementation:**
```python
from jira import JIRA
from jira.exceptions import JIRAError
from typing import List, Optional
from jira_wrapper.models import IssueCreate, IssueResponse, JiraConfig
from jira_wrapper.exceptions import JiraWrapperError, JiraAuthenticationError, JiraNotFoundError

class JiraWrapper:
    """Simplified wrapper around the jira library."""
    
    def __init__(self, config: JiraConfig):
        """Initialize wrapper with configuration."""
        self.config = config
        try:
            self._jira = JIRA(
                server=config.base_url,
                basic_auth=(config.email, config.api_token),
                timeout=config.timeout_seconds
            )
        except JIRAError as e:
            if "authentication" in str(e).lower() or "401" in str(e):
                raise JiraAuthenticationError(f"Failed to authenticate: {e}") from e
            raise JiraWrapperError(f"Failed to connect to Jira: {e}") from e
    
    @classmethod
    def from_env(cls) -> 'JiraWrapper':
        """Create wrapper from environment variables."""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        config = JiraConfig(
            base_url=os.getenv('JIRA_BASE_URL'),
            email=os.getenv('JIRA_EMAIL'),
            api_token=os.getenv('JIRA_API_TOKEN'),
            project_key=os.getenv('JIRA_PROJECT_KEY'),  # Optional default
        )
        return cls(config)
    
    @classmethod
    def from_config(cls, config_path: str) -> 'JiraWrapper':
        """Create wrapper from config file."""
        # Load from YAML/JSON config
        pass
    
    def create_issue(self, issue: IssueCreate) -> IssueResponse:
        """Create a Jira issue."""
        try:
            jira_issue = self._jira.create_issue(**issue.to_jira_dict())
            return IssueResponse.from_jira_issue(jira_issue)
        except JIRAError as e:
            raise JiraWrapperError(f"Failed to create issue: {e}") from e
    
    def get_issue(self, issue_key: str) -> IssueResponse:
        """Get issue by key."""
        try:
            jira_issue = self._jira.issue(issue_key)
            return IssueResponse.from_jira_issue(jira_issue)
        except JIRAError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise JiraNotFoundError(f"Issue {issue_key} not found") from e
            raise JiraWrapperError(f"Failed to get issue: {e}") from e
    
    def bulk_create_issues(self, issues: List[IssueCreate]) -> List[IssueResponse]:
        """Create multiple issues."""
        results = []
        for issue in issues:
            try:
                result = self.create_issue(issue)
                results.append(result)
            except JiraWrapperError as e:
                # Log error but continue with others
                print(f"Failed to create issue '{issue.summary}': {e}")
                # Optionally: collect errors and return them
        return results
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[IssueResponse]:
        """Search issues using JQL."""
        try:
            jira_issues = self._jira.search_issues(jql, maxResults=max_results)
            return [IssueResponse.from_jira_issue(issue) for issue in jira_issues]
        except JIRAError as e:
            raise JiraWrapperError(f"Failed to search issues: {e}") from e
    
    def add_comment(self, issue_key: str, comment: str) -> None:
        """Add comment to issue."""
        try:
            issue = self._jira.issue(issue_key)
            issue.add_comment(comment)
        except JIRAError as e:
            raise JiraWrapperError(f"Failed to add comment: {e}") from e
    
    def transition_issue(self, issue_key: str, transition_name: str) -> None:
        """Transition issue through workflow."""
        try:
            issue = self._jira.issue(issue_key)
            transitions = self._jira.transitions(issue)
            transition_id = next(
                (t['id'] for t in transitions if t['name'].lower() == transition_name.lower()),
                None
            )
            if not transition_id:
                raise JiraWrapperError(f"Transition '{transition_name}' not found")
            self._jira.transition_issue(issue, transition_id)
        except JIRAError as e:
            raise JiraWrapperError(f"Failed to transition issue: {e}") from e
```

#### 1.4 Configuration Management

**Tasks:**
- [ ] Create `jira_wrapper/config.py`:
  - [ ] `JiraConfig` Pydantic model
  - [ ] Environment variable loading
  - [ ] Config file loading (YAML/JSON)
  - [ ] Validation

**Example:**
```python
from pydantic import BaseModel, Field
from typing import Optional
import os
from pathlib import Path

class JiraConfig(BaseModel):
    """Jira configuration."""
    base_url: str = Field(..., description="Jira base URL")
    email: str = Field(..., description="Email for authentication")
    api_token: str = Field(..., description="API token")
    project_key: Optional[str] = Field(default=None, description="Default project key")
    timeout_seconds: int = Field(default=30, description="Request timeout")
    
    @classmethod
    def from_env(cls) -> 'JiraConfig':
        """Load from environment variables."""
        return cls(
            base_url=os.getenv('JIRA_BASE_URL') or '',
            email=os.getenv('JIRA_EMAIL') or '',
            api_token=os.getenv('JIRA_API_TOKEN') or '',
            project_key=os.getenv('JIRA_PROJECT_KEY'),
            timeout_seconds=int(os.getenv('JIRA_TIMEOUT_SECONDS', '30')),
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'JiraConfig':
        """Load from YAML/JSON file."""
        # Implementation
        pass
```

#### 1.5 Custom Exceptions

**Tasks:**
- [ ] Create `jira_wrapper/exceptions.py`:
  - [ ] `JiraWrapperError` - Base exception
  - [ ] `JiraAuthenticationError` - Auth failures
  - [ ] `JiraNotFoundError` - Resource not found
  - [ ] `JiraValidationError` - Invalid request
  - [ ] `JiraRateLimitError` - Rate limiting
  - [ ] `JiraServerError` - Server errors

**Example:**
```python
class JiraWrapperError(Exception):
    """Base exception for jira-wrapper."""
    pass

class JiraAuthenticationError(JiraWrapperError):
    """Authentication failed."""
    pass

class JiraNotFoundError(JiraWrapperError):
    """Resource not found."""
    pass

class JiraValidationError(JiraWrapperError):
    """Invalid request data."""
    pass

class JiraRateLimitError(JiraWrapperError):
    """Rate limit exceeded."""
    pass

class JiraServerError(JiraWrapperError):
    """Jira server error."""
    pass
```

#### 1.6 Issue Templates

**Tasks:**
- [ ] Create `jira_wrapper/templates.py`:
  - [ ] `IssueTemplate` base class
  - [ ] `TaskTemplate` - Generic task template
  - [ ] `BugTemplate` - Bug report template
  - [ ] `FeatureTemplate` - Feature request template
  - [ ] `OrchestratorTaskTemplate` - Orchestrator-specific (optional, can be in orchestrator)

**Example:**
```python
from typing import Dict, Any
from jira_wrapper.models import IssueCreate

class IssueTemplate:
    """Base class for issue templates."""
    
    def __init__(self, project_key: str, default_labels: list = None):
        self.project_key = project_key
        self.default_labels = default_labels or []
    
    def create(self, **kwargs) -> IssueCreate:
        """Create issue from template with provided values."""
        raise NotImplementedError

class TaskTemplate(IssueTemplate):
    """Template for generic tasks."""
    
    def create(
        self,
        summary: str,
        description: str = "",
        priority: str = "Medium",
        labels: list = None,
        **kwargs
    ) -> IssueCreate:
        """Create a task issue."""
        all_labels = self.default_labels + (labels or [])
        return IssueCreate(
            project_key=self.project_key,
            summary=summary,
            description=description,
            issue_type="Task",
            priority=priority,
            labels=all_labels,
            **kwargs
        )

class OrchestratorTaskTemplate(TaskTemplate):
    """Template for orchestrator implementation tasks."""
    
    def __init__(self, project_key: str):
        super().__init__(project_key, default_labels=["orchestrator"])
    
    def create(
        self,
        summary: str,
        description: str = "",
        phase: str = None,
        acceptance_criteria: list = None,
        **kwargs
    ) -> IssueCreate:
        """Create orchestrator task issue."""
        labels = ["orchestrator"]
        if phase:
            labels.append(f"phase-{phase}")
        
        # Format description with acceptance criteria
        if acceptance_criteria:
            desc = description + "\n\n## Acceptance Criteria\n"
            desc += "\n".join(f"- {ac}" for ac in acceptance_criteria)
        else:
            desc = description
        
        return super().create(
            summary=summary,
            description=desc,
            labels=labels,
            **kwargs
        )
```

#### 1.7 Testing

**Tasks:**
- [ ] Create comprehensive test suite:
  - [ ] Unit tests for models
  - [ ] Unit tests for wrapper (mock jira library)
  - [ ] Unit tests for templates
  - [ ] Integration tests (optional, against test Jira instance)
- [ ] Use `pytest` and mocking
- [ ] Test error scenarios

---

### Phase 2: CLI Tool & Convenience Features

#### 2.1 CLI Tool

**Tasks:**
- [ ] Create CLI using `click` or `argparse`:
  - [ ] `jira-wrapper create` - Create single issue
  - [ ] `jira-wrapper bulk-create` - Create from file
  - [ ] `jira-wrapper get` - Get issue details
  - [ ] `jira-wrapper search` - Search issues
  - [ ] `jira-wrapper comment` - Add comment
- [ ] Support YAML/JSON input files

#### 2.2 Additional Convenience Methods

**Tasks:**
- [ ] Add helper methods:
  - [ ] `create_epic_with_tasks()` - Create epic and linked tasks
  - [ ] `link_issues()` - Link issues
  - [ ] `add_watchers()` - Add watchers
  - [ ] `get_issue_history()` - Get issue change history

---

## Usage Examples

### Basic Usage

```python
from jira_wrapper import JiraWrapper, IssueCreate, Priority

# Initialize from environment
jira = JiraWrapper.from_env()

# Create an issue
issue = jira.create_issue(
    IssueCreate(
        project_key='PROJ',
        summary='Implement orchestrator core',
        description='Create the main orchestrator class',
        issue_type='Task',
        priority=Priority.HIGH,
        labels=['orchestrator', 'phase-1']
    )
)

print(f"Created: {issue.key} - {issue.url}")
```

### Using Templates

```python
from jira_wrapper import JiraWrapper
from jira_wrapper.templates import OrchestratorTaskTemplate

jira = JiraWrapper.from_env()
template = OrchestratorTaskTemplate(project_key='PROJ')

issue = jira.create_issue(
    template.create(
        summary='Phase 1.1: Project Setup',
        description='Set up orchestrator directory structure',
        phase='1',
        acceptance_criteria=[
            'Directory structure created',
            'Dependencies configured',
            'Tests passing'
        ]
    )
)
```

### Bulk Create

```python
from jira_wrapper import JiraWrapper, IssueCreate

jira = JiraWrapper.from_env()

issues = [
    IssueCreate(project_key='PROJ', summary='Task 1', ...),
    IssueCreate(project_key='PROJ', summary='Task 2', ...),
    IssueCreate(project_key='PROJ', summary='Task 3', ...),
]

results = jira.bulk_create_issues(issues)
print(f"Created {len(results)} issues")
```

### Search Issues

```python
# Search for all orchestrator issues
issues = jira.search_issues(
    jql='project = PROJ AND labels = orchestrator',
    max_results=100
)

for issue in issues:
    print(f"{issue.key}: {issue.summary} - {issue.status}")
```

---

## Integration with Orchestrator

Later, when orchestrator is ready, integrate like this:

```python
# In orchestrator/integrations/jira_integration.py
from jira_wrapper import JiraWrapper, IssueCreate

class JiraIntegration:
    def __init__(self, jira_wrapper: JiraWrapper):
        self.jira = jira_wrapper
    
    def create_issue_for_finding(self, finding: Finding) -> str:
        """Create Jira issue for a code finding."""
        issue = self.jira.create_issue(
            IssueCreate(
                project_key=self.config.project_key,
                summary=f"[GCCO] {finding.rule_id}: {finding.description}",
                description=self._format_finding(finding),
                issue_type='Bug',
                priority=self._calculate_priority(finding),
                labels=['gcrs', 'code-optimization', finding.language],
            )
        )
        return issue.key
```

---

## Project Structure

```
gcrs_project/
├── jira-wrapper/               # NEW: Standalone wrapper package
│   ├── jira_wrapper/
│   │   ├── __init__.py
│   │   ├── client.py           # JiraWrapper class
│   │   ├── models.py           # Pydantic models
│   │   ├── templates.py        # Issue templates
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── config.py           # Configuration
│   ├── tests/
│   ├── examples/
│   ├── pyproject.toml
│   └── README.md
├── gcrs/                       # Existing GCRS scanner
├── orchestrator/               # Orchestrator (uses jira-wrapper)
└── scripts/                    # Utility scripts
    └── create_orchestrator_issues.py
```

---

## Benefits of This Approach

1. ✅ **Faster Development**: Use existing library, just wrap it
2. ✅ **Simpler API**: Cleaner interface than raw jira library
3. ✅ **Type Safety**: Pydantic models for validation
4. ✅ **Templates**: Pre-built templates for common cases
5. ✅ **Generic**: Standalone, reusable in any project
6. ✅ **Maintainable**: Thin layer, easy to maintain
7. ✅ **Testable**: Easy to mock and test

---

## Next Steps

1. **Review and approve this plan**
2. **Set up Jira API token** (if not already done)
3. **Start Phase 1.1: Project Setup**
4. **Create first issues** for orchestrator implementation

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-16  
**Status:** Planning Phase

