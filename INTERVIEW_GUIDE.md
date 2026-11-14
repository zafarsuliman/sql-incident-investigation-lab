# Interview guide

**Why this architecture?** A thin service layer keeps incident logic testable while Streamlit provides a low-friction support console.

**How does data move?** The UI selects a catalogue entry, the service executes a bounded reproduction or investigation, and SQLite records the isolated result.

**How are failures handled?** Database contexts roll back exceptions; imports quarantine invalid rows; reset recreates a known-good fixture.

**Security?** No secrets are committed, SQL parameters are used for user data, and SQL Server credentials are environment-only.

**Production changes?** Use Alembic-style migrations, RBAC, immutable audit storage, telemetry, backups, and a non-production SQL Server clone for reproduction.

**Key trade-off?** SQLite improves reviewer accessibility but cannot faithfully reproduce SQL Server locking; that limitation is explicit.

