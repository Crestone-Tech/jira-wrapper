# Acceptance Criteria to Jira Issues Preview

**Project:** PROJ

This table shows what Jira issues would be created from the acceptance criteria.

## Hierarchy

- **Epic**: Section (e.g., A) Run Identity and Timing)
- **Story**: Individual Acceptance Criterion (e.g., AC-RUN-001 | Run UUID)

---

## Epic: A) Run Identity and Timing

| Issue Type | Summary | Description Preview |
|------------|---------|---------------------|
| Epic | A) Run Identity and Timing | Section: Run Identity and Timing. Contains 3 acceptance c... |

### Stories (Acceptance Criteria)

| Issue Type | AC ID | Summary | Description Preview |
|-----------|-------|---------|---------------------|
| Story | AC-RUN-001 | AC-RUN-001: Run UUID | - Each execution MUST generate a unique RUN_UUID. |
| Story | AC-RUN-002 | AC-RUN-002: Run Timestamps | - RUN_STARTED_AT MUST be captured at execution start. |
| Story | AC-RUN-003 | AC-RUN-003: Repeatability | - Given identical repo state, commit, config, and tool ve... |

---

## Epic: B) Triggers and Entrypoints

| Issue Type | Summary | Description Preview |
|------------|---------|---------------------|
| Epic | B) Triggers and Entrypoints | Section: Triggers and Entrypoints. Contains 3 acceptance ... |

### Stories (Acceptance Criteria)

| Issue Type | AC ID | Summary | Description Preview |
|-----------|-------|---------|---------------------|
| Story | AC-TRIG-001 | AC-TRIG-001: Git Post-Commit Trigger | - Orchestrator MUST support a post-commit git hook. |
| Story | AC-TRIG-002 | AC-TRIG-002: Manual Scan | - Orchestrator MUST provide a manual CLI scan command. |
| Story | AC-TRIG-003 | AC-TRIG-003: Per-Repo Configuration | - Configuration MUST be supported per repository. |

---

## Epic: C) Target Selection

| Issue Type | Summary | Description Preview |
|------------|---------|---------------------|
| Epic | C) Target Selection | Section: Target Selection. Contains 3 acceptance criteria. |

### Stories (Acceptance Criteria)

| Issue Type | AC ID | Summary | Description Preview |
|-----------|-------|---------|---------------------|
| Story | AC-TARGET-001 | AC-TARGET-001: Latest Default | - If no branch or commit is specified, scan latest commit... |
| Story | AC-TARGET-002 | AC-TARGET-002: Branch Selection | - If branch is specified, scan latest commit on that branch. |
| Story | AC-TARGET-003 | AC-TARGET-003: Commit UUID | - If commit UUID is specified, scan that exact commit. |

---

## Epic: D) Scope Selection (Delta vs Full)

| Issue Type | Summary | Description Preview |
|------------|---------|---------------------|
| Epic | D) Scope Selection (Delta vs Full) | Section: Scope Selection (Delta vs Full). Contains 2 acce... |

### Stories (Acceptance Criteria)

| Issue Type | AC ID | Summary | Description Preview |
|-----------|-------|---------|---------------------|
| Story | AC-SCOPE-001 | AC-SCOPE-001: Delta Default | - Default scan scope MUST be DELTA. |
| Story | AC-SCOPE-002 | AC-SCOPE-002: Full Repo Scan | - When FULL is specified, the entire repository at the ta... |

---

## Summary

- **Total Epics (Sections):** 4
- **Total Stories (ACs):** 11
