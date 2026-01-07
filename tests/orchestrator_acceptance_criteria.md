# MSG Orchestrator Acceptance Criteria (v1)

## Purpose

The MSG Orchestrator coordinates repository scanning, analyzer invocation, and persistence of results for a single execution ("run").

## A) Run Identity and Timing

### AC-RUN-001 | Run UUID

- Each execution MUST generate a unique RUN_UUID.
- RUN_UUID MUST be included in:
  - logs
  - persisted records
  - output artifacts (including SARIF).

### AC-RUN-002 | Run Timestamps

- RUN_STARTED_AT MUST be captured at execution start.
- RUN_FINISHED_AT MUST be captured at execution end (success, partial success, or failure).

### AC-RUN-003 | Repeatability

- Given identical repo state, commit, config, and tool versions:
- Results MUST be equivalent except for: RUN_UUID, RUN_STARTED_AT, RUN_FINISHED_AT.

## B) Triggers and Entrypoints

### AC-TRIG-001 | Git Post-Commit Trigger

- Orchestrator MUST support a post-commit git hook.
- Default behavior is DELTA scan (commit-only).

### AC-TRIG-002 | Manual Scan

- Orchestrator MUST provide a manual CLI scan command.
- Manual scans MUST behave identically to hook-triggered scans.

### AC-TRIG-003 | Per-Repo Configuration

- Configuration MUST be supported per repository.
- Effective configuration (or config hash) MUST be recorded per run.

## C) Target Selection

### AC-TARGET-001 | Latest Default

- If no branch or commit is specified, scan latest commit on current branch.

### AC-TARGET-002 | Branch Selection

- If branch is specified, scan latest commit on that branch.
- Fail if branch cannot be resolved.

### AC-TARGET-003 | Commit UUID

- If commit UUID is specified, scan that exact commit.
- Fail if commit cannot be resolved.

## D) Scope Selection (Delta vs Full)

### AC-SCOPE-001 | Delta Default

- Default scan scope MUST be DELTA.
- DELTA means files changed by the specified commit only.

### AC-SCOPE-002 | Full Repo Scan

- When FULL is specified, the entire repository at the target commit MUST be scanned.

