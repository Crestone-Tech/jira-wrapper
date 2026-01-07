"""Tests for custom exceptions."""

import pytest
from jira_wrapper.exceptions import (
    JiraWrapperError,
    JiraAuthenticationError,
    JiraNotFoundError,
    JiraValidationError,
    JiraRateLimitError,
    JiraServerError,
)


def test_jira_wrapper_error_is_base_exception():
    """Test that JiraWrapperError is the base exception."""
    error = JiraWrapperError("Test error")
    assert isinstance(error, Exception)
    assert str(error) == "Test error"


def test_jira_authentication_error_inherits_from_base():
    """Test that JiraAuthenticationError inherits from JiraWrapperError."""
    error = JiraAuthenticationError("Auth failed")
    assert isinstance(error, JiraWrapperError)
    assert str(error) == "Auth failed"


def test_jira_not_found_error_inherits_from_base():
    """Test that JiraNotFoundError inherits from JiraWrapperError."""
    error = JiraNotFoundError("Not found")
    assert isinstance(error, JiraWrapperError)
    assert str(error) == "Not found"


def test_jira_validation_error_inherits_from_base():
    """Test that JiraValidationError inherits from JiraWrapperError."""
    error = JiraValidationError("Invalid data")
    assert isinstance(error, JiraWrapperError)
    assert str(error) == "Invalid data"


def test_jira_rate_limit_error_inherits_from_base():
    """Test that JiraRateLimitError inherits from JiraWrapperError."""
    error = JiraRateLimitError("Rate limited")
    assert isinstance(error, JiraWrapperError)
    assert str(error) == "Rate limited"


def test_jira_server_error_inherits_from_base():
    """Test that JiraServerError inherits from JiraWrapperError."""
    error = JiraServerError("Server error")
    assert isinstance(error, JiraWrapperError)
    assert str(error) == "Server error"


def test_exceptions_can_be_caught_by_base_class():
    """Test that specific exceptions can be caught by base class."""
    errors = [
        JiraAuthenticationError("Auth"),
        JiraNotFoundError("Not found"),
        JiraValidationError("Invalid"),
    ]
    
    for error in errors:
        with pytest.raises(JiraWrapperError):
            raise error


def test_exceptions_preserve_context():
    """Test that exceptions can preserve original error context."""
    original = ValueError("Original error")
    wrapper_error = JiraWrapperError("Wrapper error")
    wrapper_error.__cause__ = original
    
    assert wrapper_error.__cause__ == original

