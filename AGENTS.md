# Repository guidance

- Keep reproduction destructive only to disposable fixtures.
- Every new incident needs symptom, investigation, root cause, correction, prevention, and a regression test.
- Never embed database credentials. Preserve the SQLite no-infrastructure path.
- Report SQL Server-only checks as `NOT VERIFIED` unless actually executed.

