"""Pydantic models for jira-wrapper."""

import os
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field
from dotenv import load_dotenv

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
        
        load_dotenv()
        
        base_url = os.getenv('JIRA_BASE_URL')
        email = os.getenv('JIRA_EMAIL')
        api_token = os.getenv('JIRA_API_TOKEN')
        
        if not base_url or not email or not api_token:
            missing = []
            if not base_url:
                missing.append('JIRA_BASE_URL')
            if not email:
                missing.append('JIRA_EMAIL')
            if not api_token:
                missing.append('JIRA_API_TOKEN')
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(
            base_url=base_url,
            email=email,
            api_token=api_token,
            project_key=os.getenv('JIRA_PROJECT_KEY'),
            timeout_seconds=int(os.getenv('JIRA_TIMEOUT_SECONDS', '30')),
        )


class IssueCreate(BaseModel):
    """Simplified model for creating Jira issues."""
    project_key: str = Field(..., min_length=1, description="Jira project key (e.g., 'PROJ')")
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
        # Get enum values - use .value for enums, otherwise use as-is
        if isinstance(self.issue_type, IssueType):
            issue_type_name = self.issue_type.value
        else:
            issue_type_name = self.issue_type
        
        fields = {
            'project': {'key': self.project_key},
            'summary': self.summary,
            'description': self.description,
            'issuetype': {'name': issue_type_name},
        }
        
        if self.priority:
            # After None check, self.priority is Priority enum, use .value
            fields['priority'] = {'name': self.priority.value}
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

