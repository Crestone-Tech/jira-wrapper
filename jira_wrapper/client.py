"""Main JiraWrapper client class."""

from typing import List, Optional
from jira import JIRA
from jira.exceptions import JIRAError

from jira_wrapper.models import JiraConfig, IssueCreate, IssueResponse
from jira_wrapper.exceptions import (
    JiraWrapperError,
    JiraAuthenticationError,
    JiraNotFoundError,
)


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
            error_str = str(e).lower()
            if "authentication" in error_str or "401" in error_str or "403" in error_str:
                raise JiraAuthenticationError(f"Failed to authenticate: {e}") from e
            raise JiraWrapperError(f"Failed to connect to Jira: {e}") from e
    
    @classmethod
    def from_env(cls) -> 'JiraWrapper':
        """Create wrapper from environment variables."""
        config = JiraConfig.from_env()
        return cls(config)
    
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
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str:
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

