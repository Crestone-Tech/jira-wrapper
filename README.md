# Jira Wrapper

A simplified, type-safe wrapper around the [jira](https://github.com/pycontribs/jira) Python library. This wrapper provides a cleaner API, Pydantic models for validation, and better error handling.

## Features

- ✅ **Simplified API**: Cleaner interface than the raw jira library
- ✅ **Type Safety**: Pydantic models for validation and IDE support
- ✅ **Better Error Handling**: Custom exceptions with clear error messages
- ✅ **Easy Configuration**: Load from environment variables or config
- ✅ **Bulk Operations**: Create multiple issues at once
- ✅ **Search Support**: JQL-based issue searching

## Installation

```bash
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Set up environment variables

Create a `.env` file:

```bash
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_api_token_here
JIRA_PROJECT_KEY=PROJ  # Optional default project
```

### 2. Basic Usage

```python
from jira_wrapper import JiraWrapper, IssueCreate, Priority

# Initialize from environment variables
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

### 3. Get an Issue

```python
# Get issue by key
issue = jira.get_issue('PROJ-123')
print(f"{issue.key}: {issue.summary} - {issue.status}")
```

### 4. Search Issues

```python
# Search for issues using JQL
issues = jira.search_issues(
    jql='project = PROJ AND labels = orchestrator',
    max_results=100
)

for issue in issues:
    print(f"{issue.key}: {issue.summary} - {issue.status}")
```

### 5. Bulk Create Issues

```python
issues = [
    IssueCreate(project_key='PROJ', summary='Task 1', description='...'),
    IssueCreate(project_key='PROJ', summary='Task 2', description='...'),
    IssueCreate(project_key='PROJ', summary='Task 3', description='...'),
]

results = jira.bulk_create_issues(issues)
print(f"Created {len(results)} issues")
```

## API Reference

### JiraWrapper

Main wrapper class that wraps the jira library.

#### Methods

- `from_env() -> JiraWrapper`: Create wrapper from environment variables
- `create_issue(issue: IssueCreate) -> IssueResponse`: Create a Jira issue
- `get_issue(issue_key: str) -> IssueResponse`: Get issue by key
- `search_issues(jql: str, max_results: int = 50) -> List[IssueResponse]`: Search issues using JQL
- `bulk_create_issues(issues: List[IssueCreate]) -> List[IssueResponse]`: Create multiple issues
- `add_comment(issue_key: str, comment: str) -> None`: Add comment to issue
- `transition_issue(issue_key: str, transition_name: str) -> None`: Transition issue through workflow

### Models

#### IssueCreate

Model for creating Jira issues.

```python
IssueCreate(
    project_key: str,              # Required: Project key
    summary: str,                  # Required: Issue summary/title
    description: str = "",         # Optional: Issue description
    issue_type: str | IssueType = IssueType.TASK,  # Issue type
    priority: Optional[Priority] = None,           # Priority
    labels: Optional[List[str]] = None,            # Labels
    assignee: Optional[str] = None,                # Assignee email/username
    components: Optional[List[str]] = None,         # Component names
    custom_fields: Optional[Dict[str, Any]] = None, # Custom fields
    parent_key: Optional[str] = None,               # Parent issue key for subtasks
)
```

#### IssueResponse

Model representing a Jira issue response.

```python
IssueResponse(
    key: str,                      # Issue key (e.g., "PROJ-123")
    id: str,                       # Issue ID
    summary: str,                  # Issue summary
    description: Optional[str],     # Issue description
    status: str,                   # Issue status
    priority: Optional[str],       # Priority
    assignee: Optional[str],       # Assignee email
    labels: List[str],             # Labels
    url: str,                      # Issue URL
    created: str,                  # Creation timestamp
    updated: str,                  # Last update timestamp
)
```

### Exceptions

- `JiraWrapperError`: Base exception for all jira-wrapper errors
- `JiraAuthenticationError`: Authentication failed
- `JiraNotFoundError`: Resource not found (404)
- `JiraValidationError`: Invalid request data
- `JiraRateLimitError`: Rate limit exceeded
- `JiraServerError`: Jira server error

## Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=jira_wrapper --cov-report=html
```

### Project Structure

```
jira-wrapper/
├── jira_wrapper/
│   ├── __init__.py
│   ├── client.py          # JiraWrapper class
│   ├── models.py          # Pydantic models
│   └── exceptions.py       # Custom exceptions
├── tests/
│   ├── test_client.py
│   ├── test_models.py
│   └── test_exceptions.py
├── pyproject.toml
└── README.md
```

## License

See LICENSE file for details.
