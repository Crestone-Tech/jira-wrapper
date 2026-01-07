# Feature List

This document tracks all features to be implemented using TDD.

## Feature Status

- 📝 **Planned** - Feature described, not started
- 🧪 **Testing** - Tests written, implementation pending
- 🚧 **Implementing** - Working on implementation
- ✅ **Complete** - Feature implemented and tested
- 🔄 **Refactoring** - Improving implementation

---

## Phase 1: Core Foundation

### F1: IssueCreate Model
**Status**: 📝 Planned  
**Priority**: High  
**Description**: Pydantic model for creating Jira issues with validation

**Acceptance Criteria:**
- Model accepts project_key, summary, description, issue_type, priority, labels
- Validates required fields (project_key, summary)
- Validates issue_type is valid
- Validates priority is valid
- Has `to_jira_dict()` method to convert to jira library format
- Handles optional fields gracefully

**Test Scenarios:**
- ✅ Valid data creates model successfully
- ✅ Missing required fields raises ValidationError
- ✅ Invalid issue_type raises ValidationError
- ✅ Invalid priority raises ValidationError
- ✅ to_jira_dict() returns correct format
- ✅ Optional fields work correctly

---

### F2: IssueResponse Model
**Status**: 📝 Planned  
**Priority**: High  
**Description**: Pydantic model for Jira issue responses

**Acceptance Criteria:**
- Model represents issue data from Jira API
- Has `from_jira_issue()` class method to create from jira library Issue object
- Extracts key, id, summary, description, status, priority, labels, url, timestamps
- Handles None values gracefully

**Test Scenarios:**
- ✅ from_jira_issue() creates model from jira Issue object
- ✅ All fields are extracted correctly
- ✅ None values handled gracefully
- ✅ URL is generated correctly

---

### F3: JiraConfig Model
**Status**: 📝 Planned  
**Priority**: High  
**Description**: Configuration model for Jira connection

**Acceptance Criteria:**
- Model accepts base_url, email, api_token
- Has `from_env()` class method to load from environment variables
- Validates required fields
- Supports optional project_key and timeout_seconds

**Test Scenarios:**
- ✅ Valid config creates model successfully
- ✅ Missing required fields raises ValidationError
- ✅ from_env() loads from environment variables
- ✅ from_env() handles missing variables gracefully

---

### F4: JiraWrapper Client - Initialization
**Status**: 📝 Planned  
**Priority**: High  
**Description**: Main wrapper class that wraps jira.JIRA

**Acceptance Criteria:**
- Can initialize with JiraConfig
- Has `from_env()` class method
- Connects to Jira using jira library
- Handles authentication errors
- Stores jira client instance

**Test Scenarios:**
- ✅ Initializes with valid config
- ✅ from_env() creates instance from environment
- ✅ Authentication errors raise custom exception
- ✅ Connection errors handled gracefully

---

### F5: JiraWrapper - create_issue()
**Status**: 📝 Planned  
**Priority**: High  
**Description**: Create a Jira issue

**Acceptance Criteria:**
- Accepts IssueCreate model
- Calls jira library create_issue()
- Returns IssueResponse
- Handles Jira API errors
- Converts IssueCreate to jira library format

**Test Scenarios:**
- ✅ Creates issue with valid data
- ✅ Returns IssueResponse with correct data
- ✅ Handles Jira API errors gracefully
- ✅ Converts IssueCreate format correctly

---

### F6: Custom Exceptions
**Status**: 📝 Planned  
**Priority**: Medium  
**Description**: Custom exception hierarchy

**Acceptance Criteria:**
- JiraWrapperError base exception
- JiraAuthenticationError for auth failures
- JiraNotFoundError for 404 errors
- JiraValidationError for invalid data
- JiraServerError for server errors

**Test Scenarios:**
- ✅ Exceptions have appropriate messages
- ✅ Exceptions can be caught by base class
- ✅ Exceptions preserve original error context

---

## Phase 2: Additional Features

### F7: get_issue()
**Status**: 📝 Planned  
**Priority**: Medium  
**Description**: Get issue by key

### F8: search_issues()
**Status**: 📝 Planned  
**Priority**: Medium  
**Description**: Search issues using JQL

### F9: bulk_create_issues()
**Status**: 📝 Planned  
**Priority**: Medium  
**Description**: Create multiple issues

### F10: Issue Templates
**Status**: 📝 Planned  
**Priority**: Low  
**Description**: Pre-built issue templates

---

## Notes

- Features are implemented in priority order
- Each feature follows TDD: Tests → Implementation → Refactor
- Tests must pass before moving to next feature

