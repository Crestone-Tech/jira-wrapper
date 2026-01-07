"""Custom exceptions for jira-wrapper."""


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

