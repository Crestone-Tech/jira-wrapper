"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError
from jira_wrapper.models import (
    JiraConfig,
    IssueCreate,
    IssueResponse,
    Priority,
    IssueType,
)

class TestJiraConfig:
    """Tests for JiraConfig model."""
    
    def test_valid_config_creates_successfully(self):
        """Test that valid config creates model successfully."""
        config = JiraConfig(
            base_url="https://example.atlassian.net",
            email="user@example.com",
            api_token="token123"
        )
        assert config.base_url == "https://example.atlassian.net"
        assert config.email == "user@example.com"
        assert config.api_token == "token123"
        assert config.project_key is None
        assert config.timeout_seconds == 30
    
    def test_config_with_optional_fields(self):
        """Test config with optional fields."""
        config = JiraConfig(
            base_url="https://example.atlassian.net",
            email="user@example.com",
            api_token="token123",
            project_key="PROJ",
            timeout_seconds=60
        )
        assert config.project_key == "PROJ"
        assert config.timeout_seconds == 60
    
    def test_missing_required_fields_raises_validation_error(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            JiraConfig(base_url="https://example.atlassian.net")
        
        with pytest.raises(ValidationError):
            JiraConfig(email="user@example.com")
        
        with pytest.raises(ValidationError):
            JiraConfig(api_token="token123")


class TestIssueCreate:
    """Tests for IssueCreate model."""
    
    def test_valid_issue_creates_successfully(self):
        """Test that valid data creates model successfully."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test issue"
        )
        assert issue.project_key == "PROJ"
        assert issue.summary == "Test issue"
        assert issue.description == ""
        assert issue.issue_type == IssueType.TASK
        assert issue.priority is None
    
    def test_issue_with_all_fields(self):
        """Test issue with all fields populated."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test issue",
            description="Test description",
            issue_type=IssueType.BUG,
            priority=Priority.HIGH,
            labels=["label1", "label2"],
            assignee="user@example.com",
            components=["Component1"],
            parent_key="PROJ-1"
        )
        assert issue.issue_type == IssueType.BUG
        assert issue.priority == Priority.HIGH
        assert issue.labels == ["label1", "label2"]
        assert issue.assignee == "user@example.com"
        assert issue.components == ["Component1"]
        assert issue.parent_key == "PROJ-1"
    
    def test_missing_required_fields_raises_validation_error(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            IssueCreate(summary="Test")
        
        with pytest.raises(ValidationError):
            IssueCreate(project_key="PROJ")
    
    def test_empty_project_key_raises_validation_error(self):
        """Test that empty project_key raises ValidationError."""
        with pytest.raises(ValidationError):
            IssueCreate(project_key="", summary="Test")
    
    def test_empty_summary_raises_validation_error(self):
        """Test that empty summary raises ValidationError."""
        with pytest.raises(ValidationError):
            IssueCreate(project_key="PROJ", summary="")
    
    def test_to_jira_dict_basic(self):
        """Test to_jira_dict() with basic fields."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test issue",
            description="Test description"
        )
        result = issue.to_jira_dict()
        
        assert 'fields' in result
        assert result['fields']['project']['key'] == "PROJ"
        assert result['fields']['summary'] == "Test issue"
        assert result['fields']['description'] == "Test description"
        assert result['fields']['issuetype']['name'] == "Task"
    
    def test_to_jira_dict_with_priority(self):
        """Test to_jira_dict() with priority."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test",
            priority=Priority.HIGH
        )
        result = issue.to_jira_dict()
        
        assert result['fields']['priority']['name'] == "High"
    
    def test_to_jira_dict_with_labels(self):
        """Test to_jira_dict() with labels."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test",
            labels=["label1", "label2"]
        )
        result = issue.to_jira_dict()
        
        assert result['fields']['labels'] == ["label1", "label2"]
    
    def test_to_jira_dict_with_assignee(self):
        """Test to_jira_dict() with assignee."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test",
            assignee="user@example.com"
        )
        result = issue.to_jira_dict()
        
        assert result['fields']['assignee']['name'] == "user@example.com"
    
    def test_to_jira_dict_with_components(self):
        """Test to_jira_dict() with components."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test",
            components=["Comp1", "Comp2"]
        )
        result = issue.to_jira_dict()
        
        assert len(result['fields']['components']) == 2
        assert result['fields']['components'][0]['name'] == "Comp1"
        assert result['fields']['components'][1]['name'] == "Comp2"
    
    def test_to_jira_dict_with_parent(self):
        """Test to_jira_dict() with parent key."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test",
            parent_key="PROJ-1"
        )
        result = issue.to_jira_dict()
        
        assert result['fields']['parent']['key'] == "PROJ-1"
    
    def test_to_jira_dict_with_custom_fields(self):
        """Test to_jira_dict() with custom fields."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test",
            custom_fields={"customfield_10001": "value"}
        )
        result = issue.to_jira_dict()
        
        assert result['fields']['customfield_10001'] == "value"
    
    def test_to_jira_dict_with_string_issue_type(self):
        """Test to_jira_dict() with string issue type."""
        issue = IssueCreate(
            project_key="PROJ",
            summary="Test",
            issue_type="Bug"
        )
        result = issue.to_jira_dict()
        
        assert result['fields']['issuetype']['name'] == "Bug"


class TestIssueResponse:
    """Tests for IssueResponse model."""
    
    def test_from_jira_issue_creates_model(self):
        """Test from_jira_issue() creates model from jira Issue object."""
        # Create a mock jira issue object
        class MockFields:
            def __init__(self):
                self.summary = "Test issue"
                self.description = "Test description"
                self.status = MockStatus()
                self.priority = MockPriority()
                self.assignee = MockAssignee()
                self.labels = ["label1", "label2"]
                self.created = "2024-01-01T00:00:00"
                self.updated = "2024-01-02T00:00:00"
        
        class MockStatus:
            name = "To Do"
        
        class MockPriority:
            name = "High"
        
        class MockAssignee:
            emailAddress = "user@example.com"
        
        class MockIssue:
            def __init__(self):
                self.key = "PROJ-1"
                self.id = "12345"
                self.fields = MockFields()
            
            def permalink(self):
                return "https://example.atlassian.net/browse/PROJ-1"
        
        jira_issue = MockIssue()
        response = IssueResponse.from_jira_issue(jira_issue)
        
        assert response.key == "PROJ-1"
        assert response.id == "12345"
        assert response.summary == "Test issue"
        assert response.description == "Test description"
        assert response.status == "To Do"
        assert response.priority == "High"
        assert response.assignee == "user@example.com"
        assert response.labels == ["label1", "label2"]
        assert response.url == "https://example.atlassian.net/browse/PROJ-1"
    
    def test_from_jira_issue_handles_none_values(self):
        """Test from_jira_issue() handles None values gracefully."""
        class MockFields:
            def __init__(self):
                self.summary = "Test issue"
                self.status = MockStatus()
                self.priority = None
                self.assignee = None
                self.labels = []
                self.created = "2024-01-01T00:00:00"
                self.updated = "2024-01-02T00:00:00"
        
        class MockStatus:
            name = "To Do"
        
        class MockIssue:
            def __init__(self):
                self.key = "PROJ-1"
                self.id = "12345"
                self.fields = MockFields()
            
            def permalink(self):
                return "https://example.atlassian.net/browse/PROJ-1"
        
        jira_issue = MockIssue()
        response = IssueResponse.from_jira_issue(jira_issue)
        
        assert response.priority is None
        assert response.assignee is None
        assert response.labels == []
        assert response.description is None

