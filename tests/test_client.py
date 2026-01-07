"""Tests for JiraWrapper client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from jira.exceptions import JIRAError

from jira_wrapper.client import JiraWrapper
from jira_wrapper.models import JiraConfig, IssueCreate, IssueResponse, Priority
from jira_wrapper.exceptions import (
    JiraWrapperError,
    JiraAuthenticationError,
    JiraNotFoundError,
)


class TestJiraWrapperInitialization:
    """Tests for JiraWrapper initialization."""
    
    @patch('jira_wrapper.client.JIRA')
    def test_initializes_with_valid_config(self, mock_jira_class):
        """Test that wrapper initializes with valid config."""
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance
        
        config = JiraConfig(
            base_url="https://example.atlassian.net",
            email="user@example.com",
            api_token="token123"
        )
        
        wrapper = JiraWrapper(config)
        
        assert wrapper.config == config
        assert wrapper._jira == mock_jira_instance
        mock_jira_class.assert_called_once_with(
            server="https://example.atlassian.net",
            basic_auth=("user@example.com", "token123"),
            timeout=30
        )
    
    @patch('jira_wrapper.client.JIRA')
    def test_authentication_error_raises_custom_exception(self, mock_jira_class):
        """Test that authentication errors raise custom exception."""
        mock_jira_class.side_effect = JIRAError(status_code=401, text="Unauthorized")
        
        config = JiraConfig(
            base_url="https://example.atlassian.net",
            email="user@example.com",
            api_token="token123"
        )
        
        with pytest.raises(JiraAuthenticationError) as exc_info:
            JiraWrapper(config)
        
        assert "Failed to authenticate" in str(exc_info.value)
    
    @patch('jira_wrapper.client.JIRA')
    def test_connection_error_raises_wrapper_error(self, mock_jira_class):
        """Test that connection errors raise wrapper error."""
        mock_jira_class.side_effect = JIRAError(status_code=500, text="Server Error")
        
        config = JiraConfig(
            base_url="https://example.atlassian.net",
            email="user@example.com",
            api_token="token123"
        )
        
        with pytest.raises(JiraWrapperError) as exc_info:
            JiraWrapper(config)
        
        assert "Failed to connect to Jira" in str(exc_info.value)
    
    @patch('jira_wrapper.client.JiraConfig')
    @patch('jira_wrapper.client.JIRA')
    def test_from_env_creates_instance(self, mock_jira_class, mock_config_class):
        """Test that from_env() creates instance from environment."""
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance
        
        mock_config = Mock()
        mock_config.base_url = "https://example.atlassian.net"
        mock_config.email = "user@example.com"
        mock_config.api_token = "token123"
        mock_config.timeout_seconds = 30
        mock_config_class.from_env.return_value = mock_config
        
        wrapper = JiraWrapper.from_env()
        
        assert wrapper.config == mock_config
        assert wrapper._jira == mock_jira_instance


class TestJiraWrapperCreateIssue:
    """Tests for JiraWrapper.create_issue()."""
    
    @pytest.fixture
    def wrapper(self):
        """Create a JiraWrapper instance with mocked JIRA client."""
        with patch('jira_wrapper.client.JIRA') as mock_jira_class:
            mock_jira_instance = Mock()
            mock_jira_class.return_value = mock_jira_instance
            
            config = JiraConfig(
                base_url="https://example.atlassian.net",
                email="user@example.com",
                api_token="token123"
            )
            
            wrapper = JiraWrapper(config)
            wrapper._jira = mock_jira_instance
            return wrapper
    
    def test_create_issue_success(self, wrapper):
        """Test creating issue with valid data."""
        # Create mock jira issue
        mock_jira_issue = Mock()
        mock_jira_issue.key = "PROJ-1"
        mock_jira_issue.id = "12345"
        mock_jira_issue.fields.summary = "Test issue"
        mock_jira_issue.fields.description = "Test description"
        mock_jira_issue.fields.status.name = "To Do"
        mock_jira_issue.fields.priority = None
        mock_jira_issue.fields.assignee = None
        mock_jira_issue.fields.labels = []
        mock_jira_issue.fields.created = "2024-01-01T00:00:00"
        mock_jira_issue.fields.updated = "2024-01-02T00:00:00"
        mock_jira_issue.permalink.return_value = "https://example.atlassian.net/browse/PROJ-1"
        
        wrapper._jira.create_issue.return_value = mock_jira_issue
        
        issue_create = IssueCreate(
            project_key="PROJ",
            summary="Test issue",
            description="Test description"
        )
        
        result = wrapper.create_issue(issue_create)
        
        assert isinstance(result, IssueResponse)
        assert result.key == "PROJ-1"
        assert result.summary == "Test issue"
        wrapper._jira.create_issue.assert_called_once()
    
    def test_create_issue_handles_jira_error(self, wrapper):
        """Test that Jira API errors are handled gracefully."""
        wrapper._jira.create_issue.side_effect = JIRAError(status_code=400, text="Bad Request")
        
        issue_create = IssueCreate(
            project_key="PROJ",
            summary="Test issue"
        )
        
        with pytest.raises(JiraWrapperError) as exc_info:
            wrapper.create_issue(issue_create)
        
        assert "Failed to create issue" in str(exc_info.value)


class TestJiraWrapperGetIssue:
    """Tests for JiraWrapper.get_issue()."""
    
    @pytest.fixture
    def wrapper(self):
        """Create a JiraWrapper instance with mocked JIRA client."""
        with patch('jira_wrapper.client.JIRA') as mock_jira_class:
            mock_jira_instance = Mock()
            mock_jira_class.return_value = mock_jira_instance
            
            config = JiraConfig(
                base_url="https://example.atlassian.net",
                email="user@example.com",
                api_token="token123"
            )
            
            wrapper = JiraWrapper(config)
            wrapper._jira = mock_jira_instance
            return wrapper
    
    def test_get_issue_success(self, wrapper):
        """Test getting issue by key."""
        mock_jira_issue = Mock()
        mock_jira_issue.key = "PROJ-1"
        mock_jira_issue.id = "12345"
        mock_jira_issue.fields.summary = "Test issue"
        mock_jira_issue.fields.description = None
        mock_jira_issue.fields.status.name = "To Do"
        mock_jira_issue.fields.priority = None
        mock_jira_issue.fields.assignee = None
        mock_jira_issue.fields.labels = []
        mock_jira_issue.fields.created = "2024-01-01T00:00:00"
        mock_jira_issue.fields.updated = "2024-01-02T00:00:00"
        mock_jira_issue.permalink.return_value = "https://example.atlassian.net/browse/PROJ-1"
        
        wrapper._jira.issue.return_value = mock_jira_issue
        
        result = wrapper.get_issue("PROJ-1")
        
        assert isinstance(result, IssueResponse)
        assert result.key == "PROJ-1"
        wrapper._jira.issue.assert_called_once_with("PROJ-1")
    
    def test_get_issue_not_found(self, wrapper):
        """Test that 404 errors raise JiraNotFoundError."""
        wrapper._jira.issue.side_effect = JIRAError(status_code=404, text="Not Found")
        
        with pytest.raises(JiraNotFoundError) as exc_info:
            wrapper.get_issue("PROJ-999")
        
        assert "PROJ-999" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()


class TestJiraWrapperBulkCreate:
    """Tests for JiraWrapper.bulk_create_issues()."""
    
    @pytest.fixture
    def wrapper(self):
        """Create a JiraWrapper instance with mocked JIRA client."""
        with patch('jira_wrapper.client.JIRA') as mock_jira_class:
            mock_jira_instance = Mock()
            mock_jira_class.return_value = mock_jira_instance
            
            config = JiraConfig(
                base_url="https://example.atlassian.net",
                email="user@example.com",
                api_token="token123"
            )
            
            wrapper = JiraWrapper(config)
            wrapper._jira = mock_jira_instance
            return wrapper
    
    def test_bulk_create_success(self, wrapper):
        """Test bulk creating multiple issues."""
        # Mock successful issue creation
        def create_issue_side_effect(**kwargs):
            mock_issue = Mock()
            mock_issue.key = f"PROJ-{len(wrapper._jira.create_issue.call_args_list) + 1}"
            mock_issue.id = str(len(wrapper._jira.create_issue.call_args_list) + 1)
            mock_issue.fields.summary = kwargs['fields']['summary']
            mock_issue.fields.description = kwargs['fields'].get('description', None)
            mock_issue.fields.status.name = "To Do"
            mock_issue.fields.priority = None
            mock_issue.fields.assignee = None
            mock_issue.fields.labels = []
            mock_issue.fields.created = "2024-01-01T00:00:00"
            mock_issue.fields.updated = "2024-01-02T00:00:00"
            mock_issue.permalink.return_value = f"https://example.atlassian.net/browse/{mock_issue.key}"
            return mock_issue
        
        wrapper._jira.create_issue.side_effect = create_issue_side_effect
        
        issues = [
            IssueCreate(project_key="PROJ", summary="Issue 1"),
            IssueCreate(project_key="PROJ", summary="Issue 2"),
            IssueCreate(project_key="PROJ", summary="Issue 3"),
        ]
        
        results = wrapper.bulk_create_issues(issues)
        
        assert len(results) == 3
        assert all(isinstance(r, IssueResponse) for r in results)
        assert wrapper._jira.create_issue.call_count == 3
    
    def test_bulk_create_continues_on_error(self, wrapper):
        """Test that bulk create continues even if some issues fail."""
        call_count = 0
        
        def create_issue_side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise JIRAError(status_code=400, text="Bad Request")
            
            mock_issue = Mock()
            mock_issue.key = f"PROJ-{call_count}"
            mock_issue.id = str(call_count)
            mock_issue.fields.summary = kwargs['fields']['summary']
            mock_issue.fields.description = None
            mock_issue.fields.status.name = "To Do"
            mock_issue.fields.priority = None
            mock_issue.fields.assignee = None
            mock_issue.fields.labels = []
            mock_issue.fields.created = "2024-01-01T00:00:00"
            mock_issue.fields.updated = "2024-01-02T00:00:00"
            mock_issue.permalink.return_value = f"https://example.atlassian.net/browse/{mock_issue.key}"
            return mock_issue
        
        wrapper._jira.create_issue.side_effect = create_issue_side_effect
        
        issues = [
            IssueCreate(project_key="PROJ", summary="Issue 1"),
            IssueCreate(project_key="PROJ", summary="Issue 2"),
            IssueCreate(project_key="PROJ", summary="Issue 3"),
        ]
        
        results = wrapper.bulk_create_issues(issues)
        
        # Should have 2 successful results (1 and 3)
        assert len(results) == 2
        assert wrapper._jira.create_issue.call_count == 3

